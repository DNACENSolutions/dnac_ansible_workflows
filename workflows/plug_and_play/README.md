# Plug and Play Workflow

## Overview

This workflow manages Plug and Play (PnP) devices in **Cisco Catalyst Center** by calling the `cisco.catalystcenter.pnp_workflow_manager` module.

Supported operations:
- Add devices to the PnP inventory
- Bulk import devices
- Automatically authorize devices in `Pending Authorization` state
- Claim routers, switches, switch stacks, wireless controllers, and access points
- Delete devices from the PnP inventory

The workflow playbooks are:
- `workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml`
- `workflows/plug_and_play/playbook/delete_catalyst_center_pnp_playbook.yml`

## Supported Input Buckets

The merged playbook accepts these `pnp_details` buckets:
- `network_devices`
- `claim_router_devices`
- `claim_switching_devices`
- `claim_wireless_controllers`
- `claim_access_points`

Backward-compatible aliases are still accepted and normalized into `network_devices`:
- `add_network_device`
- `add_bulk_network_devices`

These aliases are deprecated. Prefer `network_devices` for all add and bulk-add operations.

The delete playbook accepts:
- `network_devices`
- `claim_router_devices`
- `claim_switching_devices`
- `claim_wireless_controllers`
- `claim_access_points`

For delete operations, `serial_number` is the only required device identifier.

## Key Parameters

### Device Info

Each item under `device_info` supports:

| Parameter | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `serial_number` | string | Yes | Required for merged and delete workflows |
| `pid` | string | Yes for merged | Required by the module for add/claim operations |
| `hostname` | string | No | Applied during claim/update flows |
| `state` | string | No | Common values: `Unclaimed`, `Claimed`, `Provisioned`, `Error` |
| `authorize` | bool | No | Auto-authorize when device enters `Pending Authorization` on Catalyst Center `2.3.7.9+` |
| `is_sudi_required` | bool | No | Enables SUDI authorization handling |
| `user_sudi_serial_nos` | list[string] | Conditionally required | Required when `is_sudi_required: true` |
| `is_stack_device` | bool | No | Marks stack members in switch / stack workflows |

### Claim-Level Parameters

| Parameter | Applies To | Notes |
| :--- | :--- | :--- |
| `site_name` | All claim buckets | Required for claim flows |
| `project_name` | Routers, switches, WLCs | Defaults to `Onboarding Configuration` in the module |
| `template_name` | Routers, switches, WLCs | Optional |
| `template_params` | Routers, switches, WLCs | Optional dict |
| `image_name` | Routers, switches, WLCs | Optional |
| `golden_image` | Routers, switches, WLCs | Tags the selected image as golden |
| `pnp_type` | Claim buckets | Common values: `Default`, `StackSwitch`, `CatalystWLC`, `AccessPoint` |
| `license_level` | Switch / router claim | Primarily relevant to Catalyst switch / stack claims |
| `top_of_stack_serial_number` | Stack switch claim | Used for stack renumbering |
| `cabling_scheme` | Stack switch claim | Allowed values: `1A`, `1B` |
| `rf_profile` | Access point claim | Required for AP claim |
| `static_ip`, `subnet_mask`, `gateway`, `ip_interface_name`, `vlan_id` | WLC claim | Required by the module for `CatalystWLC` claims |

## Example Input File

The shipped sample file is [workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml](/Users/pawansi/dnac_ansible_workflows/workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml). It is valid YAML and includes examples for:
- Add/import with `authorize`
- Access point claim
- Switch claim
- Stack switch claim with renumbering inputs
- WLC claim with `golden_image`
- Router claim with SUDI inputs

### Add or Bulk Import Devices

Use `network_devices` for both single-device and bulk-device imports.

```yaml
---
catalyst_center_version: 2.3.7.9
pnp_details:
  network_devices:
    - device_info:
        - serial_number: FOX2639PAYD
          hostname: SJ-EWLC-1
          state: Unclaimed
          pid: C9800-40-K9
          authorize: true
        - serial_number: FXS2502Q2HC
          hostname: SF-BN-2-ASR.cisco.local
          state: Unclaimed
          pid: ASR1001-X
          authorize: false
```

### Claim a Switch Stack

Use the exact site hierarchy and a Golden image that exists on the controller. When adding and claiming the stack in the same run, include the same serial under `network_devices` with `is_stack_device: true` so Catalyst Center imports it as a stack-capable PnP device before the `StackSwitch` claim.

```yaml
---
catalyst_center_version: 2.3.7.9
pnp_details:
  network_devices:
    - device_info:
        - serial_number: FJC271925Q1
          hostname: NY-EN-9300-1
          state: Unclaimed
          pid: C9300-48UXM
          is_stack_device: true
          authorize: false

  claim_switching_devices:
    - site_name: Global/USA/SAN JOSE/BLD23
      project_name: Onboarding Configuration
      template_name: PnP-Devices-SW
      image_name: cat9k_iosxe.17.17.01prd6.SPA.bin
      template_params:
        PNP_VLAN_ID: 2005
        LOOPBACK_IP: 204.1.2.2
      device_info:
        - serial_number: FJC271925Q1
          hostname: NY-EN-9300-1
          state: Unclaimed
          pid: C9300-48UXM
          is_stack_device: true
      pnp_type: StackSwitch
      license_level: network-advantage
      top_of_stack_serial_number: FJC271925Q1
      cabling_scheme: 1B
```

### Claim a Wireless Controller

```yaml
---
pnp_details:
  claim_wireless_controllers:
    - site_name: Global/USA/SAN JOSE/SJ_BLD23
      project_name: Onboarding Configuration
      image_name: C9800-40-universalk9_wlc.17.12.02.SPA.bin
      golden_image: true
      template_name: PnP-Devices_SJ-EWLC
      template_params:
        MGMT_IP: 10.22.40.244
        MGMT_SUBNET: 255.255.255.0
        NTP_SERVER_IP: 171.68.38.66
      device_info:
        - serial_number: FOX2639PAY7
          hostname: SJ-EWLC-1
          state: Unclaimed
          pid: C9800-40-K9
          authorize: true
      pnp_type: CatalystWLC
      static_ip: 204.192.50.200
      subnet_mask: 255.255.255.0
      gateway: 204.192.50.1
      ip_interface_name: TenGigabitEthernet0/0/2
      vlan_id: 2050
```

### Claim a Router with SUDI Authorization

```yaml
---
pnp_details:
  claim_router_devices:
    - site_name: Global/USA/SAN-FRANCISCO/BLD_SF1
      project_name: Onboarding Configuration
      template_name: PnP-Devices_SF-ISR_No-Vars
      image_name: isr4400-universalk9.17.12.02.SPA.bin
      device_info:
        - serial_number: FXS2502Q2HD
          hostname: SF-BN-2-ASR.cisco.local
          state: Unclaimed
          pid: ASR1001-X
          is_sudi_required: true
          user_sudi_serial_nos:
            - FXS2502Q2HD
```

### Delete Devices

The shipped delete sample is [workflows/plug_and_play/vars/delete_catalyst_center_pnp_vars.yml](/Users/pawansi/dnac_ansible_workflows/workflows/plug_and_play/vars/delete_catalyst_center_pnp_vars.yml).

```yaml
---
pnp_details:
  network_devices:
    - device_info:
        - serial_number: FOX2639PAYD
        - serial_number: FXS2502Q2HC
```

## Validate and Run

### Validate Merged Workflow Inputs

Use `./tools/schemavalidation.sh` with `-s` for schema and `-v` / `--vars` for vars.

```bash
./tools/schemavalidation.sh \
  -s workflows/plug_and_play/schema/plug_and_play_schema.yml \
  -v workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml
```

### Validate Delete Workflow Inputs

```bash
./tools/schemavalidation.sh \
  -s workflows/plug_and_play/schema/delete_plug_and_play_schema.yml \
  -v workflows/plug_and_play/vars/delete_catalyst_center_pnp_vars.yml
```

### Run the Merged Workflow

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/catalyst_center_pnp_vars.yml \
  -vvvv
```

### Run the Delete Workflow

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/plug_and_play/playbook/delete_catalyst_center_pnp_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/delete_catalyst_center_pnp_vars.yml \
  -vvvv
```

## Inventory / group_vars Example

You can run this workflow without `VARS_FILE_PATH` by placing `pnp_details` in inventory variables.

1. Copy the structure from [workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml](/Users/pawansi/dnac_ansible_workflows/workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml) into `inventory/group_vars/all.yml` or `inventory/host_vars/<host>.yml`.
2. Keep the top-level variable name as `pnp_details`.
3. Run the playbook without `VARS_FILE_PATH`:

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml \
  -vvvv
```

## VARS_FILE_PATH Path Resolution

Ansible resolves `VARS_FILE_PATH` relative to the playbook directory, not the current working directory.

Use either of these forms:

- Relative to the playbook: `../vars/catalyst_center_pnp_vars.yml`
- Fully resolved from the repo root: `${PWD}/workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml`

For the delete workflow:

- Relative to the playbook: `../vars/delete_catalyst_center_pnp_vars.yml`
- Fully resolved from the repo root: `${PWD}/workflows/plug_and_play/vars/delete_catalyst_center_pnp_vars.yml`

## References

- Module implementation reviewed for this workflow: [pnp_workflow_manager.py](/Users/pawansi/workspace/ANSIBLE/catalystcenter-ansible-dev/plugins/modules/pnp_workflow_manager.py:11)
