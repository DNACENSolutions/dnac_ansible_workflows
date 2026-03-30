# Site Config Generator

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

The Site config generator automates YAML playbook generation for existing site hierarchy in Cisco Catalyst Center. It generates output compatible with `site_workflow_manager`, helping export areas, buildings, and floors for brownfield automation and migration workflows.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `site_workflow_manager`.
  - Extract site hierarchy data from Catalyst Center.
  - Convert API responses into playbook-ready YAML.
  - Reuse generated files for backup and migration.
- **Hierarchy Filtering**: Filter by `site_name_hierarchy` or `parent_name_hierarchy`.
- **Type Filtering**: Filter by `site_type` values: `area`, `building`, `floor`.
- **Flexible Output**: Supports custom `file_path` and `file_mode` (`overwrite` / `append`).
- **Brownfield Discovery**: Omit `config` (or use workflow convenience flag) to generate complete site hierarchy.

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.dnac collection | 6.45.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.7.9+ |
| dnacentersdk | 2.10.10+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center credentials with site API access
- Network connectivity to Catalyst Center
- Existing site hierarchy in Catalyst Center

---

## Workflow Structure

```
site_config_generator/
├── playbook/
│   └── site_config_generator.yml          # Main operations
├── vars/
│   └── site_config_inputs.yml             # Input examples
├── schema/
│   └── site_config_schema.yml             # Input validation
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

### Supported Components

- `site`

### Site Filters

- `site_name_hierarchy`: string or list of hierarchy strings
- `parent_name_hierarchy`: string or list of hierarchy strings
- `site_type`: list of `area`, `building`, `floor`

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
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/site_config_generator/playbook/site_config_generator.yml -vvvv
```


## Operations

### Generate Operations (state: gathered)

Use `site_config_generator.yml` for all generation tasks.

1. **Generate full site hierarchy**
- Set `generate_all_configurations: true`.

2. **Generate hierarchy by parent**
- Use `site[].parent_name_hierarchy`.

3. **Generate hierarchy by explicit site names**
- Use `site[].site_name_hierarchy`.

4. **Filter by type**
- Use `site[].site_type` with one or more of `area`, `building`, `floor`.

5. **Append generated output**
- Set `file_mode: append` to append into an existing file.

---

## Examples

### Example 1: Generate all site hierarchy

```yaml
site_config:
  - generate_all_configurations: true
    file_path: "/tmp/site_complete_config.yml"
```

### Example 2: Filter by parent hierarchy and site type

```yaml
site_config:
  - file_path: "/tmp/site_parent_and_type_filter.yml"
    component_specific_filters:
      components_list: ["site"]
      site:
        - parent_name_hierarchy: ["Global/USA", "Global/India"]
          site_type: ["building", "floor"]
```

### Example 3: Filter by explicit site hierarchy list

```yaml
site_config:
  - file_path: "/tmp/site_name_hierarchy_filter.yml"
    component_specific_filters:
      components_list: ["site"]
      site:
        - site_name_hierarchy:
            - "Global/USA/San Francisco"
            - "Global/USA/New York"
```

---

## Notes

- `site_playbook_config_generator` expects `config` as a dictionary when filters are used.
- This workflow omits `config` when filters are absent, which triggers full generation mode.
- Avoid combining `site_name_hierarchy` and `parent_name_hierarchy` in the same filter item to keep selection behavior unambiguous.
