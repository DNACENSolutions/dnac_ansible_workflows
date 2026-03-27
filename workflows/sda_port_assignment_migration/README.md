# SDA Port Assignment Migration

This workflow migrates SDA host port assignments from a source device IP to a destination device IP.

It uses:
- `cisco.dnac.sda_host_port_onboarding_playbook_config_generator` to export source port assignments.
- `cisco.dnac.sda_host_port_onboarding_workflow_manager` to apply those assignments to destination devices.

## Workflow Representation

The following diagram represents the end-to-end functionality performed by this workflow:

![SDA Port Assignment Migration Workflow](./images/port_assignment_migration_workflow.png)

## Input Data Model

### Definition

| Field | Type | Required | Description |
|---|---|---|---|
| `port_assignment_migration` | `list[object]` | Yes | One or more migration entries. |
| `port_assignment_migration[].fabric_site` | `string` | Yes | Fabric site hierarchy (for example: `Global/California/23`). |
| `port_assignment_migration[].source_device_ip` | `string` | Yes | Source device management IP to export assignments from. |
| `port_assignment_migration[].destination_device_ip` | `string` | Yes | Destination device management IP to apply assignments to. |
| `port_assignment_migration[].interface_mappings` | `list[object]` | No | Optional source-to-destination interface remap list. If omitted, migration is 1:1 by interface name. |
| `port_assignment_migration[].interface_mappings[].source_interface_name` | `string` | Yes (when `interface_mappings` used) | Interface name from the source device payload. |
| `port_assignment_migration[].interface_mappings[].destination_interface_name` | `string` | Yes (when `interface_mappings` used) | Interface name to use on destination device payload. |

### Example 1: 1:1 Interface Migration (Default)

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.0.0.1"
    destination_device_ip: "10.0.0.2"
```

### Example 2: Partial Interface Remap

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.0.0.1"
    destination_device_ip: "10.0.0.2"
    interface_mappings:
      - source_interface_name: "GigabitEthernet1/0/1"
        destination_interface_name: "GigabitEthernet1/0/25"
      - source_interface_name: "GigabitEthernet1/0/2"
        destination_interface_name: "GigabitEthernet1/0/26"
```

Behavior for Example 2:
- Interfaces listed in `interface_mappings` are remapped.
- Interfaces not listed in `interface_mappings` keep the same interface name (1:1).

## Files

- `playbook/sda_port_assignment_migration_playbook.yml`
- `playbook/tasks/migrate_single_port_assignment.yml`
- `schema/sda_port_assignment_migration_schema.yml`
- `vars/sda_port_assignment_migration_input.yml`
- `slides/sda_port_assignment_migration_usecase_slide.md`

## Step 1: Virtual Env Setup

Run the following from repository root:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip tooling
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies (includes ansible and dnacentersdk)
pip install -r requirements.txt

# Install/upgrade Cisco DNAC Ansible collection
ansible-galaxy collection install cisco.dnac --force
```

## Step 2: Create Inputs

Update the workflow input file:
- `workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml`

Minimum example:

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.0.0.1"
    destination_device_ip: "10.0.0.2"
```

Optional interface remap example:

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.0.0.1"
    destination_device_ip: "10.0.0.2"
    interface_mappings:
      - source_interface_name: "GigabitEthernet1/0/1"
        destination_interface_name: "GigabitEthernet1/0/25"
      - source_interface_name: "GigabitEthernet1/0/2"
        destination_interface_name: "GigabitEthernet1/0/26"
```

## Step 3: Setup Env Variables and Run Playbook

The inventory file `inventory/demo_lab/hosts.yaml` reads Catalyst Center connection values from environment variables.

```bash
export HOSTIP=10.195.120.197
export CATALYST_CENTER_USERNAME=admin
export CATALYST_CENTER_PASSWORD='your_password'
export ANSIBLE_PYTHON_INTERPRETER="$(pwd)/.venv/bin/python"
```

Run:

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml \
  ./workflows/sda_port_assignment_migration/playbook/sda_port_assignment_migration_playbook.yml \
  --extra-vars VARS_FILE_PATH=./workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml \
  -vvvv
```

## Example Migration Result (Run on March 25, 2026)

Input used:

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.0.0.1"
    destination_device_ip: "10.0.0.2"
```

Generator stage result:
- `status: success`
- `components_processed: 1`
- `configurations_count: 2`
- Generated file: `/tmp/sda_port_assignment_migration/sda_port_assignment_source_10_0_0_1_to_10_0_0_2.yml`

What was migrated from source `10.0.0.1` to destination `10.0.0.2`:
- Total interfaces in source payload: `14`
- Interfaces: `GigabitEthernet1/0/1`, `GigabitEthernet1/0/2`, `GigabitEthernet1/0/3`, `GigabitEthernet1/0/5`, `GigabitEthernet1/0/6`, `GigabitEthernet1/0/7`, `GigabitEthernet1/0/10`, `GigabitEthernet1/0/12`, `GigabitEthernet1/0/13`, `GigabitEthernet1/0/14`, `GigabitEthernet1/0/15`, `GigabitEthernet1/0/16`, `GigabitEthernet1/0/17`, `GigabitEthernet1/0/18`

Apply stage result (`sda_host_port_onboarding_workflow_manager`):
- `status: success`
- Added/updated interfaces count: `8`
- Added/updated interfaces: `GigabitEthernet1/0/10`, `GigabitEthernet1/0/12`, `GigabitEthernet1/0/13`, `GigabitEthernet1/0/14`, `GigabitEthernet1/0/15`, `GigabitEthernet1/0/16`, `GigabitEthernet1/0/17`, `GigabitEthernet1/0/18`
- No-update interfaces count: `6`
- No-update interfaces: `GigabitEthernet1/0/1`, `GigabitEthernet1/0/2`, `GigabitEthernet1/0/3`, `GigabitEthernet1/0/5`, `GigabitEthernet1/0/6`, `GigabitEthernet1/0/7`

Workflow summary from logs:
- `port_assignment_migration_results` showed `generator_status: success` and `migration_status: success`
- `port_assignment_migration_results` also reports `interface_mapping_count` per migration entry
- `port_assignment_migration_results` reports `source_export_filter_mode` (`device_ip` when advanced filter schema is supported, otherwise `fabric_site_only`)
- Post-migration summary now reports interface outcomes:
  - `interfaces_moved`
  - `interfaces_moved_count`
  - `interfaces_targeted`
  - `interfaces_updated` (created/updated by apply tasks)
  - `interfaces_no_change`
  - `interfaces_unreported` (targeted interfaces not explicitly listed by module result)
  - `catalyst_center_change_count` (only actual Catalyst Center updates/creates)
- Local housekeeping tasks (generated file create/remove, local temp directory handling) are excluded from Ansible `changed` count.
- Temporary generated source file was removed successfully
- `PLAY RECAP`: `failed=0`, `unreachable=0`

## How Verification Was Done

1. Verified source export succeeded and included site data for `Global/California/23`.
2. Verified source device selection by exact IP match (`10.0.0.1`) from `generated_source_config.config`.
3. Verified destination payload was built with destination IP (`10.0.0.2`) and source port assignments list (with optional `interface_mappings` remap when provided).
4. Verified apply task returned `status: success` and reported interface-level outcomes (`success_interfaces` and `port_assignments_no_update_needed`).
5. Verified final play recap had no failures.

## Notes

- Each migration entry is processed independently.
- The workflow fails fast if source device port assignments are not found in the specified fabric site.
- The workflow removes any existing generated export file before each run to avoid false-failure behavior from config generator idempotency checks.
- Export behavior supports both filter schemas for compatibility:
  - Preferred: per-site list with `device_ips` (source-device-aware export).
  - Fallback: legacy `fabric_site_name_hierarchy` only.
- The workflow validates interface remap integrity:
  - Duplicate `source_interface_name` values are rejected.
  - Duplicate `destination_interface_name` values are rejected.
  - Any mapped source interface missing from exported source payload is rejected.
  - Any duplicate destination interface in final payload (after remap) is rejected.
- Generated intermediate export files are removed by default (`cleanup_generated_files: true`).
