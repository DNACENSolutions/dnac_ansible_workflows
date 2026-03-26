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

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml \
  ./workflows/sda_port_assignment_migration/playbook/sda_port_assignment_migration_playbook.yml \
  --extra-vars VARS_FILE_PATH=./workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml -vvvv
```

## Notes

- Each migration entry is processed independently.
- The workflow fails fast if source device port assignments are not found in the specified fabric site.
- Generated intermediate export files are removed by default (`cleanup_generated_files: true`).
