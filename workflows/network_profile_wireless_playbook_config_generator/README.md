# Network Profile Wireless Playbook Config Generator

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Workflow Structure](#workflow-structure)
- [Schema Parameters](#schema-parameters)
- [Getting Started](#getting-started)
- [Operations](#operations)
- [Examples](#examples)
- [Filter Priority System](#filter-priority-system)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Network Profile Wireless Playbook Config Generator automates the creation of YAML playbook configurations for existing wireless network profiles deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing wireless infrastructure.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `network_profile_wireless_workflow_manager` module
  - Extract existing wireless network profiles from your Cisco Catalyst Center
  - Convert them into properly formatted YAML files
  - Generate files that are ready to use with Ansible automation
- **Priority-Based Filtering**: Intelligent filter hierarchy for targeted profile extraction
- **Comprehensive Component Discovery**: Extract profiles, SSIDs, AP zones, feature templates, Day-N templates, and interfaces
- **Flexible Output**: Configurable file paths with auto-generated naming conventions
- **Brownfield Support**: Extract configurations from existing Catalyst Center wireless deployments
- **Multi-Profile Generation**: Support for generating multiple configuration files in a single execution
- **API Integration**: Leverages native Catalyst Center APIs for data retrieval

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.dnac collection | 6.49.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center | 2.3.7.9+ |
| dnacentersdk | 2.10.10+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac    # >= 6.49.0
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center admin credentials
- Network connectivity to Catalyst Center API
- Wireless infrastructure deployed and configured
- Existing wireless network profiles in Catalyst Center

---

## Workflow Structure

```
network_profile_wireless_playbook_config_generator/
├── playbook/
│   └── network_profile_wireless_playbook_config_generator_playbook.yml   # Main operations
├── vars/
│   └── network_profile_wireless_playbook_config_generator_inputs.yml     # Configuration examples
├── schema/
│   └── network_profile_wireless_playbook_config_generator_schema.yml     # Input validation
└── README.md                                                
```

---

## Schema Parameters

### Basic Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| generate_all_configurations | boolean | No | false | Generate all wireless profiles automatically |
| file_path | string | No | auto-generated | Output file path for YAML configuration |
| file_mode | string | No | overwrite | File write mode — `overwrite` replaces the file, `append` adds to it |
| global_filters | dict | No | None | Filters to specify which profiles to include |

### Global Filters (Priority-Based)

The module implements a strict filter priority system. Only the **HIGHEST priority filter** with valid data will be processed.

| Filter | Priority | Type | Description |
|--------|----------|------|-------------|
| profile_name_list | 1 (HIGHEST) | list | List of exact wireless profile names |
| day_n_template_list | 2 | list | Filter by Day-N template names |
| site_list | 3 | list | Filter by site hierarchy paths |
| ssid_list | 4 | list | Filter by SSID names |
| ap_zone_list | 5 | list | Filter by AP zone names |
| feature_template_list | 6 | list | Filter by feature template names |
| additional_interface_list | 7 (LOWEST) | list | Filter by interface names |

**Important Notes:**
- All filter values are **case-sensitive** and require **exact matches**
- Empty filter lists are treated as "not provided"
- Only ONE filter type is processed per execution
- If no filters are provided and `generate_all_configurations` is false, the module will fail

---

## Getting Started

### Step 1: Install Prerequisites

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Step 2: Configure Inventory

Edit `inventory/demo_lab/hosts.yml`:

```yaml
catalyst_center_hosts:
  hosts:
    catalyst_center_primary:
      catalyst_center_host: 10.0.0.0
      catalyst_center_username: admin
      catalyst_center_password: "password"
      catalyst_center_version: "2.3.7.9"
```

### Step 3: Configure Variables

Edit `workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml`:

```yaml
network_profile_wireless_config:
  - generate_all_configurations: true
    file_path: "network_profile_wireless/complete_wireless_config.yml"
```

### Step 4: Validate Configuration

```bash
./tools/validate.sh -s workflows/network_profile_wireless_playbook_config_generator/schema/network_profile_wireless_playbook_config_generator_schema.yml \
     -d workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml
```

### Step 5: Execute Playbook

The playbook supports two input methods:

#### Option A: Vars file input (recommended for version-controlled configs)

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/network_profile_wireless_playbook_config_generator/playbook/network_profile_wireless_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=/absolute/path/to/dnac_ansible_workflows/workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml \
  -vvvv
```

#### Option B: Inventory / host variable input

Omit `VARS_FILE_PATH` and define `network_profile_wireless_config` directly as a host variable in your inventory file or in `host_vars`/`group_vars`.

**Example inventory snippet (`inventory/demo_lab/hosts.yaml`):**

```yaml
catalyst_center_hosts:
  hosts:
    catalyst_center_primary:
      catalyst_center_host: "{{ lookup('ansible.builtin.env', 'HOSTIP') }}"
      catalyst_center_password: "{{ lookup('ansible.builtin.env', 'CATALYST_CENTER_PASSWORD') }}"
      catalyst_center_port: 443
      catalyst_center_username: "{{ lookup('ansible.builtin.env', 'CATALYST_CENTER_USERNAME') }}"
      catalyst_center_verify: false
      catalyst_center_version: 2.3.7.9

      # Workflow data defined as host variables
      network_profile_wireless_config:
        - generate_all_configurations: true
          file_path: "/tmp/complete_wireless_profiles.yml"
```

Then run **without** `VARS_FILE_PATH`:

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/network_profile_wireless_playbook_config_generator/playbook/network_profile_wireless_playbook_config_generator_playbook.yml \
  -vvvv
```

The playbook auto-detects the input source and prints it at the start:
- `Input source: vars file <path>` when using Option A
- `Input source: inventory / host variables (VARS_FILE_PATH not provided)` when using Option B

> **Note:** When `VARS_FILE_PATH` is provided, it takes **precedence** over inventory variables.

### Workflow Execution

The workflow follows these steps:

1. **Load input** from `VARS_FILE_PATH` (if provided) or fall back to inventory / host variables
2. **Connect** to Catalyst Center using provided credentials
3. **Extract** `file_path` and `file_mode` as top-level module parameters; pass `global_filters` inside `config`
4. **Omit** `config` entirely when `generate_all_configurations: true` (module runs in full auto-discovery mode)
5. **Retrieve** existing wireless network profiles via API calls
6. **Filter** profiles based on specified criteria and priority
7. **Extract** associated components (SSIDs, AP zones, templates, interfaces)
8. **Transform** API responses into Ansible-compatible format
9. **Generate** YAML configuration file with proper structure
10. **Write** output to specified file path using configured `file_mode`

---

## Operations

### Generate Operations (state: gathered)

Use `network_profile_wireless_playbook_config_generator_playbook.yml` for generating YAML playbook configuration operations.

#### Generate All Configurations

**Description**: Retrieves all wireless network profiles from Catalyst Center regardless of any filters.

```yaml
generate_config:
  generate_all_true:
    - generate_all_configurations: true
      file_path: "network_profile_wireless/complete_wireless_infrastructure.yml"
```

#### Profile Name Based Generation (Priority 1 - HIGHEST)

**Description**: Extract specific wireless profiles by exact name. Most efficient method.

```yaml
generate_config:
  profile_name_filter:
    - file_path: "network_profile_wireless/specific_profiles.yml"
      global_filters:
        profile_name_list:
          - "Campus_Wireless_Profile"
          - "nw_profile_1"
```

#### Day-N Template Based Generation (Priority 2)

**Description**: Extract profiles containing specific Day-N templates.

```yaml
generate_config:
  day_n_template_filter:
    - file_path: "network_profile_wireless/dayn_template_profiles.yml"
      global_filters:
        day_n_template_list: ["Ans Wireless DayN 1"]
```

#### Site Based Generation (Priority 3)

**Description**: Extract profiles assigned to specific sites.

```yaml
generate_config:
  site_list_filter:
    - file_path: "network_profile_wireless/site_profiles.yml"
      global_filters:
        site_list: ["Global/USA/SAN JOSE/SJ_BLD20/FLOOR3"]
```

#### SSID Based Generation (Priority 4)

**Description**: Extract profiles containing specific SSIDs.

```yaml
generate_config:
  ssid_list_filter:
    - file_path: "network_profile_wireless/ssid_profiles.yml"
      global_filters:
        ssid_list: ["GUEST", "associate_profile_1"]
```

#### AP Zone Based Generation (Priority 5)

**Description**: Extract profiles containing specific AP zones.

```yaml
generate_config:
  ap_zone_list_filter:
    - file_path: "network_profile_wireless/ap_zone_profiles.yml"
      global_filters:
        ap_zone_list: ["AP_Zone_North"]
```

#### Feature Template Based Generation (Priority 6)

**Description**: Extract profiles with specific feature templates.

```yaml
generate_config:
  feature_template_list_filter:
    - file_path: "network_profile_wireless/feature_template_profiles.yml"
      global_filters:
        feature_template_list: ["Default Dot11ax 6-GHz Design"]
```

#### Interface Based Generation (Priority 7 - LOWEST)

**Description**: Extract profiles with specific additional interfaces.

```yaml
generate_config:
  additional_interface_list_filter:
    - file_path: "network_profile_wireless/interface_profiles.yml"
      global_filters:
        additional_interface_list: ["temp_20", "VLAN_22"]
```

**Validate and Execute:**

```bash
# Validate
./tools/validate.sh -s workflows/network_profile_wireless_playbook_config_generator/schema/network_profile_wireless_playbook_config_generator_schema.yml \
                   -d workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml
```

Return result validate:

```bash
(pyats-syedkahm) [syedkahm@st-ds-4 dnac_ansible_workflows]$ ./tools/validate.sh -s workflows/network_profile_wireless_playbook_config_generator/schema/network_profile_wireless_playbook_config_generator_schema.yml \
>                    -d workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml
workflows/network_profile_wireless_playbook_config_generator/schema/network_profile_wireless_playbook_config_generator_schema.yml
workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml
yamale   -s workflows/network_profile_wireless_playbook_config_generator/schema/network_profile_wireless_playbook_config_generator_schema.yml  workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml
Validating workflows/network_profile_wireless_playbook_config_generator/vars/network_profile_wireless_playbook_config_generator_inputs.yml...
Validation success! 👍
```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/network_profile_wireless_playbook_config_generator/playbook/network_profile_wireless_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/network_profile_wireless_playbook_config_generator_inputs.yml
```

Expected Terminal Output:

1. **Generate All Configurations**

```code
TASK [Generate YAML configuration for network profile wireless] ****
ok: [catalyst_center_primary] => (item={'generate_all_configurations': True, 'file_path': 'network_profile_wireless/generate_all_true.yml'})
{
    "changed": false,
    "config": {
        "file_path": "network_profile_wireless/generate_all_true.yml",
        "generate_all_configurations": true
    },
    "msg": "YAML configuration file generated successfully for module 'network_profile_wireless_workflow_manager'",
    "response": {
        "profiles_processed": 5,
        "file_path": "network_profile_wireless/generate_all_true.yml",
        "message": "YAML configuration file generated successfully",
        "status": "success"
    },
    "status": "success"
}
```

2. **Profile Name Filter**

```code
TASK [Generate YAML configuration for network profile wireless] ****
ok: [catalyst_center_primary] => (item={'file_path': 'network_profile_wireless/profile_name_filter.yml', 'global_filters': {'profile_name_list': ['Campus_Wireless_Profile', 'nw_profile_1']}})
{
    "changed": false,
    "config": {
        "file_path": "network_profile_wireless/profile_name_filter.yml",
        "global_filters": {
            "profile_name_list": ["Campus_Wireless_Profile", "nw_profile_1"]
        }
    },
    "msg": "YAML configuration file generated successfully for module 'network_profile_wireless_workflow_manager'",
    "response": {
        "profiles_processed": 2,
        "filter_used": "profile_name_list",
        "file_path": "network_profile_wireless/profile_name_filter.yml",
        "message": "YAML configuration file generated successfully",
        "status": "success"
    },
    "status": "success"
}
```

3. **SSID Filter**

```code
TASK [Generate YAML configuration for network profile wireless] ****
ok: [catalyst_center_primary] => (item={'file_path': 'network_profile_wireless/ssid_list_filter.yml', 'global_filters': {'ssid_list': ['GUEST', 'associate_profile_1']}})
{
    "changed": false,
    "config": {
        "file_path": "network_profile_wireless/ssid_list_filter.yml",
        "global_filters": {
            "ssid_list": ["GUEST", "associate_profile_1"]
        }
    },
    "msg": "YAML configuration file generated successfully for module 'network_profile_wireless_workflow_manager'",
    "response": {
        "profiles_processed": 3,
        "filter_used": "ssid_list",
        "file_path": "network_profile_wireless/ssid_list_filter.yml",
        "message": "YAML configuration file generated successfully",
        "status": "success"
    },
    "status": "success"
}
```

---

## Examples

### Example 1: Generate ALL Wireless Profiles

Extract complete wireless infrastructure for migration or audit.

```yaml
generate_config:
  generate_all_true:
    - generate_all_configurations: true
      file_path: "network_profile_wireless/complete_wireless_infrastructure.yml"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `generate_all_configurations: true` is used:

```yaml
---
config:
- profile_name: nw_profile_2
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
- profile_name: nw_profile_1
  ssid_details:
  - ssid_name: associate_profile_1
    dot11be_profile_name: test_802.11be
    enable_fabric: false
    interface_name: test_interface
    anchor_group_name: test_anchor_group
```

### Example 2: Extract Specific Profiles by Name (Highest Priority)

Extract only known profiles for targeted configuration.

```yaml
generate_config:
  profile_name_filter:
    - file_path: "network_profile_wireless/production_profiles.yml"
      global_filters:
        profile_name_list:
          - "Campus_Wireless_Profile"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `profile_name_list` filter is used with specific profile names:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only the specified profile (`Campus_Wireless_Profile`) is extracted. The profile includes all its associated components: Day-N templates, site assignments, SSID details, additional interfaces, AP zones, and feature template designs.

**Use Case**: Backup specific profiles, targeted migration, critical profile documentation

---

### Example 3: Extract Profiles by Day-N Templates

Find all profiles using specific operational configurations.

```yaml
generate_config:
  day_n_template_filter:
    - file_path: "network_profile_wireless/controller_config_profiles.yml"
      global_filters:
        day_n_template_list: 
          - "Ans Wireless DayN 1"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `day_n_template_list` filter is used:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only profiles containing the Day-N template `Ans Wireless DayN 1` are extracted. The complete profile configuration is included in the output.

**Use Case**: Operational template tracking, configuration compliance audit

---

### Example 4: Extract Profiles by Site

Extract wireless configurations for specific locations.

```yaml
generate_config:
  site_list_filter:
    - file_path: "network_profile_wireless/campus_profiles.yml"
      global_filters:
        site_list: 
          - "Global/USA/SAN JOSE/SJ_BLD20/FLOOR3"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `site_list` filter is used:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only profiles assigned to the site `Global/USA/SAN JOSE/SJ_BLD20/FLOOR3` are extracted. The output includes the complete profile configuration with all associated site assignments.

**Use Case**: Site-specific configuration, regional wireless audit, campus documentation

---

### Example 5: Track SSID Usage Across Profiles

Find all profiles providing specific wireless networks.

```yaml
generate_config:
  ssid_list_filter:
    - file_path: "network_profile_wireless/guest_network_profiles.yml"
      global_filters:
        ssid_list: 
          - "GUEST"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `ssid_list` filter is used:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only profiles containing the SSID `GUEST` are extracted. The complete profile configuration is included, showing all SSIDs, AP zones, and other components associated with the matching profiles.

**Use Case**: Guest network tracking, SSID usage audit, network segmentation analysis

---

### Example 6: Extract Profiles by AP Zones

Zone-specific configuration management.

```yaml
generate_config:
  ap_zone_list_filter:
    - file_path: "network_profile_wireless/regional_zones.yml"
      global_filters:
        ap_zone_list: 
          - "AP_Zone_North"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `ap_zone_list` filter is used:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only profiles containing the AP zone `AP_Zone_North` are extracted. The full profile configuration is included with all associated components.

**Use Case**: AP zone configuration, coverage area tracking, regional deployment

---

### Example 7: Feature Template Based Extraction

Extract profiles with specific wireless features.

```yaml
generate_config:
  feature_template_list_filter:
    - file_path: "network_profile_wireless/advanced_features.yml"
      global_filters:
        feature_template_list: 
          - "Default Dot11ax 6-GHz Design"
```

**Sample Generated Output**:

Below is a sample YAML configuration file generated by the module when `feature_template_list` filter is used:

```yaml
---
config:
- profile_name: Campus_Wireless_Profile
  day_n_templates:
  - Ans Wireless DayN 1
  site_names:
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR3
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR2
  - Global/USA/SAN JOSE/SJ_BLD20/FLOOR4
  ssid_details:
  - ssid_name: GUEST
    dot11be_profile_name: Ans NP WL BE 1
    enable_fabric: false
    vlan_group_name: Ans_NP_WL_INT_group_1
  additional_interfaces:
  - interface_name: temp_20
    vlan_id: 20
  - interface_name: VLAN_22
    vlan_id: 22
  ap_zones:
  - ap_zone_name: AP_Zone_North
    ssids:
    - GUEST
    rf_profile_name: HIGH
  feature_template_designs:
  - feature_templates:
    - Default Dot11ax 6-GHz Design
  - feature_templates:
    - Default CleanAir 6GHz Design
```

> **Note:** Only profiles containing the feature template `Default Dot11ax 6-GHz Design` are extracted. The complete profile is included with all feature template designs and other associated components.

**Use Case**: Feature deployment tracking, advanced configuration audit

---

### Example 8: Interface Based Filtering

Extract profiles using specific interfaces.

```yaml
generate_config:
  additional_interface_list_filter:
    - file_path: "network_profile_wireless/interface_tracking.yml"
      global_filters:
        additional_interface_list: 
          - "temp_20"
          - "VLAN_22"
          - "management_interface"
```

**Use Case**: Interface configuration audit, VLAN tracking

---

### Example 9: Multiple Generation Requests

Generate multiple configuration files with different filters in one execution.

```yaml
generate_config:
  multiple_generations:
    - file_path: "network_profile_wireless/campus_profiles.yml"
      global_filters:
        profile_name_list: ["Campus_Wireless_Profile"]
    - file_path: "network_profile_wireless/guest_networks.yml"
      global_filters:
        ssid_list: ["GUEST"]
    - file_path: "network_profile_wireless/all_profiles.yml"
      generate_all_configurations: true
```

**Use Case**: Comprehensive extraction, multiple documentation needs, varied filtering requirements

---

### Example 10: Generate All Overriding Filters

When `generate_all_configurations` is true, all filters are ignored.

```yaml
generate_config:
  generate_all_over_filters:
    - generate_all_configurations: true
      file_path: "network_profile_wireless/all_profiles_ignore_filters.yml"
      global_filters:
        profile_name_list: ["Campus_Wireless_Profile"]  # IGNORED
```

**Use Case**: Complete extraction while keeping filter configuration for reference

---

### Example 11: Auto-Generated File Path

Omit `file_path` for automatic timestamped filename.

```yaml
generate_config:
  generate_all_default_path:
    - generate_all_configurations: true
```

**Generated Filename**: `network_profile_wireless_workflow_manager_playbook_2026-02-19_14-30-45.yml`

**Use Case**: Quick extractions, preventing accidental overwrites

---

### Example 12: Validation Test (Should Fail)

Configuration without filters and `generate_all_configurations: false` will fail.

```yaml
generate_config:
  generate_all_false_no_global_params:
    - generate_all_configurations: false
      file_path: "network_profile_wireless/invalid_config.yml"
```

**Expected Result**: Module fails with error message requiring at least one filter

---

## Filter Priority System

### Priority Hierarchy (Highest to Lowest)

1. **profile_name_list** (HIGHEST) - Direct profile targeting
2. **day_n_template_list** - Operational template filtering
3. **site_list** - Location-based filtering
4. **ssid_list** - Wireless network filtering
5. **ap_zone_list** - Zone-based filtering
6. **feature_template_list** - Feature-based filtering
7. **additional_interface_list** (LOWEST) - Interface-based filtering

### Filter Processing Rules

```
IF profile_name_list has data:
    USE profile_name_list
    IGNORE all other filters
ELSE IF day_n_template_list has data:
    USE day_n_template_list
    IGNORE lower priority filters
ELSE IF site_list has data:
    USE site_list
    IGNORE lower priority filters
[... continues for each priority level ...]
ELSE IF generate_all_configurations is true:
    EXTRACT all profiles
ELSE:
    FAIL with error message
```

### Important Considerations

- ✅ **Only ONE filter type** is processed per execution
- ✅ **Empty lists** (`profile_name_list: []`) are treated as "not provided"
- ✅ **Case-sensitive matching** - filter values must match exactly
- ✅ **Validation occurs** before API calls to fail fast
- ❌ **No partial matching** or wildcards supported
- ❌ **No combining filters** from different priority levels

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "No configurations or components to process"

**Cause**: Neither `generate_all_configurations: true` nor valid global_filters provided

**Solution**: Provide at least one filter with data or set `generate_all_configurations: true`

```yaml
# ❌ WRONG - Will fail
generate_config:
  test:
    - file_path: "output.yml"

# ✅ CORRECT
generate_config:
  test:
    - file_path: "output.yml"
      generate_all_configurations: true
```

---

#### Issue 2: "Profile 'XYZ' not found in Catalyst Center"

**Cause**: Profile name in `profile_name_list` doesn't exist or has typo

**Solution**: 
1. Verify profile name in Catalyst Center UI
2. Check for case sensitivity
3. Use exact profile name

```yaml
# ❌ WRONG - Case mismatch
global_filters:
  profile_name_list: ["campus_wireless_profile"]

# ✅ CORRECT - Exact match
global_filters:
  profile_name_list: ["Campus_Wireless_Profile"]
```

---

#### Issue 3: Empty Output Generated

**Cause**: Filter criteria matched no profiles

**Solution**:
1. Verify filter values are correct (case-sensitive)
2. Check if profiles with specified criteria exist
3. Use `generate_all_configurations: true` to see all available profiles

```yaml
# Diagnostic run - see all profiles
generate_config:
  diagnostic:
    - generate_all_configurations: true
      file_path: "diagnostic_all_profiles.yml"
```

---

#### Issue 4: "Catalyst Center version not supported"

**Cause**: Catalyst Center version is below 2.3.7.9

**Solution**: Upgrade Catalyst Center to version 2.3.7.9 or higher

---

#### Issue 5: Filter Not Being Applied

**Cause**: Higher priority filter has data, overriding lower priority filter

**Solution**: Remove or empty higher priority filters

```yaml
# ❌ WRONG - site_list will be ignored
global_filters:
  profile_name_list: ["Profile1"]  # Priority 1
  site_list: ["Global/USA/HQ"]     # Priority 3 - IGNORED

# ✅ CORRECT - Only use desired filter
global_filters:
  site_list: ["Global/USA/HQ"]
```

---

#### Issue 6: Permission Denied Writing File

**Cause**: Insufficient permissions for specified file_path

**Solution**: 
1. Verify directory permissions
2. Use writable directory path
3. Ensure parent directories exist or will be created

```yaml
# Use temporary directory with guaranteed write access
generate_config:
  test:
    - file_path: "/tmp/wireless_profiles.yml"
      generate_all_configurations: true
```

---

#### Issue 7: API Timeout

**Cause**: Large number of profiles or slow network

**Solution**: Increase API timeout in playbook or inventory

```yaml
# In inventory or playbook vars
catalyst_center_api_task_timeout: 3600  # Increase to 60 minutes
```

---

### Debug Mode

Enable debug mode for detailed execution information:

```yaml
# In inventory file
catalyst_center_debug: true
catalyst_center_log: true
catalyst_center_log_level: "DEBUG"
catalyst_center_log_file_path: "/tmp/catalyst_center_debug.log"
```

---

## Generated Output Structure

The generated YAML file will be compatible with `network_profile_wireless_workflow_manager` module:

```yaml
config:
  - profile_name: "Campus_Wireless_Profile"
    sites:
      - "Global/USA/SAN JOSE/SJ_BLD20/FLOOR3"
      - "Global/USA/California/San_Francisco/HQ"
    ssid_details:
      - ssid_name: "Corporate_WiFi"
        ssid_type: "Enterprise"
        enable_fabric: true
        flex_connect:
          enable_flex_connect: true
          local_to_vlan: 100
        interface_name: "management"
        wlan_profile_name: "Corporate_Profile"
    ap_zones:
      - zone_name: "AP_Zone_North"
        ap_count: 25
    feature_templates:
      - template_name: "Default Dot11ax 6-GHz Design"
        template_id: "uuid-here"
    day_n_template:
      - template_name: "Ans Wireless DayN 1"
        template_id: "uuid-here"
    additional_interfaces:
      - interface_name: "VLAN_22"
        vlan_id: 22
```

---

## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://dnacentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Wireless Network Profile Configuration Guide](https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_ug_2_3_7.html)

---