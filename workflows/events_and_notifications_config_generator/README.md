# Events and Notifications Config Generator

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
- **Brownfield Discovery**: Omit `config` to generate all supported data.

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
| `config` | dict | No | omitted | Module `config` dict. Must include `component_specific_filters` when provided. Omit to generate all 8 component types (full discovery) |
| `file_path` | string | No | auto-generated | Output file path for generated YAML. Format when auto-generated: `events_and_notifications_playbook_config_<YYYY-MM-DD_HH-MM-SS>.yml` |
| `file_mode` | string | No | `overwrite` | File write mode: `overwrite` or `append` |

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
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/events_and_notifications_config_generator/playbook/events_and_notifications_config_generator.yml -vvvv
```


## Operations

### Generate Operations (state: gathered)

Pass `config` with `component_specific_filters` for targeted export. Omit `config` entirely to trigger full discovery (all 8 component types).

#### 1. Generate all events and notifications data

Omit both `config` and `component_specific_filters` to trigger full discovery:

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/complete_config.yml"
```

**Validate:**
```bash
./tools/schemavalidation.sh \
  -s workflows/events_and_notifications_config_generator/schema/events_and_notifications_config_schema.yml \
  -v workflows/events_and_notifications_config_generator/vars/events_and_notifications_config_inputs.yml
```

**Execute:**
```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/events_and_notifications_config_generator/playbook/events_and_notifications_config_generator.yml \
  --extra-vars VARS_FILE_PATH=./workflows/events_and_notifications_config_generator/vars/events_and_notifications_config_inputs.yml
```

#### 2. Generate selected destination component types

Use `config.component_specific_filters` with `components_list` and `destination_filters`.

#### 3. Generate selected subscription component types

Use `config.component_specific_filters` with `components_list` and `notification_filters`.

#### 4. Generate ITSM settings by instance name

Use `config.component_specific_filters` with `components_list: ["itsm_settings"]` and `itsm_filters.instance_names`.

---

## Examples

### Example 1: Generate all events and notifications configurations

Omit `config` — module retrieves all 8 component types.

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/complete_config.yml"
```

### Example 2: Filter destination components

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/destinations.yml"
    config:
      component_specific_filters:
        components_list: ["webhook_destinations", "email_destinations"]
        destination_filters:
          destination_names: ["my-webhook-1", "ops-email-destination"]
          destination_types: ["webhook", "email"]
```

### Example 3: Filter event subscription components

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/subscriptions.yml"
    config:
      component_specific_filters:
        components_list: ["webhook_event_notifications", "email_event_notifications"]
        notification_filters:
          subscription_names: ["Critical Alerts"]
          notification_types: ["webhook"]
```

### Example 4: ITSM settings filter with append mode

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/itsm.yml"
    file_mode: append
    config:
      component_specific_filters:
        components_list: ["itsm_settings"]
        itsm_filters:
          instance_names:
            - "ServiceNow-Prod"
            - "BMC-Remedy"
```

### Example 5: Combined filters (destinations + notifications + ITSM)

```yaml
events_and_notifications_config:
  - file_path: "events_and_notifications_config/combined.yml"
    config:
      component_specific_filters:
        components_list:
          - "webhook_destinations"
          - "email_destinations"
          - "webhook_event_notifications"
          - "email_event_notifications"
          - "itsm_settings"
        destination_filters:
          destination_names: ["prod-webhook"]
          destination_types: ["webhook"]
        notification_filters:
          subscription_names: ["Critical Alerts"]
          notification_types: ["webhook"]
        itsm_filters:
          instance_names: ["ServiceNow-Prod"]
```

---

## Notes

- Omit `config` entirely to run in full discovery mode (all 8 component types).
- When `config` is provided, `component_specific_filters` is mandatory.
- When filter blocks (`destination_filters`, `notification_filters`, `itsm_filters`) are supplied, the module auto-adds the corresponding components to `components_list` if not already present.
- Generated YAML files contain `***REDACTED***` placeholders for passwords.
