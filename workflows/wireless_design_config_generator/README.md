# Wireless Design Config Generator

## Table of Contents

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

The Wireless Design config generator automates YAML playbook generation for existing wireless design settings in Cisco Catalyst Center. It generates output compatible with `wireless_design_workflow_manager`, enabling brownfield extraction and easy reuse of current wireless design configurations.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `wireless_design_workflow_manager`.
  - Extract existing wireless settings (SSIDs, interfaces, profiles, anchor groups, feature templates).
  - Convert API responses into playbook-ready YAML.
  - Reuse generated files for migration, backup, and automation workflows.
- **Component Filtering**: Target specific components such as `ssids`, `interfaces`, `power_profiles`, and `feature_template_config`.
- **Advanced Filtering**: Filter by SSID/site/type, interface/vlan, profile names, feature template type, and more.
- **Flexible Output**: Supports custom `file_path` and `file_mode` (`overwrite` / `append`).
- **Brownfield Discovery**: Omit `config` (or use workflow convenience flag) to generate all supported wireless design configurations.

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.dnac collection | 6.44.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.7.9+ |
| dnacentersdk | 2.9.3+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center credentials with read access to wireless design APIs
- Network connectivity to Catalyst Center
- Existing wireless configuration data in Catalyst Center

---

## Workflow Structure

```
wireless_design_config_generator/
├── playbook/
│   └── wireless_design_config_generator.yml          # Main operations
├── vars/
│   └── wireless_design_config_inputs.yml             # Input examples
├── schema/
│   └── wireless_design_config_schema.yml             # Input validation
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

- `ssids`
- `interfaces`
- `power_profiles`
- `access_point_profiles`
- `radio_frequency_profiles`
- `anchor_groups`
- `feature_template_config`
- `802_11_be_profiles`
- `flex_connect_configuration`

### Common Filters

- `ssids`: `site_name_hierarchy`, `ssid_name`, `ssid_type` (`Enterprise` / `Guest`)
- `interfaces`: `interface_name`, `vlan_id`
- `power_profiles`: `power_profile_name`
- `access_point_profiles`: `ap_profile_name`
- `radio_frequency_profiles`: `rf_profile_name`
- `anchor_groups`: `anchor_group_name`
- `feature_template_config`: `feature_template_type`, `design_name`
- `802_11_be_profiles`: `profile_name`
- `flex_connect_configuration`: `site_name_hierarchy`

---

## Getting Started

### Step 1: Configure Inventory

Example `inventory/demo_lab/hosts.yml`:

```yaml
catalyst_center_hosts:
  hosts:
    catalyst_center_primary:
      catalyst_center_host: 10.0.0.0
      catalyst_center_username: admin
      catalyst_center_password: "password"
      catalyst_center_port: 443
      catalyst_center_verify: false
      catalyst_center_version: 2.3.7.9
```

### Step 2: Configure Variables

Edit:
`workflows/wireless_design_config_generator/vars/wireless_design_config_inputs.yml`

```yaml
wireless_design_config:
  - generate_all_configurations: true
    file_path: "/tmp/wireless_design_complete_config.yml"
```

### Step 3: Validate Configuration

```bash
./tools/validate.sh -s workflows/wireless_design_config_generator/schema/wireless_design_config_schema.yml \
  -d workflows/wireless_design_config_generator/vars/wireless_design_config_inputs.yml
```

### Step 4: Execute Playbook

#### Option A: Vars file input (recommended)

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/wireless_design_config_generator/playbook/wireless_design_config_generator.yml \
  --extra-vars VARS_FILE_PATH=./workflows/wireless_design_config_generator/vars/wireless_design_config_inputs.yml \
  -vvvv
```

#### Option B: Inventory / host variable input

Omit `VARS_FILE_PATH` and define `wireless_design_config` in inventory or `host_vars`.

---

## Operations

### Generate Operations (state: gathered)

Use `wireless_design_config_generator.yml` for all generation tasks.

1. **Generate all wireless design configurations**
- Set `generate_all_configurations: true`.

2. **Generate selected components only**
- Use `component_specific_filters.components_list`.

3. **Generate filtered configuration slices**
- Provide filters under each component (`ssids`, `interfaces`, `feature_template_config`, etc.).

4. **Append generated output**
- Set `file_mode: append` to append into an existing file.

---

## Examples

### Example 1: Generate all wireless design settings

```yaml
wireless_design_config:
  - generate_all_configurations: true
    file_path: "/tmp/wireless_design_complete_config.yml"
```

### Example 2: Generate SSIDs for a specific site

```yaml
wireless_design_config:
  - file_path: "/tmp/wireless_design_ssids.yml"
    component_specific_filters:
      components_list: ["ssids"]
      ssids:
        - site_name_hierarchy: "Global/USA/San Jose"
          ssid_type: "Guest"
```

### Example 3: Generate feature templates with filter and append

```yaml
wireless_design_config:
  - file_path: "/tmp/wireless_design_aggregate.yml"
    file_mode: "append"
    component_specific_filters:
      components_list: ["feature_template_config"]
      feature_template_config:
        - feature_template_type: "advanced_ssid"
          design_name: "Enterprise Wireless Design"
```

---

## Notes

- `wireless_design_playbook_config_generator` expects `config` as a dictionary when filters are used.
- An empty dictionary for `config` is invalid at module level.
- This workflow omits `config` when filters are absent, which triggers full generation mode.
