# Switch Refresh Regression Playbooks

This regression package validates Switch Refresh with both onboarding methods currently used in the lab:

- LAN Automation path: source `ENL1` to replacement `ENL2`
- Discovery path: source `EN1` to replacement `EN2`
- Reverse LAN Automation path: source `ENL2` to replacement `ENL1`
- Reverse Discovery path: source `EN2` to replacement `EN1`

The playbooks intentionally compose the supported workflow entrypoints already present in this repository. They do not duplicate LAN Automation, Discovery, Provision, SDA fabric-device, port-assignment migration, or device-removal logic.

Use `tools/switch_refresh_regression_runner.sh` for lab regression runs. The runner selects the validated Ansible runtime, sets collection paths, prompts for missing secrets without echoing them, and writes timestamped logs under `logs/switch_refresh_regression/`.

## Required Regression Flows

Full flows:

1. LAN Automation full refresh: onboard replacement with LAN Automation, provision replacement, add replacement to fabric, migrate host-port assignments, clean up source, and validate final state.
2. Discovery full refresh: onboard replacement with Discovery, provision replacement, add replacement to fabric, migrate host-port assignments, clean up source, and validate final state.

Cut flows:

1. LAN Automation onboarding only.
2. Discovery onboarding only.
3. Replacement provisioning only.
4. Fabric onboarding only.
5. Port-assignment migration only.
6. Source cleanup only: host-port cleanup, fabric role removal, unprovision, and inventory removal as supported by `sda_device_removal_and_unprovision`.
7. Final validation only: inventory checks that the replacement remains present and the cleaned-up source is absent.
8. Read-only diagnostics: inventory, fabric, and interface discovery checks used when the lab state changes between runs.

## Run From Repository Root

Export non-secret connection values before running. The runner prompts for any missing passwords.

```bash
cd /path/to/dnac_ansible_workflows
export HOSTIP=10.195.243.100
export CATALYST_CENTER_USERNAME=iac4
export SWITCH_USERNAME=wlcaccess
export SWITCH_REFRESH_ANSIBLE_VENV=/path/to/venv-with-ansible
export SWITCH_REFRESH_COLLECTIONS_PATH=/path/to/catalystcenter-ansible/collections

tools/switch_refresh_regression_runner.sh full-lan
tools/switch_refresh_regression_runner.sh full-discovery
```

For direct playbook execution, export the expected credentials and use a compatible Ansible runtime and collection path for the Catalyst Center collection version under test.

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/switch_refresh_regression/playbook/full_lan_automation_refresh.yml

ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/switch_refresh_regression/playbook/full_discovery_refresh.yml
```

## Validated Cut-Flow Sequences

Forward LAN Automation, `ENL1` to `ENL2`:

```bash
tools/switch_refresh_regression_runner.sh lan-onboard
tools/switch_refresh_regression_runner.sh lan-provision
tools/switch_refresh_regression_runner.sh lan-set-access-role
tools/switch_refresh_regression_runner.sh lan-fabric
tools/switch_refresh_regression_runner.sh lan-migrate
tools/switch_refresh_regression_runner.sh lan-cleanup
tools/switch_refresh_regression_runner.sh lan-validate
```

Forward Discovery, `EN1` to `EN2`:

```bash
tools/switch_refresh_regression_runner.sh discovery-onboard
tools/switch_refresh_regression_runner.sh discovery-provision
tools/switch_refresh_regression_runner.sh discovery-set-access-role
tools/switch_refresh_regression_runner.sh discovery-fabric
tools/switch_refresh_regression_runner.sh discovery-migrate
tools/switch_refresh_regression_runner.sh discovery-cleanup
tools/switch_refresh_regression_runner.sh discovery-validate
```

Reverse Discovery, `EN2` to `EN1`:

```bash
tools/switch_refresh_regression_runner.sh discovery-seed-en2-port
tools/switch_refresh_regression_runner.sh discovery-onboard-en1
tools/switch_refresh_regression_runner.sh discovery-provision-en1
tools/switch_refresh_regression_runner.sh discovery-set-en1-access-role
tools/switch_refresh_regression_runner.sh discovery-fabric-en1
tools/switch_refresh_regression_runner.sh discovery-migrate-en2-to-en1
tools/switch_refresh_regression_runner.sh discovery-cleanup
```

Reverse LAN Automation, `ENL2` to `ENL1`:

```bash
tools/switch_refresh_regression_runner.sh lan-onboard-enl1
tools/switch_refresh_regression_runner.sh lan-provision-enl1
tools/switch_refresh_regression_runner.sh lan-set-enl1-access-role
tools/switch_refresh_regression_runner.sh lan-fabric-enl1
tools/switch_refresh_regression_runner.sh lan-list-enl-interfaces
tools/switch_refresh_regression_runner.sh lan-seed-enl2-port
tools/switch_refresh_regression_runner.sh lan-migrate-enl2-to-enl1
tools/switch_refresh_regression_runner.sh lan-cleanup-enl2
```

Useful individual cut-flow examples:

```bash
tools/switch_refresh_regression_runner.sh lan-diagnose-enl1
tools/switch_refresh_regression_runner.sh lan-diagnose-enl2
tools/switch_refresh_regression_runner.sh discovery-diagnose-en2
tools/switch_refresh_regression_runner.sh discovery-list-en2-interfaces
```

## Lab Data

The default lab vars are under `workflows/switch_refresh_regression/vars/`:

- LAN Automation: `ENL1` `204.1.3.248` to `ENL2` `204.1.3.249`
- Discovery: `EN1` `204.1.2.5` to `EN2` `204.1.2.6`
- SDA fabric site: `Global/USA/San Jose/BLDG23`
- Site assignment: `Global/USA/San Jose/BLDG23`
- Forward Discovery and forward LAN default migration: `GigabitEthernet1/0/3` to `GigabitEthernet1/0/3`
- Reverse Discovery migration: `EN2 GigabitEthernet2/0/3` to `EN1 GigabitEthernet1/0/3`
- Reverse LAN Automation migration: `ENL2 GigabitEthernet2/0/3` to `ENL1 GigabitEthernet1/0/3`

Adjust only the vars files when lab addressing, hostnames, serial numbers, seed interfaces, or port mappings change.

## Troubleshooting Notes

- Fabric onboarding expects the replacement switch inventory role to be `ACCESS`. Run the relevant `*-set-*-access-role` cut before `*-fabric*` when onboarding was just completed.
- LAN Automation can return Ansible success even when the Catalyst Center LAN Automation session discovered zero devices. Use `lan-diagnose-enl1` or `lan-diagnose-enl2` if inventory lookup fails after onboarding.
- If port assignment creation fails with "interface name do not exist", run the matching interface diagnostic and update the source and destination interface mapping vars.
- Cleanup supports already-absent devices when the vars opt into `allow_missing_device`; otherwise the cleanup flow expects exactly one inventory match.

## pyATS Regression Harness Integration

This repository owns the Ansible workflow playbooks and vars. The daily pyATS regression harness can call these playbooks from its testcase file using the existing `AnsibleRunner` pattern:

- pyATS testcase points `playbook=` to one of the playbooks under `workflows/switch_refresh_regression/playbook/`.
- If the harness runs by tags, add tags in a wrapper playbook or in the pyATS testcase phases that call each cut-flow playbook.
- The pyATS usecase map, for example `usecasemaps/ansiblesanity/ansible_usecases_maps.yaml`, should add the Switch Refresh suite under the desired numeric execution phase.
- The pyATS job entry point, for example `job/iac2/iac2_ansible.py`, should include that execution phase in `EXEC_UCGROUP_NUMBERS_LIST` or its default run data.

Keep those pyATS files in the regression harness repository. This package is intentionally limited to the Ansible-side regression assets so it can also be run directly from the workflow repository during development and troubleshooting.