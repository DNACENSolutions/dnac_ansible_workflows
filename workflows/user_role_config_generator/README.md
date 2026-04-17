# User Role Config Generator

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

## Overview

The User Role config generator automates YAML playbook generation for existing users and custom roles in Cisco Catalyst Center. It produces output compatible with `user_role_workflow_manager`, helping with brownfield extraction, backup, and role/user migration workflows.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `user_role_workflow_manager`.
  - Extract existing user accounts and custom role definitions.
  - Transform API data into playbook-ready YAML.
  - Reuse generated files for automation and recovery scenarios.
- **Component Filtering**: Generate `user_details`, `role_details`, or both.
- **User Filtering**: Filter users by `username`, `email`, and assigned `role_name`.
- **Role Filtering**: Filter custom roles by `role_name`.
- **Flexible Output**: Supports custom `file_path` and `file_mode` (`overwrite` / `append`).
- **Brownfield Discovery**: Omit `component_specific_filters` or set `generate_all_configurations: true` to generate all supported user/role components.

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.dnac collection | 6.44.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.5.3+ |
| dnacentersdk | 2.7.2+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center credentials with access to user/role APIs
- Network connectivity to Catalyst Center
- Existing users and/or custom roles in Catalyst Center

---

## Workflow Structure

```
user_role_config_generator/
├── playbook/
│   └── user_role_config_generator.yml          # Main operations
├── vars/
│   └── user_role_config_inputs.yml             # Input examples
├── schema/
│   └── user_role_config_schema.yml             # Input validation
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
| `config` | dict | No | omitted | Standard module-shaped config wrapper. If provided, it must contain `component_specific_filters`. |
| `component_specific_filters` | dict | No | omitted | Workflow convenience input that is wrapped into module `config.component_specific_filters` |

### Supported Components

- `user_details`
- `role_details`

### Filters

- `user_details` filter keys (list of dictionaries):
  - `username`: list of usernames
  - `email`: list of email addresses
  - `role_name`: list of role names assigned to users
- `role_details` filter keys (list of dictionaries):
  - `role_name`: list of custom role names

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
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/user_role_config_generator/playbook/user_role_config_generator.yml -vvvv
```


## Operations

### Generate Operations (state: gathered)

Use `user_role_config_generator.yml` for all generation tasks.

1. **Generate all user/role configurations**
- Set `generate_all_configurations: true`.

2. **Generate user component only**
- Use `component_specific_filters.components_list: ["user_details"]`.

3. **Generate role component only**
- Use `component_specific_filters.components_list: ["role_details"]`.

4. **Generate filtered user/role slices**
- Provide list-based filters under `user_details` / `role_details`.

5. **Append generated output**
- Set `file_mode: append` to append into an existing file.

---

## Examples

### Example 1: Generate all users and roles

```yaml
user_role_config:
  - generate_all_configurations: true
    file_path: "/tmp/user_role_complete_config.yml"
```

### Example 2: Generate users by email filter

```yaml
user_role_config:
  - file_path: "/tmp/user_role_users_by_email.yml"
    component_specific_filters:
      components_list: ["user_details"]
      user_details:
        - email: ["admin@example.com", "operator@example.com"]
```

### Example 3: Generate custom roles by role_name

```yaml
user_role_config:
  - file_path: "/tmp/user_role_role_name_filter.yml"
    component_specific_filters:
      components_list: ["role_details"]
      role_details:
        - role_name: ["Custom-Admin-Role"]
```

---

## Notes

- `user_role_playbook_config_generator` expects `config` as a dictionary when filters are used.
- This workflow accepts either the standard `config.component_specific_filters` shape or the workflow convenience `component_specific_filters` shape.
- When filters are absent, the workflow omits `config`, which triggers full generation mode.
- Role filtering under `role_details` includes only custom roles returned by the module logic.
