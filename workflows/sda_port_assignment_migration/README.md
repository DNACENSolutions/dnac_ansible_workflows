# SDA Port Assignment Migration

This workflow migrates SDA host port assignments from a source device IP to a destination device IP.

It uses:
- `cisco.dnac.sda_host_port_onboarding_playbook_config_generator` to export source port assignments.
- `cisco.dnac.sda_host_port_onboarding_workflow_manager` to apply those assignments to destination devices.

## Input Data Model

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.195.120.173"
    destination_device_ip: "10.195.120.219"
```

## Files

- `playbook/sda_port_assignment_migration_playbook.yml`
- `playbook/tasks/migrate_single_port_assignment.yml`
- `schema/sda_port_assignment_migration_schema.yml`
- `vars/sda_port_assignment_migration_input.yml`

## Run

Use absolute paths:

```bash
CWD="$(pwd)"
ansible-playbook -i "$CWD/inventory/demo_lab/hosts.yaml" \
  "$CWD/workflows/sda_port_assignment_migration/playbook/sda_port_assignment_migration_playbook.yml" \
  --extra-vars "VARS_FILE_PATH=$CWD/workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml" \
  -vvvv
```

Or use relative paths:

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml \
  ./workflows/sda_port_assignment_migration/playbook/sda_port_assignment_migration_playbook.yml \
  --extra-vars VARS_FILE_PATH=./workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml -vvvv
```

## Example Migration Result (Run on March 25, 2026)

Input used:

```yaml
port_assignment_migration:
  - fabric_site: "Global/California/23"
    source_device_ip: "10.195.120.173"
    destination_device_ip: "10.195.120.219"
```

Generator stage result:
- `status: success`
- `components_processed: 1`
- `configurations_count: 2`
- Generated file: `/tmp/sda_port_assignment_migration/sda_port_assignment_source_10_195_120_173_to_10_195_120_219.yml`

What was migrated from source `10.195.120.173` to destination `10.195.120.219`:
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
- Temporary generated source file was removed successfully
- `PLAY RECAP`: `failed=0`, `unreachable=0`

## How Verification Was Done

1. Verified source export succeeded and included site data for `Global/California/23`.
2. Verified source device selection by exact IP match (`10.195.120.173`) from `generated_source_config.config`.
3. Verified destination payload was built with destination IP (`10.195.120.219`) and source port assignments list.
4. Verified apply task returned `status: success` and reported interface-level outcomes (`success_interfaces` and `port_assignments_no_update_needed`).
5. Verified final play recap had no failures.

## Notes

- Each migration entry is processed independently.
- The workflow fails fast if source device port assignments are not found in the specified fabric site.
- Generated intermediate export files are removed by default (`cleanup_generated_files: true`).
