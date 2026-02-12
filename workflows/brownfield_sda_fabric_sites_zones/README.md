# Brownfield SDA Fabric Sites and Zones Playbook Generator

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

The Brownfield SDA Fabric Sites and Zones Configuration Generator automates the creation of YAML playbook configurations for existing fabric sites and zones deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing infrastructure.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `sda_fabric_sites_zones_workflow_manager` module.
Extract existing SDA fabric sites and zones configurations from your Cisco Catalyst Center
Convert them into properly formatted YAML files.
Generate files that are ready to use with Ansible automation.
- **Component Filtering**: Selective generation of fabric sites, fabric zones, or both components
- **Flexible Output**: Configurable file paths and naming conventions
- **Brownfield Support**: Extract configurations from existing Catalyst Center deployments
- **API Integration**: Leverages native Catalyst Center APIs for data retrieval
- **Authentication Profiles**: Includes authentication profile configurations for sites and zones

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 6.42.0+ |
| Python | 3.9+ |
| Cisco Catalyst Center SDK | 2.3.7.9+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center admin credentials with SDA fabric read permissions
- Network connectivity to Catalyst Center API
- Firewall rules for HTTPS (443) and SSH (22) if needed
- SDA fabric sites and zones must be pre-configured in Catalyst Center

---

## Workflow Structure

```
brownfield_sda_fabric_sites_zones/
├── playbook/
│   └── brownfield_sda_fabric_sites_zones_playbook.yml    # Main configuration generator
├── vars/
│   └── brownfield_sda_fabric_sites_zones_input.yml       # Input parameters and examples
├── schema/
│   └── brownfield_sda_fabric_sites_zones_schema.yml      # Configuration validation
└── README.md
```

---

## Schema Parameters

### Configuration Generator Parameters

| Parameter | Type    | Required | Default        | Description |
|---------|---------|----------|--------------------|---------------------------|
| generate_all_configurations | boolean | No       | false          | Generate all components regardless of filters |
| file_path                   | string  | No       | auto-generated | Output path for YAML configuration file       |
| component_specific_filters  | dict    | No       | all components | Filters to specify which components to include|

### Component Specific Filters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| components_list | list | No | ["fabric_sites", "fabric_zones"] | List of components to include in generation |
| fabric_sites | list | No | all sites | Filter fabric sites by specific criteria |
| fabric_zones | list | No | all zones | Filter fabric zones by specific criteria |

### Component Filter Options

| Component | Valid Values | Description |
|-----------|-------------|-------------|
| components_list | "fabric_sites" | Include only fabric sites in generation |
| components_list | "fabric_zones" | Include only fabric zones in generation |
| components_list | ["fabric_sites", "fabric_zones"] | Include both sites and zones |

### Fabric Sites Sub-Filter Parameters

| Parameter          | Type  | Required | Default | Description |
|--------------------|------  |----------|---------|-------------|
| site_name_hierarchy | string | Yes     | N/A     | Full hierarchical site path to filter specific fabric site |

**Examples**:
- `"Global/USA/San Jose"` - Filters fabric site at San Jose location
- `"Global/Test_Fabric"` - Filters fabric site named Test_Fabric
- `"Global/Area/Building1"` - Filters fabric site at Building1

### Fabric Zones Sub-Filter Parameters

| Parameter           | Type  | Required | Default | Description |
|---------------------|-------|----------|---------|-------------|
| site_name_hierarchy | string| Yes      | N/A     | Full hierarchical zone path to filter specific fabric zone |

**Examples**:
- `"Global/USA/San Jose/Building1/Zone1"` - Filters fabric zone Zone1 in Building1
- `"Global/Test_Fabric/Bld1"` - Filters fabric zone Bld1 in Test_Fabric
- `"Global/Area/Building1/Floor2"` - Filters fabric zone Floor2 in Building1

### Generated Output Structure

The generated YAML file will contain:

```yaml
config:
  - fabric_sites:
      - site_name_hierarchy: "Global/Site_Name"
        fabric_type: "fabric_site"
        is_pub_sub_enabled: false
        authentication_profile: "Closed Authentication"
      - site_name_hierarchy: "Global/Site_Name/Zone_Name"
        fabric_type: "fabric_zone"
        authentication_profile: "Closed Authentication"
```

---

## Getting Started

### Quick Start

1. **Install Prerequisites**
```bash
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install ansible.utils
pip install dnacentersdk
pip install yamale
   ```

2. **Configure Inventory**
   Edit `inventory/hosts.yml` with your Catalyst Center details:
   ```yaml
   catalyst_center_hosts:
     hosts:
       catalyst_center:
         catalyst_center_host: "10.0.0.0"
         catalyst_center_username: "admin"
         catalyst_center_password: "password"
   ```

3. **Configure Variables**

Edit `workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml`:

```yaml
brownfield_sda_fabric_sites_zones_config:
  # Generate all SDA fabric sites and zones with custom file path
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_fabric_sites_zones_config.yaml"
    component_specific_filters:
      components_list: ["fabric_sites", "fabric_zones"]
   
  - generate_all_configurations: true
    file_path: "/tmp/sda_fabric_sites_zones_components_config1.yaml"
      
  - generate_all_configurations: false
    file_path: "/tmp/sda_fabric_sites_zones_components_config_false.yaml"
    
  #Generate only fabric sites 
  - file_path: "/tmp/sda_fabric_sites_zones_components_config2.yaml"
    component_specific_filters:
      components_list: ["fabric_sites"]

```

4. **Validate Configuration**

```bash
./tools/validate.sh -s workflows/brownfield_sda_fabric_sites_zones/schema/brownfield_sda_fabric_sites_zones_schema.yml \
     -d workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml
```

5. **Execute Playbook**

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
 workflows/brownfield_sda_fabric_sites_zones/playbook/brownfield_sda_fabric_sites_zones_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/brownfield_sda_fabric_sites_zones_input.yml
```

the creation of YAML playbook configurations for existing fabric sites and zones deployed in Cisco Catalyst Center.


### Workflow Execution

The workflow follows these steps:

1. **Connect** to Catalyst Center using provided credentials
2. **Retrieve** existing fabric sites and zones via API calls
3. **Filter** components based on specified criteria
4. **Transform** API responses into Ansible-compatible format
5. **Generate** YAML configuration file with proper structure
6. **Validate** output file format and content

---

## Operations

### Generate Operations (state : gathered)

Use `brownfield_sda_fabric_sites_zones_playbook.yml` for generating yaml playbook configuration operations.


#### 1. Generate All Configurations

**Description**: Retrieves all fabric sites and zones from Catalyst Center regardless of any filters.

```yaml
config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_fabric_sites_zones_config.yaml"
```


#### 2. Component-Specific Generation

**Description**: Generates configuration for specific component types only.


```yaml
config:
  - file_path: "/tmp/sda_fabric_sites_zones_components_config2.yaml"
    component_specific_filters:
      components_list: ["fabric_sites"]
```


#### 3. Custom File Path Generation

**Description**: Specifies custom output path for generated configuration file.

```yaml
config:
  - file_path: "custompath/my_fabric_config.yaml"
    component_specific_filters:
      components_list: ["fabric_sites", "fabric_zones"]
```

**Validate**
Validate Configuration: To ensure a successful execution of the playbooks with your specified inputs, follow these steps:
Input Validation: Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command ./tools/validate.sh -s to perform the validation providing the schema path -d and the input path.


```bash
# Validate

./tools/validate.sh -s workflows/brownfield_sda_fabric_sites_zones/schema/brownfield_sda_fabric_sites_zones_schema.yml \
      -d workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml
```

Return result validate:

```bash
(pyats-nalakkam) [nalakkam@st-ds-4 dnac_ansible_workflows]$ ./tools/validate.sh -s workflows/brownfield_sda_fabric_sites_zones/schema/brownfield_sda_fabric_sites_zones_schema.yml \
>       -d workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml
workflows/brownfield_sda_fabric_sites_zones/schema/brownfield_sda_fabric_sites_zones_schema.yml
workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml
yamale   -s workflows/brownfield_sda_fabric_sites_zones/schema/brownfield_sda_fabric_sites_zones_schema.yml  workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml
Validating workflows/brownfield_sda_fabric_sites_zones/vars/brownfield_sda_fabric_sites_zones_input.yml...
Validation success! 👍
```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
 workflows/brownfield_sda_fabric_sites_zones/playbook/brownfield_sda_fabric_sites_zones_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/brownfield_sda_fabric_sites_zones_input.yml
```

1.Generate All SDA Components

Terminal Return

```code
file_path: /tmp/sda_fabric_sites_zones_components_config1.yaml
        generate_all_configurations: true
      msg:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: /tmp/sda_fabric_sites_zones_components_config1.yaml
      response:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: /tmp/sda_fabric_sites_zones_components_config1.yaml
      status: success
```
2.Component-Specific Generation

Terminal Return 

```code
 component_specific_filters:
          components_list:
          - fabric_sites
        file_path: /tmp/sda_fabric_sites_zones_components_config2.yaml
      msg:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: /tmp/sda_fabric_sites_zones_components_config2.yaml
      response:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: /tmp/sda_fabric_sites_zones_components_config2.yaml
      status: success
```
3.Custom File Path Generation

```code
component_specific_filters:
          components_list:
          - fabric_sites
          - fabric_zones
        file_path: custompath/my_fabric_config.yaml
      msg:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: custompath/my_fabric_config.yaml
      response:
        YAML config generation Task succeeded for module 'brownfield_sda_fabric_sites_zones_config_generator'.:
          file_path: custompath/my_fabric_config.yaml
      status: success
```
---

## Examples

### Example 1: Generate All SDA Components

```yaml
---
# Generate complete SDA fabric configuration
brownfield_sda_fabric_sites_zones_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_fabric_config.yaml"
```
### Example 2: Generate Fabric Sites Only

```yaml
---
# Generate fabric sites configuration only
brownfield_sda_fabric_sites_zones_config:
  - file_path: "/tmp/fabric_sites_config.yaml"
    component_specific_filters:
      components_list: ["fabric_sites"]
```

### Example 3: Generate Fabric Zones Only

```yaml
---
# Generate fabric zones configuration only
brownfield_sda_fabric_sites_zones_config:
  - file_path: "/tmp/fabric_zones_config.yaml"
    component_specific_filters:
      components_list: ["fabric_zones"]
```

### Example 4: Default Output Path

**Output**: Auto-generates filename like `sda_fabric_sites_zones_workflow_manager_playbook_2026-01-28_20-24-06.yml`

```yaml
---
# Generate with auto-generated filename
brownfield_sda_fabric_sites_zones_config:
  - component_specific_filters:
      components_list: ["fabric_sites", "fabric_zones"]
```


### Example 5: Fabric Sites with Specific Site Filter

**Description**: Generates configuration only for the fabric site at "Global/Test_Fabric" location.


```yaml
---
# Generate fabric sites configuration for specific site
brownfield_sda_fabric_sites_zones_config:
  - file_path: "/tmp/specific_fabric_site_config.yaml"
    component_specific_filters:
      components_list: ["fabric_sites"]
      fabric_sites:
        - site_name_hierarchy: "Global/Test_Fabric"
```


### Example 6: Fabric Zones with Specific Zone Filter

**Description**: Generates configuration only for the fabric zone at "Global/Test_Fabric/Bld1" location.


```yaml
---
# Generate fabric zones configuration for specific zone
brownfield_sda_fabric_sites_zones_config:
  - file_path: "/tmp/specific_fabric_zone_config.yaml"
    component_specific_filters:
      components_list: ["fabric_zones"]
      fabric_zones:
        - site_name_hierarchy: "Global/Test_Fabric/Bld1"
```


### Example 7: Combined Sites and Zones with Specific Filters

**Description**: Generates configuration for both a specific fabric site and a specific fabric zone.


```yaml
---
# Generate both fabric sites and zones with specific filters
brownfield_sda_fabric_sites_zones_config:
  - file_path: "/tmp/filtered_sites_and_zones_config.yaml"
    component_specific_filters:
      components_list: ["fabric_sites", "fabric_zones"]
      fabric_sites:
        - site_name_hierarchy: "Global/Test_Fabric"
      fabric_zones:
        - site_name_hierarchy: "Global/Test_Fabric/Bld1"
```


## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://dnacentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)