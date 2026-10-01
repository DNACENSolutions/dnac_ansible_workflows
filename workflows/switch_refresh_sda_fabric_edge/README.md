# SDA Fabric Edge Switch Refresh

## Overview

The SDA Fabric Edge Switch Refresh workflow replaces one or more existing SDA
fabric edge access switches with replacement switches while preserving supported
Cisco Catalyst Center intent.

The workflow is intended for hardware-refresh scenarios such as replacing an
existing Catalyst access switch with a newer model. It supports like-to-like and
like-to-unlike replacements and can process multiple switch pairs as one
stage-batched operation.

This IAC workflow wraps the
`cisco.catalystcenter.switch_refresh_sda_fabric_edge` role and provides two
playbooks:

- **Prepare** onboards and configures replacement switches while the old
  switches remain available.
- **Cleanup** removes old switches only after the customer validates the
  replacements and approves destructive cleanup.

The workflow supports replacement switches in SDA fabric sites and SDA fabric
zones. Use the appropriate site or zone hierarchy in the fabric hierarchy input
fields.

> **Important:** The workflow migrates Catalyst Center host-port intent. It does
> not move physical cables. The operator must move endpoint, access point,
> phone, server, and uplink cables during the approved change window.

## Workflow Capabilities

- Onboard replacement switches through Discovery or LAN Automation.
- Add or merge replacements in Catalyst Center inventory and assign inventory
  role `ACCESS`.
- Provision replacements to the selected fabric site or fabric zone.
- Add replacements to the SDA fabric as fabric edge devices.
- Validate fabric membership after fabric onboarding.
- Migrate supported host-port and port-channel intent using explicit interface
  mappings.
- Optionally tag and apply a SWIM golden image to LAN Automation replacement
  switches.
- Optionally capture and resume hostname-transfer data.
- Remove old switches only after replacement validation and Cleanup approval.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Workflow Structure](#workflow-structure)
- [Collection Requirements](#collection-requirements)
- [Catalyst Center Inventory](#catalyst-center-inventory)
- [Mandatory Input Information](#mandatory-input-information)
- [Fabric Site and Fabric Zone Support](#fabric-site-and-fabric-zone-support)
- [Configure the Variables File](#configure-the-variables-file)
- [Discovery Input Example](#discovery-input-example)
- [LAN Automation Input Example](#lan-automation-input-example)
- [Schema Validation](#schema-validation)
- [Executing the Prepare Playbook](#executing-the-prepare-playbook)
- [Prepare Validation](#prepare-validation)
- [Physical Cutover and Traffic Validation](#physical-cutover-and-traffic-validation)
- [Executing the Cleanup Playbook](#executing-the-cleanup-playbook)
- [Final Validation](#final-validation)
- [Hostname Transfer Recovery](#hostname-transfer-recovery)
- [Optional SWIM](#optional-swim)
- [Attention macOS Users](#attention-macos-users)
- [Troubleshooting and Stop Conditions](#troubleshooting-and-stop-conditions)
- [Success Criteria](#success-criteria)

## Prerequisites

Before running the workflow, confirm the following requirements.

### Catalyst Center and Fabric

- Access to a supported Cisco Catalyst Center instance and API connectivity from
  the Ansible runner.
- The configured `catalyst_center_version` or `catalystcenter_version` matches
  the deployed Catalyst Center release supported by the collection.
- The target site exists and is enabled as an SDA fabric site, or the target
  fabric zone already exists under an SDA fabric site.
- Required virtual networks, IP pools, authentication templates, and existing
  host-port intent are present.
- Each old switch is present exactly once, reachable, managed, provisioned to
  the intended site or zone, and an SDA fabric edge device.
- The automation account can use Discovery or LAN Automation, inventory,
  provisioning, fabric-device, SWIM, and host-port APIs as required by the
  selected options.

### Select the Onboarding Method

| Requirement | Discovery | LAN Automation |
| --- | --- | --- |
| Replacement management IP | Already configured and reachable | Assigned or reserved during onboarding |
| Underlay connectivity | Must already work | Built by LAN Automation |
| Physical seed connection | Not required | Required |
| Replacement serial number | Recommended | Required |
| LAN Automation IP pools | Not required | Required |
| PnP-ready device | Not required | Required |

> **Note:** Use Discovery when management routing and SSH already work. Use LAN
> Automation when Catalyst Center must discover the device through a seed port
> and build the underlay.

### Replacement Device Prechecks

```bash
show ip interface brief
show ip route <catalyst_center_address>
ping <catalyst_center_address> source <management_address>
show ip ssh
show run | section line vty
show privilege
show snmp user
show netconf-yang status
show isis neighbors
```

For LAN Automation, also verify the physical seed port, replacement serial
number, PnP state, and available main and physical-link IP pools.

## Workflow Structure

| Path | Purpose |
| --- | --- |
| `workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_prepare.yml` | Runs the non-destructive replacement Prepare phase. |
| `workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_cleanup_old.yml` | Runs destructive old-switch Cleanup after approval. |
| `workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml` | Sample variables file for a two-switch LAN Automation refresh. |
| `workflows/switch_refresh_sda_fabric_edge/schema/switch_refresh_sda_fabric_edge_schema.yml` | Schema used to validate workflow variables. |
| `workflows/switch_refresh_sda_fabric_edge/description.json` | Dashboard metadata for this workflow. |

Generated runtime logs such as `catalystcenter.log` should not be committed.

## Collection Requirements

This workflow requires a `cisco.catalystcenter` collection version that includes
the `switch_refresh_sda_fabric_edge` role. Use `cisco.catalystcenter` 2.13.0 or
later.

Verify the installed collection:

```bash
ansible-galaxy collection list | grep cisco.catalystcenter
ls ~/.ansible/collections/ansible_collections/cisco/catalystcenter/roles | grep switch_refresh
```

Expected role:

```text
switch_refresh_sda_fabric_edge
```

## Catalyst Center Inventory

Cluster connection details should come from inventory, environment variables, or
Ansible Vault. Do not place Catalyst Center host, username, or password in the
workflow vars file.

Example inventory values:

```yaml
---
catalyst_center_hosts:
  hosts:
    catalyst_center220:
      catalyst_center_host: "{{ lookup('ansible.builtin.env', 'HOSTIP') }}"
      catalyst_center_username: "{{ lookup('ansible.builtin.env', 'CATALYST_CENTER_USERNAME') }}"
      catalyst_center_password: "{{ lookup('ansible.builtin.env', 'CATALYST_CENTER_PASSWORD') }}"
      catalyst_center_port: 443
      catalyst_center_timeout: 60
      catalyst_center_verify: false
      catalyst_center_version: "2.3.7.9"
      catalyst_center_debug: false
      catalyst_center_log: true
      catalyst_center_log_level: INFO
```

Export the environment variables before running:

```bash
export HOSTIP="<catalyst-center-host>"
export CATALYST_CENTER_USERNAME="<username>"
export CATALYST_CENTER_PASSWORD="<password>"
```

## Mandatory Input Information

| Required value | Why it is required |
| --- | --- |
| Catalyst Center address, API version, and credentials | Connects the workflow to the correct controller. |
| Exact fabric site or fabric zone hierarchy | Validates old devices and places replacements in the correct fabric scope. |
| One unique identifier for every old switch | Resolves the old source device. Use hostname, management IP, serial, or MAC. |
| Replacement management IPs | Authoritative target set for onboarding, inventory, provisioning, fabric, and migration. |
| Replacement serial numbers | Required for LAN Automation and recommended for verification. |
| Source-to-destination interface mappings | Moves intent to the correct replacement interfaces. |
| CLI credentials | Required for Discovery and replacement inventory management. |
| Seed device, seed ports, and IP pools | Required only for LAN Automation. |
| Known-good endpoint and traffic tests | Proves service after cable movement. |

## Fabric Site and Fabric Zone Support

The workflow supports fabric sites and fabric zones by using the correct
hierarchy in the same hierarchy fields:

- `fabric_site_name_hierarchy`
- `discovered_device_site_name_hierarchy`
- `device_site_name_hierarchy`

Use the fabric site hierarchy when the replacement belongs directly to the
fabric site:

```yaml
fabric_site_name_hierarchy: Global/USA/San Jose/BLDG23
```

Use the fabric zone hierarchy when the replacement belongs to a zone:

```yaml
fabric_site_name_hierarchy: Global/USA/San Jose/BLDG23/FLOOR1
```

For LAN Automation, keep the hierarchy consistent across the batch and discovery
device entries:

```yaml
fabric_site_name_hierarchy: Global/USA/San Jose/BLDG23/FLOOR1

new_devices:
  lan_automation_config:
    - lan_automation:
        discovered_device_site_name_hierarchy: Global/USA/San Jose/BLDG23/FLOOR1
        discovery_devices:
          - device_site_name_hierarchy: Global/USA/San Jose/BLDG23/FLOOR1
```

The fabric site or zone must already exist in Catalyst Center before running
this workflow.

## Configure the Variables File

Start from:

```text
workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml
```

Keep Catalyst Center credentials in inventory, environment variables, or Ansible
Vault. Keep only workflow input in the vars file.

Top-level controls:

```yaml
switch_refresh_sda_fabric_edge_work_dir: /tmp/catalystcenter_switch_refresh_sda_fabric_edge
switch_refresh_sda_fabric_edge_onboarding_method: lan_automation

switch_refresh_sda_fabric_edge_device_info_lookup_enabled: true
switch_refresh_sda_fabric_edge_fabric_validation_enabled: true

switch_refresh_sda_fabric_edge_inventory_config_verify: true
switch_refresh_sda_fabric_edge_provision_config_verify: true
switch_refresh_sda_fabric_edge_sda_fabric_devices_config_verify: true
switch_refresh_sda_fabric_edge_sda_host_port_onboarding_config_verify: true
```

Inventory credentials for replacement switches:

```yaml
switch_refresh_sda_fabric_edge_inventory_credentials:
  username: "{{ vault_switch_cli_username }}"
  password: "{{ vault_switch_cli_password }}"
  enable_password: "{{ vault_switch_enable_password }}"
  cli_transport: ssh
  type: NETWORK_DEVICE
```

## Discovery Input Example

Use Discovery when replacement switches already have management reachability and
SSH access.

```yaml
---
switch_refresh_sda_fabric_edge_work_dir: /tmp/catalystcenter_switch_refresh_sda_fabric_edge
switch_refresh_sda_fabric_edge_onboarding_method: discovery

switch_refresh_sda_fabric_edge_hostname_transfer_enabled: false
switch_refresh_sda_fabric_edge_device_info_lookup_enabled: true
switch_refresh_sda_fabric_edge_fabric_validation_enabled: true

switch_refresh_sda_fabric_edge_inventory_credentials:
  username: "{{ vault_switch_cli_username }}"
  password: "{{ vault_switch_cli_password }}"
  enable_password: "{{ vault_switch_enable_password }}"
  cli_transport: ssh
  type: NETWORK_DEVICE

switch_refresh_sda_fabric_edge_batches:
  - name: discovery-onboard-new-devices
    fabric_site_name_hierarchy: "<fabric_site_or_zone_hierarchy>"
    onboarding_method: discovery

    new_devices:
      device_ips:
        - "<replacement_1_management_ip>"
        - "<replacement_2_management_ip>"
      discovery_config:
        - discovery_name: "<discovery_name>"
          discovery_type: MULTI RANGE
          ip_address_list:
            - "<replacement_1_management_ip>"
            - "<replacement_2_management_ip>"
          protocol_order: ssh
          retry: 2
          use_global_credentials: true

    device_mapping:
      - old:
          hostname: "<old_switch_1_fqdn>"
        new:
          management_ip: "<replacement_1_management_ip>"
        interface_migration:
          only_mapped: true
          port_assignments:
            - source: GigabitEthernet1/0/5
              destination: GigabitEthernet1/0/4
          port_channels: []

      - old:
          hostname: "<old_switch_2_fqdn>"
        new:
          management_ip: "<replacement_2_management_ip>"
        interface_migration:
          only_mapped: true
          port_assignments:
            - source: GigabitEthernet2/0/6
              destination: GigabitEthernet2/0/5
          port_channels: []
```

## LAN Automation Input Example

Use LAN Automation when Catalyst Center should discover the replacement switch
through a seed device and build the underlay.

```yaml
---
switch_refresh_sda_fabric_edge_work_dir: /tmp/catalystcenter_switch_refresh_sda_fabric_edge
switch_refresh_sda_fabric_edge_onboarding_method: lan_automation

switch_refresh_sda_fabric_edge_hostname_transfer_enabled: true
switch_refresh_sda_fabric_edge_hostname_transfer_resume_from_manifest: false
switch_refresh_sda_fabric_edge_hostname_transfer_manifest_dir: >-
  /tmp/catalystcenter_switch_refresh_sda_fabric_edge/hostname_transfer

switch_refresh_sda_fabric_edge_device_info_lookup_enabled: true
switch_refresh_sda_fabric_edge_fabric_validation_enabled: true

switch_refresh_sda_fabric_edge_lan_automation_completion_timeout: 604800
switch_refresh_sda_fabric_edge_lan_automation_completion_poll_interval: 30

switch_refresh_sda_fabric_edge_inventory_credentials:
  username: "{{ vault_switch_cli_username }}"
  password: "{{ vault_switch_cli_password }}"
  enable_password: "{{ vault_switch_enable_password }}"
  cli_transport: ssh
  type: NETWORK_DEVICE

switch_refresh_sda_fabric_edge_batches:
  - name: switch-refresh-two-device
    fabric_site_name_hierarchy: "<fabric_site_or_zone_hierarchy>"
    onboarding_method: lan_automation

    new_devices:
      device_ips:
        - "<replacement_1_management_ip>"
        - "<replacement_2_management_ip>"

      lan_automation_config:
        - lan_automation:
            discovered_device_site_name_hierarchy: "<fabric_site_or_zone_hierarchy>"
            primary_device_management_ip_address: "<seed_management_ip>"
            primary_device_interface_names:
              - "<seed_interface_to_replacement_1>"
              - "<seed_interface_to_replacement_2>"
            ip_pools:
              - ip_pool_name: "<lan_automation_main_pool>"
                ip_pool_role: MAIN_POOL
              - ip_pool_name: "<lan_automation_physical_link_pool>"
                ip_pool_role: PHYSICAL_LINK_POOL
            multicast_enabled: true
            redistribute_isis_to_bgp: false
            discovery_level: 5
            discovery_timeout: 40
            discovery_devices:
              - device_serial_number: "<replacement_1_serial>"
                device_host_name: "<replacement_1_temporary_hostname>"
                device_site_name_hierarchy: "<fabric_site_or_zone_hierarchy>"
                device_management_ip_address: "<replacement_1_management_ip>"
              - device_serial_number: "<replacement_2_serial>"
                device_host_name: "<replacement_2_temporary_hostname>"
                device_site_name_hierarchy: "<fabric_site_or_zone_hierarchy>"
                device_management_ip_address: "<replacement_2_management_ip>"
            launch_and_wait: true
            pnp_authorization: true

    device_mapping:
      - old:
          hostname: "<old_switch_1_fqdn>"
        new:
          management_ip: "<replacement_1_management_ip>"
        interface_migration:
          only_mapped: true
          port_assignments:
            - source: GigabitEthernet1/0/5
              destination: GigabitEthernet1/0/4
          port_channels: []

      - old:
          hostname: "<old_switch_2_fqdn>"
        new:
          management_ip: "<replacement_2_management_ip>"
        interface_migration:
          only_mapped: true
          port_assignments:
            - source: GigabitEthernet2/0/6
              destination: GigabitEthernet2/0/5
          port_channels: []
```

> **Note:** The replacement IP set under `new_devices.device_ips` must match
> every onboarding and `device_mapping` target. For identical interface names,
> use empty mapping lists. For unlike platforms, map every changed interface
> explicitly.

## Device Mapping

Each `device_mapping` entry connects one old switch to one replacement switch.

Supported old-device identifiers:

- `hostname`
- `management_ip`
- `serial_number`
- `mac_address`

Replacement devices use:

```yaml
new:
  management_ip: "<replacement-management-ip>"
```

Host-port migration uses:

```yaml
interface_migration:
  only_mapped: true
  port_assignments:
    - source: GigabitEthernet1/0/5
      destination: GigabitEthernet1/0/4
  port_channels: []
```

When `only_mapped` is true, only the listed source interfaces are migrated.

## Schema Validation

Validate the vars file before a live run:

```bash
yamale -s workflows/switch_refresh_sda_fabric_edge/schema/switch_refresh_sda_fabric_edge_schema.yml \
  workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml
```

Also confirm YAML and playbook syntax:

```bash
python -c "import yaml; yaml.safe_load(open('workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml')); print('YAML valid')"
ansible-playbook --syntax-check workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_prepare.yml
ansible-playbook --syntax-check workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_cleanup_old.yml
```

Correct every YAML, schema, and syntax error before a live run.

## Executing the Prepare Playbook

Run prepare from the repository root:

```bash
ansible-playbook \
  -i inventory/demo_lab/hosts.yaml \
  workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_prepare.yml \
  --extra-vars "VARS_FILE_PATH=$PWD/workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml" \
  -e ansible_python_interpreter="$(which python)" \
  -vvvv
```

Prepare can perform these stages depending on the vars:

- onboard replacement switches by Discovery or LAN Automation
- wait for LAN Automation completion
- wait for inventory readiness
- update inventory role when needed
- provision replacement devices
- add replacement devices to the SDA fabric
- validate fabric membership
- migrate host-port assignments and port-channel mappings
- optionally tag and apply a SWIM golden image
- optionally capture hostname transfer data

Prepare must finish with `failed=0` and `unreachable=0`. Then validate actual
Catalyst Center state before moving cables.

## Prepare Validation

- Exactly one inventory record exists for every replacement IP.
- Every replacement is reachable or ping reachable, managed, and inventory role
  `ACCESS`.
- Every replacement is provisioned to the intended site or zone.
- Every replacement is an SDA fabric edge device in the expected fabric.
- Host-port and port-channel intent exists only on the mapped replacement
  interfaces.
- For LAN Automation, PnP completed, no LAN Automation session remains active,
  and underlay neighbors and routes are healthy.

## Physical Cutover and Traffic Validation

- Keep the old switch powered and available.
- Move one cable or approved cable group at a time to the exact mapped
  replacement interface.
- Wait for link, authentication, IP learning, and policy programming.
- Verify the expected MAC and IP binding on the replacement port.
- Test the default gateway, required VN paths, shared services, and an
  application.
- Move affected cables back to the old switch immediately when validation fails.

> **Note:** Expected downtime: A single-homed endpoint normally experiences an
> interruption while its cable is moved and the replacement port converges. The
> workflow does not create endpoint redundancy.

## Executing the Cleanup Playbook

Cleanup is destructive. Run it only after every intended cable has moved, all
validation passes, fabric health is acceptable, and explicit Cleanup approval is
recorded.

Run cleanup from the repository root:

```bash
ansible-playbook \
  -i inventory/demo_lab/hosts.yaml \
  workflows/switch_refresh_sda_fabric_edge/playbook/switch_refresh_sda_fabric_edge_cleanup_old.yml \
  --extra-vars "VARS_FILE_PATH=$PWD/workflows/switch_refresh_sda_fabric_edge/vars/switch_refresh_sda_fabric_edge_usecase.yml" \
  -e ansible_python_interpreter="$(which python)" \
  -vvvv
```

Cleanup can remove old host-port configuration, fabric membership,
provisioning, and inventory records.

## Final Validation

| Replacement switches | Old switches |
| --- | --- |
| Present exactly once, reachable, managed, and role `ACCESS`. | Host-port intent removed. |
| Provisioned to the intended site or zone and fabric edge role. | Removed from the SDA fabric. |
| Mapped host-port and port-channel intent remains present. | Unprovisioned and absent from inventory. |
| Endpoints are learned and required traffic tests pass. | Old IP, UUID, and serial identities are absent. |

## Hostname Transfer Recovery

The prepare workflow can capture hostname-transfer state in a manifest when
hostname transfer is enabled:

```yaml
switch_refresh_sda_fabric_edge_hostname_transfer_enabled: true
switch_refresh_sda_fabric_edge_hostname_transfer_manifest_dir: >-
  /tmp/catalystcenter_switch_refresh_sda_fabric_edge/hostname_transfer
```

If cleanup must resume from the manifest instead of running destructive cleanup,
set:

```yaml
switch_refresh_sda_fabric_edge_hostname_transfer_resume_from_manifest: true
```

When this is true, the cleanup playbook runs in hostname-transfer recovery mode
instead of destructive cleanup mode.

## Optional SWIM

To enable SWIM for LAN Automation replacement switches, enable:

```yaml
switch_refresh_sda_fabric_edge_swim_enabled: true
switch_refresh_sda_fabric_edge_swim_config_verify: true
```

Then provide a golden image per batch:

```yaml
new_devices:
  golden_image:
    image_name: cisco9k_iosxe.26.01.01a.SPA.bin
    device_image_family_name: Cisco C9350 Smart Switch
```

## Attention macOS Users

If Ansible workers terminate with an Objective-C `initializeAfterForkError` or
`A worker was found in a dead state`, set this environment variable in the shell
used to run the playbook:

```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## Troubleshooting and Stop Conditions

| Condition | Required action |
| --- | --- |
| Input or syntax validation fails | Correct the input before any live run. |
| Old switch does not resolve exactly once | Correct the identifier and use only one identifier. |
| Replacement is unreachable or not managed | Restore reachability and collection. Do not bypass validation. |
| LAN Automation remains active | Resolve or stop the session before inventory or provisioning. |
| Replacement is not in the intended fabric site or zone | Correct the hierarchy values and rerun Prepare before cutover. |
| Generated host-port intent is empty or incorrect | Correct old intent or mappings and rerun Prepare before cutover. |
| Endpoint authentication, addressing, policy, or traffic fails | Move affected cables back and troubleshoot. |
| Cleanup approval is missing | Keep the old switch in fabric and inventory. |

## Success Criteria

- Every replacement is reachable, managed, `ACCESS`, provisioned to the intended
  site or zone, and an SDA fabric edge device.
- Required host-port and port-channel intent exists only on mapped replacement
  interfaces.
- Connected endpoints authenticate and pass approved traffic and application
  tests.
- Every old switch is absent from the fabric and inventory after approved
  Cleanup.
- Validation evidence and generated payloads are retained with the change
  record.
