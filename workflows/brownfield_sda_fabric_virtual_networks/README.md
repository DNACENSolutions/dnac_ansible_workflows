# Brownfield SDA Fabric Virtual Networks Playbook Generator

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

The Brownfield SDA Fabric Virtual Networks playbook generator automates the creation of YAML playbook configurations for existing fabric vlans,virtual networks and anycast gateways deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing infrastructure.


---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `sda_fabric_virtual_networks_workflow_manager` module.
Extract existing SDA fabric VLANs, virtual networks, or anycast gateways configurations from your Cisco Catalyst Center.
Convert them into properly formatted YAML files.
Generate files that are ready to use with Ansible automation.
- **Component Filtering**: Selective generation of fabric VLANs, virtual networks, or anycast gateways
- **Flexible Output**: Configurable file paths and naming conventions
- **Brownfield Support**: Extract configurations from existing Catalyst Center deployments
- **API Integration**: Leverages native Catalyst Center APIs for data retrieval
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

- Catalyst Center admin credentials
- Network connectivity to Catalyst Center API
- SDA fabric infrastructure deployed and configured
- Existing fabric VLANs, virtual networks, and anycast gateways

---

## Workflow Structure

```
brownfield_sda_fabric_virtual_networks/
├── playbook/
│   └── brownfield_sda_fabric_vn_playbook.yml   # Main operations
├── vars/
│   ├── brownfield_sda_fabric_virtual_networks_inputs.yml     # Configuration examples
├── schema/
│   └── brownfield_sda_fabric_virtual_networks_schema.yml     # Input validation
└── README.md                                                
```

---

## Schema Parameters

### Basic Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| generate_all_configurations | boolean | No | false | Generate all components automatically |
| file_path | string | No | auto-generated | Output file path for YAML configuration file |
| component_specific_filters | dict | No | all components | Filters to specify which components to include |

### Component specific Filtering

| Parameter      | Type | Required | Default | Description |
|--------------|------|----------|-------------|-----------|
| components_list | list | No | ["fabric_vlans",virtual_networks","anycast_gateways"] |List of components to include in generation |
| fabric_vlan      | list | No | all fabric vlans|Fabric VLAN filtering criteria |
| virtual_networks | list | No | all virtual networks| Virtual network filtering criteria |
| anycast_gateways | list | No | all anycast gateways|Anycast gateway filtering criteria |

**Valid Component Types:**
- `fabric_vlan`: Layer 2 fabric VLANs
- `virtual_networks`: Layer 3 virtual networks  
- `anycast_gateways`: Anycast gateway configurations

### Fabric VLAN Filters

| Parameter | Type   | Description 
|-----------|--------|-------------|
| vlan_name | string | Filter by VLAN name | 
| vlan_id   | integer| Filter by VLAN ID ( 2 to 4094, excluding reserved VLANs 1002-1005 and 2046) |

### Virtual Network Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| vn_name    string | Filter by VN name | 

### Anycast Gateway Filters

| Parameter  | Type | Description | 
|------------|------|-------------|
| vn_name    | string | Virtual Network name to filter anycast gateways |
| vlan_name  | string | VLAN name to filter anycast gateways  |
| vlan_id    | integer | VLAN ID to filter anycast gateways  |
| ip_pool_name| string | IP Pool name to filter anycast gateways | 

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

Edit `workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml`:

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_config.yml"
```

### Step 4: Validate Configuration

```bash
./tools/validate.sh -s workflows/brownfield_sda_fabric_virtual_networks/schema/brownfield_sda_fabric_virtual_networks_schema.yml \
     -d workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml
```

### Step 5: Execute Playbook

```bash
ansible-playbook -i inventory/demo_lab/hosts.yml \
  workflows/brownfield_sda_fabric_virtual_networks/playbook/brownfield_sda_fabric_virtual_networks_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/brownfield_sda_fabric_virtual_networks_inputs.yml
```

the creation of YAML playbook configurations for existing fabric vlans,virtual networks and anycast gateways deployed in Cisco Catalyst Center.

### Workflow Execution

The workflow follows these steps:

1. **Connect** to Catalyst Center using provided credentials
2. **Retrieve** existing fabric vlans,virtual networks and anycast gateways via API calls
3. **Filter** components based on specified criteria
4. **Transform** API responses into Ansible-compatible format
5. **Generate** YAML configuration file with proper structure
6. **Validate** output file format and content

---

## Operations

### Generate Operations (state: gathered)

Use `brownfield_sda_fabric_virtual_networks_playbook.yml` for generating yaml playbook configuration operations.

#### Generate All Configurations

1. **Description**

Retrieves all fabric vlans,virtual networks and anycast gateways from Catalyst Center regardless of any filters.

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_fabric_virtual_networks_config.yml"
```

#### 2.Component-Specific Generation

**Description**: Generates configuration for specific component types only.

 **Extract Fabric VLANs Only**

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/sda_fabric_vlan_components_config2.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
```

 **Extract Virtual Networks Only**

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/sda_virtual_networks_components_config3.yml"
    component_specific_filters:
      components_list: ["virtual_networks"]
```

 **Extract Anycast Gateways Only**

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/sda_anycast_gateways_components_config4.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
```

**Validate and Execute:**
Validate Configuration: To ensure a successful execution of the playbooks with your specified inputs, follow these steps:
Input Validation: Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command ./tools/validate.sh -s to perform the validation providing the schema path -d and the input path.



```bash
# Validate
./tools/validate.sh -s workflows/brownfield_sda_fabric_virtual_networks/schema/brownfield_sda_fabric_virtual_networks_schema.yml \
                   -d workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml

```

Return result validate:
```bash
(pyats-nalakkam) [nalakkam@st-ds-4 dnac_ansible_workflows]$ ./tools/validate.sh -s workflows/brownfield_sda_fabric_virtual_networks/schema/brownfield_sda_fabric_virtual_networks_schema.yml \
>                    -d workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml
workflows/brownfield_sda_fabric_virtual_networks/schema/brownfield_sda_fabric_virtual_networks_schema.yml
workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml
yamale   -s workflows/brownfield_sda_fabric_virtual_networks/schema/brownfield_sda_fabric_virtual_networks_schema.yml  workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml
Validating workflows/brownfield_sda_fabric_virtual_networks/vars/brownfield_sda_fabric_virtual_networks_inputs.yml...
Validation success! 👍
```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/brownfield_sda_fabric_virtual_networks/playbook/brownfield_sda_fabric_virtual_networks_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/brownfield_sda_fabric_virtual_networks_inputs.yml
```

1.Generate All Configurations

Terminal Return 

```code 

- file_path: /tmp/complete_sda_fabric_virtual_networks_config.yml
        generate_all_configurations: true
  msg:
    components_processed: 3
    components_skipped: 0
    configurations_count: 3
    file_path: /tmp/complete_sda_fabric_virtual_networks_config.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  response:
    components_processed: 3
    components_skipped: 0
    configurations_count: 3
    file_path: /tmp/complete_sda_fabric_virtual_networks_config.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  status: success

```

2.Component Specific Generation:

a.Fabric Vlan filter:

```code
- component_specific_filters:
          components_list:
          - fabric_vlan
        file_path: /tmp/sda_fabric_vlan_components_config2.yml
  msg:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_fabric_vlan_components_config2.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  response:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_fabric_vlan_components_config2.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  status: success
```

b.Virtual Neworks Filter:

```code
- component_specific_filters:
          components_list:
          - virtual_networks
        file_path: /tmp/sda_virtual_networks_components_config3.yml
  msg:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_virtual_networks_components_config3.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  response:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_virtual_networks_components_config3.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  status: success
```

c.Anycast Gateways Filter :

```code
- component_specific_filters:
          components_list:
          - anycast_gateways
        file_path: /tmp/sda_anycast_gateways_components_config4.yml
  msg:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_anycast_gateways_components_config4.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  response:
    components_processed: 1
    components_skipped: 0
    configurations_count: 1
    file_path: /tmp/sda_anycast_gateways_components_config4.yml
    message: YAML configuration file generated successfully for module 'sda_fabric_virtual_networks_workflow_manager'
    status: success
  status: success
```

---

## Examples

### Example 1: Generate ALL SDA fabric virtual networks components

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_infrastructure.yml"
```

### Example 2: Fabric VLAN Filters only

Extract all fabric VLANs.

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/fabric_vlan_audit.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
```

### Example 3: Virtual Network Filters only

Extract all virtual networks

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/migration_virtual_networks.yml"
    component_specific_filters:
      components_list: ["virtual_networks"]
      virtual_networks:
        - vn_name: "Production-VN"
        - vn_name: "Development-VN"
```

### Example 4: Anycast Gateway Filters only


```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/critical_gateways_backup.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
      anycast_gateways:
        - ip_pool_name: "Critical-Pool-1"
        - ip_pool_name: "Critical-Pool-2"
```

### Example 5: Multi-Filter configurations


```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/vlans_and_vns.yml"
    component_specific_filters:
      components_list: ["fabric_vlan", "virtual_networks"]
      fabric_vlan:
        - vlan_name: "Data-VLAN-100"
        - vlan_name: "Voice-VLAN-200"
      virtual_networks:
        - vn_name: "Corporate-VN"
        - vn_name: "Voice-VN"
```

### Example 6: Fabric VLANS within specific VLAN ID 

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/vlan_range_100_200.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
      fabric_vlan:
        - vlan_id: 1023
        - vlan_id: 1028
        - vlan_id: 1029
```

### Example 7:  Gateway configurations with all available filters.

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/comprehensive_gateways.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
      anycast_gateways:
        - vn_name: "Corporate-VN"
          vlan_name: "Data-VLAN-100"
          vlan_id: 100
          ip_pool_name: "Corporate-Pool-1"
        - vn_name: "Guest-VN"
          vlan_name: "Guest-VLAN-300"
          vlan_id: 300
          ip_pool_name: "Guest-Pool-1"
```

### Example 8: Generate separate files for each component type.

```yaml
brownfield_sda_fabric_virtual_networks_details:
  - file_path: "/tmp/fabric_vlans.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
  - file_path: "/tmp/virtual_networks.yml"
    component_specific_filters:
      components_list: ["virtual_networks"]
  - file_path: "/tmp/anycast_gateways.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
```
---

## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://dnacentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)