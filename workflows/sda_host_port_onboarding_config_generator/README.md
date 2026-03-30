# SDA Host Port Onboarding Config Generator

This workflow runs the `cisco.dnac.sda_host_port_onboarding_playbook_config_generator` module to export host port onboarding configurations from Cisco Catalyst Center into a YAML file that is compatible with `sda_host_port_onboarding_workflow_manager`.

## Files

- `playbook/sda_host_port_onboarding_config_generator.yml`
- `schema/sda_host_port_onboarding_config_schema.yml`
- `vars/sda_host_port_onboarding_config_input.yml`

## Run

The playbook supports two input methods:

### Option A: Vars file input (recommended for version-controlled configs)

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/sda_host_port_onboarding_config_generator/playbook/sda_host_port_onboarding_config_generator.yml \
  --extra-vars VARS_FILE_PATH=/absolute/path/to/dnac_ansible_workflows/workflows/sda_host_port_onboarding_config_generator/vars/sda_host_port_onboarding_config_input.yml \
  -vvvv
```

### Option B: Inventory / host variable input

Omit `VARS_FILE_PATH` and define `sda_host_port_onboarding_config` directly as a host variable in your inventory file or in `host_vars`/`group_vars`.

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/sda_host_port_onboarding_config_generator/playbook/sda_host_port_onboarding_config_generator.yml \
  -vvvv
```

The playbook auto-detects the input source and prints it at the start:
- `Input source: vars file <path>` when using Option A
- `Input source: inventory / host variables (VARS_FILE_PATH not provided)` when using Option B

> **Note:** When `VARS_FILE_PATH` is provided, it takes **precedence** over inventory variables.

## Notes

- `state` supports only `gathered`.
- If `generate_all_configurations: true`, all supported onboarding components are exported.
- `file_mode` supports `overwrite` (default) and `append`.
- Uses list-based configuration structure with `sda_host_port_onboarding_config` variable.
- Supports conditional `include_vars` for flexible input methods.

## Workflow Steps
## User Flow (3 Steps)

```mermaid
flowchart TD
  A[Start] --> B[Step 1: Create virtual env and install dependencies]
  B --> C[Step 2: Provide workflow inputs]
  C --> D{Choose input location}
  D -->|Option A| E[Update inventory hosts.yaml]
  D -->|Option B| F[Update vars input file]
  E --> G[Step 3: Export env vars]
  F --> G
  G --> H[Run ansible-playbook]
  H --> I[Review playbook summary output]
  I --> J[Done]
```

### Installation and Run (Aligned)

1. Create and activate a Python virtual environment, then install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install cisco.dnac --force
```

2. Provide workflow inputs in either inventory (`inventory/demo_lab/hosts.yaml`) or the workflow `vars/` file.

3. Export Catalyst Center environment variables and run the playbook.

```bash
export HOSTIP=<catalyst-center-ip-or-fqdn>
export CATALYST_CENTER_USERNAME=<username>
export CATALYST_CENTER_PASSWORD='<password>'
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/sda_host_port_onboarding_config_generator/playbook/sda_host_port_onboarding_config_generator.yml -vvvv
```
