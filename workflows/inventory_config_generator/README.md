# Inventory Config Generator

## Table of Contents

- [User Flow (3 Steps)](#user-flow-3-steps)

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Workflow Structure](#workflow-structure)
- [Schema Parameters](#schema-parameters)
- [Getting Started](#getting-started)
- [Operations](#operations)
- [Examples](#examples)

---

## Overview

The Inventory config generator automates YAML configurations for inventory components in Cisco Catalyst Center. It generates output compatible with inventory_workflow_manager.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with inventory_workflow_manager module. Extract existing inventory configurations from your Cisco Catalyst Center. Convert them into properly formatted YAML files. Generate files that are ready to use with Ansible automation.
- **Component Filtering**: Selective generation using devices,device_roles and device_identifier.
- **Flexible Output**: Configurable file paths, auto-generated timestamped filenames, and `overwrite`/`append` file modes.
- **Brownfield Support**: Extract configurations from existing Catalyst Center deployments.
- **API Integration**: Leverages native Catalyst Center discovery APIs for data retrieval.

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.catalystcenter collection | 2.6.0 |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.7.9+ |
| catalystcentersdk | 2.7.2+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.catalystcenter
ansible-galaxy collection install ansible.utils
pip install catalystcentersdk
pip install yamale
```

---

## Workflow Structure

```text
inventory_config_generator/
├── playbook/
│   └── inventory_config_generator.yml
├── vars/
│   └── inventory_config_inputs.yml
├── schema/
│   └── inventory_config_schema.yml
└── README.md
```

---

## Schema Parameters

### Top-Level parameters 

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | — | Output file path for YAML configuration file. Required for automated output validation in this workflow. |
| `file_mode` | string | No | `overwrite` | File write mode — `overwrite` replaces the file, `append` adds to it . Only applicable when `file_path` is provided.|
| `config` | dict | No | omitted (all components) | Configuration filters dict. When omitted, all discovery configurations are retrieved. When provided, `global_filters` is mandatory. |


### Global Filters (within config parameter)

| Parameter | Type | Description |
|-----------|------|-------------|
| `global_filters` | dict | Required when `config` is provided. Filters to specify which components to include. |
| `devices` | list[string] | Matches each value against device `ip_address`, `hostname`, `serial_number`, `mac_address` |
| `device_roles` | list[string] | Allowed: `ACCESS`, `DISTRIBUTION`, `CORE`, `BORDER ROUTER`, `UNKNOWN` |
| `device_identifier` | string | Output key selector: `ip_address`, `hostname`, `serial_number`, `mac_address` |

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
ansible-galaxy collection install cisco.catalystcenter --force
```

2. Provide workflow inputs in either inventory (`inventory/demo_lab/hosts.yaml`) or the workflow `vars/` file.

3. Export Catalyst Center environment variables and run the playbook.

```bash
export HOSTIP=<catalyst-center-ip-or-fqdn>
export CATALYST_CENTER_USERNAME=<username>
export CATALYST_CENTER_PASSWORD='<password>'
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/discovery_config_generator/playbook/discovery_config_generator.yml -vvvv
```

---

## Operations

#### 1. Generate all inventory configurations:

**Description**: Retrieves all inventory configurations from Catalyst Center regardless of any filters

```yaml
inventory_config:
  - file_path: "/tmp/inventory_complete_config.yml"
```

**Terminal Return:**

```
 response:
        configurations_count: 31
        file_mode: overwrite
        file_path: /tmp/inventory_complete_config.yml
        message: YAML configuration file generated successfully for module 'inventory_workflow_manager'
        status: success
      status: success
```

### 2.Filter by devices values (IP/hostname/serial/mac)
```yaml
inventory_config:
  - file_path: "/tmp/inventory_devices_filter.yml"
    config:
      global_filters: 
        devices:
          - 204.1.216.3
```

**Terminal Return:**

```
response:
        configurations_count: 1
        file_mode: overwrite
        file_path: /tmp/inventory_devices_filter.yml
        message: YAML configuration file generated successfully for module 'inventory_workflow_manager'
        status: success
      status: success

```
### Filter by device roles

```yaml
inventory_config:
  - file_path: "/tmp/inventory_roles.yml"
    config:
      global_filters:
        device_roles: 
          - "DISTRIBUTION"
          - "BORDER ROUTER"
```
**Terminal Return:**

```
response:
        configurations_count: 7
        file_mode: overwrite
        file_path: /tmp/inventory_roles.yml
        message: YAML configuration file generated successfully for module 'inventory_workflow_manager'
        status: success
      status: success
```

**Validate and Execute:**

```bash
#validate
./tools/schemavalidation.sh \
  -s workflows/inventory_config_generator/schema/inventory_config_schema.yml \
  -v workflows/inventory_config_generator/vars/inventory_config_inputs.yml
```

```bash
./tools/schemavalidation.sh \
  -s workflows/inventory_config_generator/schema/inventory_config_schema.yml \
  -v workflows/inventory_config_generator/vars/inventory_config_inputs.yml
Validating:
  Schema: workflows/inventory_config_generator/schema/inventory_config_schema.yml
  Vars:   workflows/inventory_config_generator/vars/inventory_config_inputs.yml

✓ Validation successful
✓ Validation successful
```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/inventory_config_generator/playbook/inventory_config_generator.yml \
  --extra-vars VARS_FILE_PATH=../vars/inventory_config_inputs.yml
```

---

## Examples

### Example 1: Filter by devices values 

```yaml
inventory_config:
  - file_path: "/tmp/inventory_devices_filter.yml"
    config:
      global_filters: 
        devices:
          - 204.1.216.3
```
After running the playbook, the following YAML configuration is generated.

```yaml
config:
- ip_address_list:
  - 204.1.216.3
  role: ACCESS
```
### Example 2: Filter by roles and types

```yaml
inventory_config:
  - file_path: "/tmp/inventory_roles_types.yml"
    global_filters:
      device_roles: ["ACCESS", "BORDER ROUTER"]
      device_identifier: "serial_number"
```
After running the playbook, the following YAML configuration is generated.

```yaml
config:
- serial_number_list:
  - KWC24160JLL
  role: ACCESS
- serial_number_list:
  - 91GRFWNYCL6
  role: ACCESS
- serial_number_list:
  - 9TRQFABSFR2
  role: BORDER ROUTER
- serial_number_list:
  - FXS2424Q4PA
  role: ACCESS
- serial_number_list:
  - FJC2402A0TX
  role: BORDER ROUTER
- serial_number_list:
  - FXS2502Q2HC
  role: BORDER ROUTER
```

### Example 3: Filter by all global filters together (devices, roles, types) with mac add as identifier

```yaml
inventory_config:
  - file_path: "/tmp/inventory_all_filters.yml"
    config:
      global_filters:
        devices:
          - "68:7d:b4:06:b0:a0"
        device_roles:
          - "ACCESS"
        device_identifier: "mac_address"
```
After running the playbook, the following YAML configuration is generated.

```yaml
config:
- mac_address_list:
  - 68:7d:b4:06:b0:a0
  role: ACCESS
```
---

## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://catalystcentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)

## Inventory / group_vars Example

You can also run this workflow without `VARS_FILE_PATH` by moving the sample workflow data into inventory, `host_vars`, or `group_vars`.

1. Create an inventory vars file such as `inventory/group_vars/all.yml` or `inventory/host_vars/<host>.yml`.
2. Copy the sample workflow data from `workflows/inventory_config_generator/vars/inventory_config_inputs.yml` into that inventory vars file.
3. Keep the same top-level variable name in inventory: `inventory_config`.
4. Run the playbook without `VARS_FILE_PATH`:

```bash
ansible-playbook -i <inventory-file> workflows/inventory_config_generator/playbook/inventory_config_generator.yml -vvvv
```
## VARS_FILE_PATH Path Resolution

Ansible resolves `VARS_FILE_PATH` relative to the playbook directory, not the current working directory.

Use either of these forms:

- Relative to the playbook: `../vars/inventory_config_inputs.yml`
- Fully resolved from the repo root: `${PWD}/workflows/inventory_config_generator/vars/inventory_config_inputs.yml`

