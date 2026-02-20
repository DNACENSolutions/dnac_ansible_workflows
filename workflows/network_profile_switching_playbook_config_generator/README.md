# Brownfield Network Profile Switch Playbook Config Generator

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

The Brownfield Network Profile Switch playbook config generator automates the creation of YAML playbook configurations for existing switch profiles deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing switch profile infrastructure.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `playbooks` module.
Extract existing switch profiles and associated configurations from your Cisco Catalyst Center.
Convert them into properly formatted YAML files.
Generate files that are ready to use with Ansible automation.
- **Profile Filtering**: Selective generation based on profile names, Day-N templates, or site assignments
- **Priority-based Filtering**: Intelligent filter precedence (Profile Names > Day-N Templates > Sites)
- **Flexible Output**: Configurable file paths and naming conventions with timestamp support
- **Brownfield Support**: Extract configurations from existing Catalyst Center deployments
- **API Integration**: Leverages native Catalyst Center APIs for data retrieval

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 6.42.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center SDK | 2.9.3+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center admin credentials
- Network connectivity to Catalyst Center API
- Switch profile infrastructure deployed and configured
- Existing switch profiles with associated templates and configurations

---

## Workflow Structure

```
network_profile_switching_playbook_config_generator/
├── playbook/
│   └── network_profile_switching_playbook_config_generator_playbook.yml   # Main operations
├── vars/
│   ├── network_profile_switching_playbook_config_generator_inputs.yml     # Configuration examples
├── schema/
│   └── network_profile_switching_playbook_config_generator_schema.yml     # Input validation
└── README.md                                                
```

---

## Schema Parameters

### Basic Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| generate_all_configurations | boolean | No | false | Generate all switch profiles automatically |
| file_path | string | No | auto-generated | Output file path for YAML configuration file |
| global_filters | dict | No | none | Filters to specify which switch profiles to include |

### Global Filtering (Priority Order)

| Parameter      | Type | Required | Priority | Description |
|--------------|------|----------|-------------|-----------|
| profile_name_list | list | No | **HIGHEST** | List of specific switch profile names to extract |
| day_n_template_list      | list | No | **MEDIUM**| List of Day-N templates to filter switch profiles |
| site_list | list | No | **LOWEST**| List of site hierarchies to filter switch profiles |

### Filter Specifications

#### Profile Name List
- **Type**: List of strings
- **Case-sensitive**: Must match exact profile names in Catalyst Center
- **Example**: `["Campus_Switch_Profile", "Enterprise_Switch_Profile"]`
- **Behavior**: Module will fail if any specified profile doesn't exist

#### Day-N Template List
- **Type**: List of strings
- **Case-sensitive**: Must match exact template names
- **Example**: `["Periodic_Config_Audit", "Security_Compliance_Check"]`
- **Behavior**: Returns all profiles containing any of the specified templates

#### Site List
- **Type**: List of strings
- **Case-sensitive**: Must match exact site hierarchy paths
- **Example**: `["Global/India/Chennai/Main_Office", "Global/USA/San_Francisco/Regional_HQ"]`
- **Behavior**: Returns all profiles assigned to any of the specified sites

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
```

### Step 3: Configure Variables

Edit `workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml`:

```yaml
brownfield_network_profile_switch_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_switch_profiles_config.yml"
```

### Step 4: Validate Configuration

```bash
./tools/validate.sh -s workflows/network_profile_switching_playbook_config_generator/schema/network_profile_switching_playbook_config_generator_schema.yml \
     -d workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml
```

### Step 5: Execute Playbook

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/network_profile_switching_playbook_config_generator/playbook/network_profile_switching_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/network_profile_switching_playbook_config_generator_inputs.yml
```

### Workflow Execution

The workflow follows these steps:

1. **Connect** to Catalyst Center using provided credentials
2. **Retrieve** existing switch profiles and associated configurations via API calls
3. **Filter** switch profiles based on specified criteria and priority
4. **Transform** API responses into Ansible-compatible format
5. **Generate** YAML configuration file with proper structure
6. **Validate** output file format and content

---

## Operations

### Generate Operations (state: gathered)

Use `network_profile_switching_playbook_config_generator_playbook.yml` for generating YAML playbook configuration operations.

#### Generate All Configurations

**Description**: Retrieves all switch profiles and configurations from Catalyst Center regardless of any filters.

```yaml
brownfield_network_profile_switch_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_switch_profiles_config.yml"
```

#### Profile Name Based Generation

**Description**: Generates configuration for specific switch profiles only.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/specific_switch_profiles_config.yml"
    global_filters:
      profile_name_list:
        - "Campus_Switch_Profile"
        - "Enterprise_Switch_Profile"
```

#### Day-N Template Based Generation

**Description**: Generates configuration for switch profiles containing specific Day-N templates.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/template_based_switch_profiles_config.yml"
    global_filters:
      day_n_template_list:
        - "Periodic_Config_Audit"
        - "Security_Compliance_Check"
```

#### Site Based Generation

**Description**: Generates configuration for switch profiles assigned to specific sites.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/site_based_switch_profiles_config.yml"
    global_filters:
      site_list:
        - "Global/USA/SAN JOSE/SJ_BLD21/FLOOR1"
        - "Global/India/Chennai/Main_Office"
```

**Validate and Execute:**

```bash
# Validate
./tools/validate.sh -s workflows/network_profile_switching_playbook_config_generator/schema/network_profile_switching_playbook_config_generator_schema.yml \
                   -d workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml
```
**Return result validate:**
```bash
(pyats-priya) [pbalaku2@st-ds-4 dnac_ansible_workflows]$ ./tools/validate.sh -s workflows/network_profile_switching_playbook_config_generator/schema/network_profile_switching_playbook_config_generator_schema.yml \
>                    -d workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml
workflows/network_profile_switching_playbook_config_generator/schema/network_profile_switching_playbook_config_generator_schema.yml
workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml
yamale   -s workflows/network_profile_switching_playbook_config_generator/schema/network_profile_switching_playbook_config_generator_schema.yml  workflows/network_profile_switching_playbook_config_generator/vars/network_profile_switching_playbook_config_generator_inputs.yml
Validating workflows/brownfield_network_profile_switch/vars/brownfield_network_profile_switch_inputs.yml...
Validation success! 👍
```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/network_profile_switching_playbook_config_generator/playbook/network_profile_switching_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/network_profile_switching_playbook_config_generator_inputs.yml
```

**Expected Terminal Output:**

1. **Generate All Configurations**

```code
        file_path: /tmp/complete_switch_profiles_config.yml
        generate_all_configurations: true
   msg: 
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/complete_switch_profiles_config.yml
      response:
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/complete_switch_profiles_config.yml
      status: success
```

2. **Profile Name Based Generation:**

```code
        global_filters:
          profile_name_list:
          - Campus_Switch_Profile
          - Enterprise_Switch_Profile
        file_path: /tmp/specific_switch_profiles_config.yml
      msg: 
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/specific_switch_profiles_config.yml
      response:
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/specific_switch_profiles_config.yml
      status: success
```

3. **Day-N Template Based Generation:**

```code
        global_filters:
          day_n_template_list:
          - Periodic_Config_Audit
        file_path: /tmp/template_based_switch_profiles_config.yml
      msg: 
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/template_based_switch_profiles_config.yml
      response:
        YAML config generation Task succeeded for module 'network_profile_switching'.:
          file_path: /tmp/template_based_switch_profiles_config.yml
      status: success
```
---

## Examples

### Example 1: Generate ALL switch profiles

```yaml
brownfield_network_profile_switch_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_switch_infrastructure.yml"
```

### Example 2: Specific Profile Names

Extract configurations for specific switch profiles by name.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/campus_enterprise_profiles.yml"
    global_filters:
      profile_name_list:
        - "Test Profile BF1"
        - "Test Profile BF2"
```

### Example 3: Day-N Template Based Filtering

Extract all switch profiles that use specific Day-N templates.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/audit_template_profiles.yml"
    global_filters:
      day_n_template_list:
        - "Ans Switch DayN 2"
        - "static_host_onboarding_template"
```

### Example 4: Site-Based Filtering

Extract switch profiles assigned to specific sites.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/site_specific_profiles.yml"
    global_filters:
      site_list:
        - "Global/USA/SAN JOSE/SJ_BLD21/FLOOR1"
        - "Global/USA/SAN JOSE/SJ_BLD23/FLOOR2"
```

### Example 5: Multiple Generation Tasks

```yaml
brownfield_network_profile_switch_config:
  # Generate all configurations
  - generate_all_configurations: true
    file_path: "/tmp/all_switch_profiles.yml"
  
  # Generate specific profiles
  - file_path: "/tmp/campus_profiles_only.yml"
    global_filters:
      profile_name_list:
        - "Campus_Switch_Profile"
  
  # Generate by template
  - file_path: "/tmp/security_template_profiles.yml"
    global_filters:
      day_n_template_list:
        - "Ans Switch DayN 2"
        - "static_host_onboarding_template"
```

### Example 6: Auto-generated File Path

When no file path is specified, the module auto-generates a timestamped filename.

```yaml
brownfield_network_profile_switch_config:
  - global_filters:
      profile_name_list:
        - "Test Profile BF1"
        - "Test Profile BF2"
# Output: playbooks_config_2026-02-19_14-30-45.yml
```

### Example 7: Filter Priority Demonstration

Only the highest priority filter with data will be processed.

```yaml
brownfield_network_profile_switch_config:
  - file_path: "/tmp/priority_example.yml"
    global_filters:
      # This will be used (HIGHEST PRIORITY)
      profile_name_list:
        - "Campus_Switch_Profile"
      # These will be IGNORED
      day_n_template_list:
        - "Some_Template"
      site_list:
        - "Some/Site/Path"
```

### Example 8: Complete Configuration with Error Handling

```yaml
brownfield_network_profile_switch_config:
  # Primary generation task
  - file_path: "/tmp/production_switch_profiles.yml"
    global_filters:
      profile_name_list:
        - "Test Profile BF1"
        - "Test Profile BF2"
  
  # Backup generation task with templates
  - file_path: "/tmp/template_based_backup.yml"
    global_filters:
      day_n_template_list:
        - "Ans Switch DayN 2"
        - "static_host_onboarding_template"
  
  # Site-specific generation for branch offices
  - file_path: "/tmp/branch_office_profiles.yml"
    global_filters:
      site_list:
        - "Global/USA/SAN JOSE/SJ_BLD21/FLOOR1"
        - "Global/USA/SAN JOSE/SJ_BLD23/FLOOR2"
```

---

## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://dnacentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Playbooks Module](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/)