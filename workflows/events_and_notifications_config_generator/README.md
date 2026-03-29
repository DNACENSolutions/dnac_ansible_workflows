# Events and Notifications Config Generator

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

The Events and Notifications config generator automates YAML playbook generation for destinations, subscriptions, and ITSM integration settings in Cisco Catalyst Center. It generates output compatible with `events_and_notifications_workflow_manager`.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `events_and_notifications_workflow_manager`.
  - Extract destinations, event subscriptions, and ITSM settings.
  - Resolve output into workflow-manager-ready YAML.
  - Reuse generated files for backup, migration, and audit.
- **Component Filtering**: Generate specific destination and notification component types.
- **Name-based Filters**: Filter by destination names, subscription names, and ITSM instance names.
- **Flexible Output**: Supports custom `file_path` and `file_mode` (`overwrite` / `append`).
- **Brownfield Discovery**: Omit `config` (or use workflow convenience flag) to generate all supported data.

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

- Catalyst Center credentials with events and notifications API access
- Network connectivity to Catalyst Center
- Existing destination/subscription/ITSM data (for targeted export use cases)

---

## Workflow Structure

```
events_and_notifications_config_generator/
├── playbook/
│   └── events_and_notifications_config_generator.yml   # Main operations
├── vars/
│   └── events_and_notifications_config_inputs.yml      # Input examples
├── schema/
│   └── events_and_notifications_config_schema.yml      # Input validation
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

- `webhook_destinations`
- `email_destinations`
- `syslog_destinations`
- `snmp_destinations`
- `itsm_settings`
- `webhook_event_notifications`
- `email_event_notifications`
- `syslog_event_notifications`

### Additional Filter Blocks

- `destination_filters`
  - `destination_names`
  - `destination_types`: `webhook`, `email`, `syslog`, `snmp`
- `notification_filters`
  - `subscription_names`
  - `notification_types`: `webhook`, `email`, `syslog`
- `itsm_filters`
  - `instance_names`

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
`workflows/events_and_notifications_config_generator/vars/events_and_notifications_config_inputs.yml`

```yaml
events_and_notifications_config:
  - generate_all_configurations: true
    file_path: "/tmp/events_and_notifications_complete_config.yml"
```

### Step 3: Validate Configuration

```bash
./tools/validate.sh -s workflows/events_and_notifications_config_generator/schema/events_and_notifications_config_schema.yml \
  -d workflows/events_and_notifications_config_generator/vars/events_and_notifications_config_inputs.yml
```

### Step 4: Execute Playbook

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/events_and_notifications_config_generator/playbook/events_and_notifications_config_generator.yml \
  --extra-vars VARS_FILE_PATH=./workflows/events_and_notifications_config_generator/vars/events_and_notifications_config_inputs.yml \
  -vvvv
```

---

## Operations

### Generate Operations (state: gathered)

1. **Generate all events and notifications data**
- Set `generate_all_configurations: true`.

2. **Generate selected destination component types**
- Use `components_list` and `destination_filters`.

3. **Generate selected subscription component types**
- Use `components_list` and `notification_filters`.

4. **Generate ITSM settings by instance name**
- Use `components_list: ["itsm_settings"]` and `itsm_filters.instance_names`.

---

## Examples

### Example 1: Generate all events and notifications configurations

```yaml
events_and_notifications_config:
  - generate_all_configurations: true
    file_path: "/tmp/events_and_notifications_complete_config.yml"
```

### Example 2: Filter destination components by names and types

```yaml
events_and_notifications_config:
  - file_path: "/tmp/events_notifications_destinations.yml"
    component_specific_filters:
      components_list: ["webhook_destinations", "email_destinations"]
      destination_filters:
        destination_names: ["my-webhook-1", "ops-email-destination"]
        destination_types: ["webhook", "email"]
```

### Example 3: Filter event subscription components

```yaml
events_and_notifications_config:
  - file_path: "/tmp/events_notifications_subscriptions.yml"
    component_specific_filters:
      components_list: ["webhook_event_notifications", "email_event_notifications"]
      notification_filters:
        subscription_names: ["Critical Alerts"]
        notification_types: ["webhook"]
```

---

## Notes

- `events_and_notifications_playbook_config_generator` expects `config` as a dictionary when filters are used.
- This workflow omits `config` when filters are absent, which triggers full generation mode.
- When filter blocks are supplied, the module can auto-populate missing component entries in `components_list`.
