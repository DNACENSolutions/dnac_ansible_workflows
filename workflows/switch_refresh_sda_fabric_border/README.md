# SDA Fabric Border Switch Refresh

## Overview

The SDA Fabric Border Switch Refresh workflow replaces supported SDA fabric devices while preserving their source inventory role, supported fabric roles, border capabilities, and captured handoff configuration.

This workflow wraps the `cisco.catalystcenter.switch_refresh_sda_fabric_border` role and provides two phases:

| Phase | Purpose |
| --- | --- |
| **Prepare** | Discover and configure replacements without deleting old devices or transferring handoffs. |
| **Cutover** | Save recovery manifests, remove old devices, transfer captured handoffs, verify configuration, and optionally transfer hostnames. |

> **Important:** Cutover uses a break-before-make sequence. Handoffs are applied to the replacement after the old device is removed. Schedule a maintenance window for the affected services.

The workflow does not move physical cables, transfer management IP addresses, or copy the complete switch running configuration.

## Workflow Capabilities

- Onboard replacement switches through Discovery.
- Capture supported source configuration using the fabric-device configuration generator.
- Preserve the source inventory role and supported fabric roles.
- Preserve Layer 2 and Layer 3 border capabilities.
- Transfer captured Layer 2 and IP-transit handoffs using explicit interface mappings.
- Preserve captured IP-transit local and peer addresses.
- Verify replacement configuration through generated readback.
- Save protected recovery manifests before destructive actions.
- Resume interrupted cutovers using validated manifests.
- Optionally transfer the source hostname after handoff verification.

## Prerequisites

Before execution, confirm:

- The runner's Catalyst Center connection and credentials are configured.
- The installed collection contains the tested border-refresh role and dependencies.
- The target fabric site exists.
- Old and replacement devices belong to the same Catalyst Center.
- Required virtual networks, transit networks, pools, and source handoff intent exist.
- The automation account has the required permissions.
- Replacement management addressing, routing, SSH, and inventory credentials are ready.
- Source identities, replacement identities, interface mappings, and cabling are reviewed.
- Work and manifest directories are writable by the runner.
- A maintenance window and recovery procedure are available.

Supported source fabric role sets are:

- `BORDER_NODE`
- `CONTROL_PLANE_NODE`
- `BORDER_NODE` and `CONTROL_PLANE_NODE`
- `BORDER_NODE`, `CONTROL_PLANE_NODE`, and `EDGE_NODE`

The replacement inherits the captured role set. Other combinations are rejected.

### Device Prechecks

```text
show inventory
show version
show ip interface brief
show ip route <controller_address>
ping <controller_address> source <replacement_management_address>
show ip ssh
show snmp user
show snmp group
show isis neighbors
show cdp neighbors
```

Verify underlay addressing, matching MTU, routing adjacencies, and controller reachability. Physical link-up or CDP visibility alone does not establish routing readiness.

Maintain console or out-of-band access and record configuration and traffic baselines.

The role does not require another operational border outside the replacement pair. Review redundancy and outage impact independently.

## Workflow Structure

Paths below are relative to the IaC repository root.

| Path | Purpose |
| --- | --- |
| `workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_prepare.yml` | Prepare replacements. |
| `workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_cutover.yml` | Execute Cutover or manifest continuation. |
| `workflows/switch_refresh_sda_fabric_border/vars/switch_refresh_sda_fabric_border_input.yml` | Workflow input. |
| `workflows/switch_refresh_sda_fabric_border/schema/switch_refresh_sda_fabric_border_schema.yml` | Input schema. |
| `workflows/switch_refresh_sda_fabric_border/tests/` | Offline wrapper tests. |

Do not commit populated credentials, runtime logs, or recovery manifests.

## Collection Requirements

The playbooks call the installed `cisco.catalystcenter` collection. An adjacent development checkout is not automatically used.

Verify the installed collection:

```bash
ansible-galaxy collection list cisco.catalystcenter
```

For development builds, retain the source commit and collection archive filename with the test evidence. The collection version alone may not identify the development revision.

## Mandatory Input Information

| Input | Requirement |
| --- | --- |
| Batch name | Unique within the run. |
| Fabric hierarchy | Exact existing fabric-site hierarchy. |
| Old-device selector | Exactly one management IP, hostname, serial number, or MAC address. |
| Replacement IP | One unique management IP per replacement. |
| Discovery configuration | Covers the replacement IP set. |
| Switch credentials | Required for Discovery and inventory operations. |
| Handoff mappings | Exactly one mapping per captured L2/IP-transit source interface. |
| Work directory | Absolute, non-root path writable by the runner. |
| Manifest directory | Durable absolute, non-root path required for Cutover. |

Source inventory and fabric roles are captured automatically. They are not independently selected in the replacement input.

## Configure the Variables File

Start from:

```text
workflows/switch_refresh_sda_fabric_border/vars/switch_refresh_sda_fabric_border_input.yml
```

Replace example identities, IP addresses, site hierarchy, and interface names before execution.

```yaml
---
switch_refresh_sda_fabric_border_work_dir: /var/lib/catalystcenter-runner/border-refresh/work
switch_refresh_sda_fabric_border_manifest_dir: /var/lib/catalystcenter-runner/border-refresh/manifests

switch_refresh_sda_fabric_border_cutover_approved: false
switch_refresh_sda_fabric_border_resume_from_manifest: false
switch_refresh_sda_fabric_border_hostname_transfer_enabled: false

switch_refresh_sda_fabric_border_inventory_readiness_timeout: 1800

switch_refresh_sda_fabric_border_inventory_credentials:
  username: "{{ vault_switch_cli_username }}"
  password: "{{ vault_switch_cli_password }}"
  enable_password: "{{ vault_switch_enable_password }}"
  cli_transport: ssh
  type: NETWORK_DEVICE

switch_refresh_sda_fabric_border_batches:
  - name: border-refresh-example
    fabric_site_name_hierarchy: Global/USA/San Jose/BLDG23
    onboarding_method: discovery

    new_devices:
      device_ips:
        - "192.0.2.20"

      discovery_config:
        - discovery_name: border-refresh-example
          discovery_type: SINGLE
          ip_address_list:
            - "192.0.2.20"
          protocol_order: ssh
          retry: 2
          use_global_credentials: true

    device_mapping:
      - old:
          serial_number: OLD-BORDER-01
        new:
          management_ip: "192.0.2.20"

        handoff_interface_mappings:
          - source_interface_name: GigabitEthernet1/0/10
            destination_interface_name: GigabitEthernet2/0/10
          - source_interface_name: GigabitEthernet1/0/11
            destination_interface_name: GigabitEthernet2/0/11
```

This example assumes suitable global Discovery credentials exist in Catalyst Center. The referenced `vault_*` variables must be supplied through Ansible Vault or another approved secret source.

Every IP under `new_devices.device_ips` must have exactly one device mapping. Discovery configuration must cover the same replacement set.

## Layer 2 and Layer 3 Handoff Mapping

Map every distinct source interface used by captured Layer 2 or IP-transit handoffs.

```yaml
handoff_interface_mappings:
  - source_interface_name: GigabitEthernet1/0/10
    destination_interface_name: GigabitEthernet2/0/10
  - source_interface_name: GigabitEthernet1/0/11
    destination_interface_name: GigabitEthernet2/0/11
```

Mapping requirements:

- Use interfaces from the captured source configuration.
- Map each distinct source interface once, even when multiple virtual networks share it.
- Include explicit mappings when interface names remain unchanged.
- Do not include interfaces without captured handoffs.
- Destination interfaces must exist and pass validation.
- SDA-transit handoffs do not require interface mappings.

Disconnected interfaces can support configuration-only testing but cannot demonstrate service restoration.

### Pool-Backed IP-Transit Handoffs

The updated role preserves captured local and peer addresses.

During Cutover, it omits the pool selector from the outgoing creation payload so the fabric manager uses explicit captured addresses instead of requesting a new allocation.

The protected capture retains the original pool information. Retention of the same pool association in replacement readback is not guaranteed and requires validation in the target environment.

Do not bypass address, capability, or manifest validation.

## Schema and Offline Validation

Run from the IaC repository root.

Validate the input:

```bash
yamale \
  -s workflows/switch_refresh_sda_fabric_border/schema/switch_refresh_sda_fabric_border_schema.yml \
  workflows/switch_refresh_sda_fabric_border/vars/switch_refresh_sda_fabric_border_input.yml
```

Set `INVENTORY_PATH` to your existing inventory file containing the `catalyst_center_hosts` group and controller connection variables. No inventory file is bundled with this workflow.

```bash
export INVENTORY_PATH="/absolute/path/to/your/hosts.yaml"
```

Check playbook syntax:

```bash
ansible-playbook \
  -i "$INVENTORY_PATH" \
  workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_prepare.yml \
  --syntax-check

ansible-playbook \
  -i "$INVENTORY_PATH" \
  workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_cutover.yml \
  --syntax-check
```

Run offline wrapper tests:

```bash
python -m unittest discover \
  -s workflows/switch_refresh_sda_fabric_border/tests \
  -p 'test_*.py'
```

Offline wrapper tests use a stub role and do not contact Catalyst Center. Passing schema, syntax, and offline tests does not establish live device readiness.

## Executing Prepare

Keep approval and manifest resume disabled:

```yaml
switch_refresh_sda_fabric_border_cutover_approved: false
switch_refresh_sda_fabric_border_resume_from_manifest: false
```

Run:

```bash
ansible-playbook \
  -i "$INVENTORY_PATH" \
  workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_prepare.yml \
  -e "VARS_FILE_PATH=$PWD/workflows/switch_refresh_sda_fabric_border/vars/switch_refresh_sda_fabric_border_input.yml" \
  -e "ansible_python_interpreter=$(command -v python)" \
  -e @vault.yml --ask-vault-pass
```

Use your configured inventory path. The example assumes `vault.yml` supplies the referenced secrets; omit those arguments only when another approved source supplies them.

Prepare performs the following:

1. Resolves source identity and captures supported configuration.
2. Validates exact handoff mapping coverage.
3. Discovers and onboards replacements.
4. Waits for completed inventory collection and management readiness.
5. Assigns and confirms inherited inventory roles.
6. Provisions replacements.
7. Adds inherited fabric roles and required border capabilities.
8. Verifies the handoff-free replacement configuration.

Prepare does not delete old devices or transfer their handoffs.

## Prepare Validation

Require `failed=0` and `unreachable=0`, then verify:

- Exactly one inventory record exists for each replacement.
- UUID, serial, platform, and software identity are correct.
- Collection and management states are Managed.
- Reachability, device support, and provisioning checks pass.
- Fabric roles match the source.
- Mixed L2/L3 borders report both required capabilities.
- Source handoffs remain on the old device.
- Replacement base configuration contains no transferred handoffs.
- Underlay routing and controller connectivity are healthy.

Missing handoff SVIs or peer configuration on the replacement can be expected during Prepare.

**Prepare success does not prove handoff traffic migration.**

## Executing Cutover

Cutover is destructive. Proceed only after Prepare succeeds, the captured configuration is reviewed, and the maintenance window and recovery procedure are approved.

Set:

```yaml
switch_refresh_sda_fabric_border_cutover_approved: true
switch_refresh_sda_fabric_border_resume_from_manifest: false
```

Run:

```bash
ansible-playbook \
  -i "$INVENTORY_PATH" \
  workflows/switch_refresh_sda_fabric_border/playbook/switch_refresh_sda_fabric_border_cutover.yml \
  -e "VARS_FILE_PATH=$PWD/workflows/switch_refresh_sda_fabric_border/vars/switch_refresh_sda_fabric_border_input.yml" \
  -e "ansible_python_interpreter=$(command -v python)" \
  -e @vault.yml --ask-vault-pass
```

Normal Cutover:

1. Recaptures source configuration and saves all batch manifests before deletion.
2. Validates replacement identity, configuration, and border capabilities.
3. Processes old/new pairs serially.
4. Removes each source from fabric, provisioning, and inventory.
5. Confirms source absence.
6. Applies captured handoffs to mapped replacement interfaces.
7. Verifies generated replacement configuration.
8. Optionally transfers the source hostname.
9. Records completion.

The workflow has no automatic rollback.

Use YAML booleans. Passing `-e key=true` creates a string and may fail strict validation.

## Physical Cutover and Final Validation

Coordinate cable movement with the approved cutover sequence. The workflow does not move cables or configure external peer devices.

Useful commands:

```text
show cdp neighbors
show isis neighbors
show interfaces trunk
show vlan brief
show ip interface brief
show running-config | section ^router bgp
show ip bgp summary
show ip bgp vpnv4 vrf <vn_name> summary
show ip route vrf <vn_name>
```

Confirm:

- L2 interfaces and internal/external VLAN mappings match the capture.
- L3 SVIs, VRFs, addresses, and peer configuration match expectations.
- Connected trunks carry required VLANs.
- External peers and return routing are correct.
- Required routing sessions and traffic tests pass.
- Old devices are absent from fabric and inventory.
- Manifest state is complete.
- Optional hostname transfer is verified.

Configuration-only testing with disconnected ports or Idle BGP peers does not prove service restoration.

## Manifest Storage and Recovery

Manifests are stored on the **Ansible control node**, not on the switch.

Each batch uses a filename such as:

```text
<batch_name>_border_cutover.yml
```

Normal Cutover saves the manifest before source deletion. Prepare alone does not establish that a cutover manifest exists.

Manifest progress includes:

```text
captured -> deletion_started -> old_deleted -> handoff_verified -> complete
```

Treat manifests as sensitive recovery artifacts. Do not edit protected payloads or fingerprints, commit manifests, or delete them to bypass validation.

| Execution Mode | Approval | Resume |
| --- | --- | --- |
| Prepare | `false` | `false` |
| Normal Cutover | `true` | `false` |
| Approved destructive continuation | `true` | `true` |
| Non-destructive manifest continuation | `false` | `true` |

Non-destructive continuation requires the source to be fully absent. The role verifies this condition.

For an interrupted cutover, preserve the original manifest directory and review live controller/device state before selecting a recovery mode.

For a fresh test, restore and validate the starting state before using a new manifest directory or explicitly archiving the completed record.

## Optional Hostname Transfer

Enable before the planned workflow:

```yaml
switch_refresh_sda_fabric_border_hostname_transfer_enabled: true
```

Hostname transfer occurs after handoff verification during Cutover, not during Prepare.

When disabled, retaining the replacement hostname is expected. Hostname transfer does not transfer the old management IP.

## Runner Considerations

Use the execution environment containing the tested collection and SDK dependencies.

For macOS fork-related worker failures:

```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

Ensure work and manifest paths are writable by the runner account and appropriate for the runner operating system.

Cutover locking is local to one control node. Coordinate jobs across runner hosts. Remove stale locks only after confirming that no cutover for that controller is active.

## Troubleshooting and Stop Conditions

| Condition | Required Action |
| --- | --- |
| Controller credentials are empty | Check the runner connection and variable precedence. |
| TLS verification fails | Configure trust for the controller certificate chain. |
| Installed role lacks expected fixes | Verify the collection installed in the execution environment. |
| Handoff mapping validation fails | Compare mappings with current captured source interfaces. |
| Replacement is not Managed or supported | Resolve inventory collection, credentials, platform, or software issues. |
| Required border capability is missing | Resolve controller acceptance and rerun Prepare. |
| Existing manifest blocks normal Cutover | Inspect its state and select reviewed recovery or fresh-test procedures. |
| Handoff verification fails | Preserve evidence and stop; do not bypass comparison. |
| Traffic validation fails | Follow the approved recovery procedure. |

## Success Criteria

- Replacement identity, inventory role, provisioning, and fabric roles are correct.
- Required border capabilities are present.
- Captured handoffs exist on the mapped interfaces.
- Generated configuration verification passes.
- Required service tests pass after physical connectivity is established.
- Old devices are absent from fabric and inventory.
- Manifest state is complete.
- Optional hostname transfer is confirmed.
- Recovery artifacts and validation evidence are retained securely.
