# SDA Fabric Devices Config Generator

## Table of Contents

- [User Flow (3 Steps)](#user-flow-3-steps)

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Workflow Structure](#workflow-structure)
- [Schema Parameters](#schema-parameters)
- [Getting Started](#getting-started)
- [Operations](#operations)
- [Examples](#examples)---

## Overview

The SDA Fabric Devices config generator automates YAML playbook generation for existing SDA fabric devices in Cisco Catalyst Center. It generates output compatible with `sda_fabric_devices_workflow_manager` for brownfield export and migration of fabric device-role assignments and handoff-related configuration.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `sda_fabric_devices_workflow_manager`.
  - Extract existing fabric device settings from Catalyst Center.
  - Convert API responses into workflow-manager-ready YAML.
  - Reuse generated files for backup and migration.
- **Component Filtering**: Generate `fabric_devices` selectively.
- **Fabric and Device Filtering**: Filter by `fabric_name`, `device_ip`, and/or `device_roles`.
- **Flexible Output**: Supports custom `file_path` and `file_mode` (`overwrite` / `append`).
- **Brownfield Discovery**: Omit `config` (or use workflow convenience flag) to generate all fabric devices.

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.dnac collection | 6.49.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.7.6+ |
| dnacentersdk | 2.4.5+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center credentials with SDA fabric API access
- Network connectivity to Catalyst Center
- Existing SDA fabric devices (for targeted export use cases)

---

## Workflow Structure

```
sda_fabric_devices_config_generator/
├── playbook/
│   └── sda_fabric_devices_config_generator.yml    # Main operations
├── vars/
│   └── sda_fabric_devices_config_inputs.yml       # Input examples
├── schema/
│   └── sda_fabric_devices_config_schema.yml       # Input validation
└── README.md
```

---

## Schema Parameters

### Basic Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `generate_all_configurations` | boolean | No | false | Workflow convenience flag. When true, playbook omits module `config` |
| `file_path` | string | No | auto-generated | Output file path for generated YAML |
| `file_mode` | string | No | `overwrite` | File write mode: `overwrite` or `append` |
| `component_specific_filters` | dict | No | omitted | Component and filters passed to module `config` |

### Component Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `components_list` | list[string] | No | Supported value: `fabric_devices` |
| `fabric_devices` | dict | No | Fabric device filters (`fabric_name`, `device_ip`, `device_roles`) |

### Fabric Device Filter Fields

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fabric_name` | string | Yes* | Fabric hierarchy name. Required when `fabric_devices` block is used |
| `device_ip` | string | No | Specific device management IP in the selected fabric |
| `device_roles` | list[string] | No | Device role filter list |

`device_roles` supported values:
- `CONTROL_PLANE_NODE`
- `EDGE_NODE`
- `BORDER_NODE`
- `WIRELESS_CONTROLLER_NODE`
- `EXTENDED_NODE`

---

## Getting Started

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
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/sda_fabric_devices_config_generator/playbook/sda_fabric_devices_config_generator.yml -vvvv
```


## Operations

### Generate Operations (state: gathered)

1. **Generate all fabric devices**
- Set `generate_all_configurations: true`.

2. **Generate all devices in a fabric**
- Set `fabric_devices.fabric_name`.

3. **Generate one device in a fabric**
- Set `fabric_devices.fabric_name` and `fabric_devices.device_ip`.

4. **Generate devices by role in a fabric**
- Set `fabric_devices.fabric_name` and `fabric_devices.device_roles`.

---

## Examples

### Example 1: Generate all SDA fabric devices

```yaml
sda_fabric_devices_config:
  - generate_all_configurations: true
    file_path: "/tmp/sda_fabric_devices_complete_config.yml"
```

### Example 2: Generate all devices for a fabric site

```yaml
sda_fabric_devices_config:
  - file_path: "/tmp/sda_fabric_devices_by_fabric.yml"
    component_specific_filters:
      components_list: ["fabric_devices"]
      fabric_devices:
        fabric_name: "Global/USA/SAN JOSE"
```

### Example 3: Generate devices by role

```yaml
sda_fabric_devices_config:
  - file_path: "/tmp/sda_fabric_devices_by_role.yml"
    component_specific_filters:
      components_list: ["fabric_devices"]
      fabric_devices:
        fabric_name: "Global/USA/SAN JOSE"
        device_roles: ["BORDER_NODE", "EDGE_NODE"]
```

---

## Notes

- `sda_fabric_devices_playbook_config_generator` expects `config` as a dictionary when filters are used.
- This workflow omits `config` when filters are absent, which triggers full generation mode.
- If `fabric_devices` is provided without `components_list`, the module auto-populates `components_list` internally.
