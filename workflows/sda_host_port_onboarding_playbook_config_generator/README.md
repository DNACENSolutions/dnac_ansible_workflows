# SDA Host Port Onboarding Playbook Config Generator

This workflow runs the `cisco.dnac.sda_host_port_onboarding_playbook_config_generator` module to export host port onboarding configurations from Cisco Catalyst Center into a YAML file that is compatible with `sda_host_port_onboarding_workflow_manager`.

## Files

- `playbook/sda_host_port_onboarding_playbook_config_generator_playbook.yml`
- `schema/sda_host_port_onboarding_playbook_config_generator_schema.yml`
- `vars/sda_host_port_onboarding_playbook_config_generator_input.yml`

## Run

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml \
  ./workflows/sda_host_port_onboarding_playbook_config_generator/playbook/sda_host_port_onboarding_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=./../vars/sda_host_port_onboarding_playbook_config_generator_input.yml -vvvv
```

## Notes

- `state` supports only `gathered`.
- If `config` is omitted, all supported onboarding components are exported.
- `file_mode` supports `overwrite` and `append`.
