# SDA Fabric Virtual Networks Playbook Config Generator

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

The SDA Fabric Virtual Networks playbook config generator automates the creation of YAML playbook configurations for existing fabric vlans,virtual networks and anycast gateways deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing infrastructure.


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
sda_fabric_virtual_networks_playbook_config_generator/
├── playbook/
│   └── sda_fabric_virtual_networks_playbook_config_generator_playbook.yml   # Main operations
├── vars/
│   ├── sda_fabric_virtual_networks_playbook_config_generator_inputs.yml     # Configuration examples
├── schema/
│   └── sda_fabric_virtual_networks_playbook_config_generator_schema.yml     # Input validation
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

Edit `workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml`:

```yaml
sda_fabric_virtual_networks_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_config.yml"
```

### Step 4: Validate Configuration

```bash
./tools/validate.sh -s workflows/sda_fabric_virtual_networks_playbook_config_generator/schema/sda_fabric_virtual_networks_playbook_config_generator_schema.yml \
     -d workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
```

### Step 5: Execute Playbook

```bash
ansible-playbook -i inventory/demo_lab/hosts.yml \
  workflows/sda_fabric_virtual_networks_playbook_config_generator/playbook/sda_fabric_virtual_networks_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
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

Use `sda_fabric_virtual_networks_playbook_config_generator_playbook.yml` for generating yaml playbook configuration operations.

#### Generate All Configurations

1. **Description**

Retrieves all fabric vlans,virtual networks and anycast gateways from Catalyst Center regardless of any filters.

```yaml
sda_fabric_virtual_networks_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_fabric_virtual_networks_config.yml"
```

#### 2.Component-Specific Generation

**Description**: Generates configuration for specific component types only.

 **Extract Fabric VLANs Only**

```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/sda_fabric_vlan_components_config2.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
```

 **Extract Virtual Networks Only**

```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/sda_virtual_networks_components_config3.yml"
    component_specific_filters:
      components_list: ["virtual_networks"]
```

 **Extract Anycast Gateways Only**

```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/sda_anycast_gateways_components_config4.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
```

**Validate and Execute:**
Validate Configuration: To ensure a successful execution of the playbooks with your specified inputs, follow these steps:
Input Validation: Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command ./tools/validate.sh -s to perform the validation providing the schema path -d and the input path.



```bash
# Validate
./tools/validate.sh -s workflows/sda_fabric_virtual_networks_playbook_config_generator/schema/sda_fabric_virtual_networks_playbook_config_generator_schema.yml \
                   -d workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml

```

Return result validate:
```bash
(pyats-nalakkam) [nalakkam@st-ds-4 dnac_ansible_workflows]$ ./tools/validate.sh -s workflows/sda_fabric_virtual_networks_playbook_config_generator/schema/sda_fabric_virtual_networks_playbook_config_generator_schema.yml \
>                    -d workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
workflows/sda_fabric_virtual_networks_playbook_config_generator/schema/sda_fabric_virtual_networks_playbook_config_generator_schema.yml
workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
yamale   -s workflows/sda_fabric_virtual_networks_playbook_config_generator/schema/sda_fabric_virtual_networks_playbook_config_generator_schema.yml  workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
Validating workflows/sda_fabric_virtual_networks_playbook_config_generator/vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml...
Validation success! 👍

```

```bash
# Execute
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/sda_fabric_virtual_networks_playbook_config_generator/playbook/sda_fabric_virtual_networks_playbook_config_generator_playbook.yml \
  --extra-vars VARS_FILE_PATH=../vars/sda_fabric_virtual_networks_playbook_config_generator_inputs.yml
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
sda_fabric_virtual_networks_config:
  - generate_all_configurations: true
    file_path: "/tmp/complete_sda_infrastructure.yml"
```

After running the playbook, the following YAML configuration is generated:

```yaml
---
config:
- fabric_vlan:
  - vlan_name: test1
    vlan_id: 1024
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: Fabric_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 80net_sub-WiredVNFB1
    vlan_id: 1021
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: Test_Vlan
    vlan_id: 1000
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: true
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: 112net_sub-WiredVNFBLayer2
    vlan_id: 1028
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: test2
    vlan_id: 1023
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: INFRA_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: CRITICAL_VLAN
    vlan_id: 1029
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: test5
    vlan_id: 1025
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WirelessVNFGuest
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: VOICE_VLAN
    vlan_id: 2046
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: a4_lay2
    vlan_id: 3444
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.1
  - vlan_name: SGT_Port_test_sub-SGT_Port_test
    vlan_id: 1032
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: SGT_Port_test
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: WSClients_sub-WirelessVNFB
    vlan_id: 1023
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFB
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: SENSORPool_sub-WiredVNStatic
    vlan_id: 1027
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNStatic
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 96net_sub-WiredVNFBLayer2
    vlan_id: 1030
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: 40_10_1_0-test_vlan_layer3
    vlan_id: 1049
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: test_vlan_layer3
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: GP_sub-WirelessVNFGuest
    vlan_id: 1031
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFGuest
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: test
    vlan_id: 1022
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 80net_nyc-WiredVNFB1
    vlan_id: 1021
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: DEFAULT_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 64net_sub-WiredVNFB1
    vlan_id: 1022
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: WClients_sub-WirelessVNFB
    vlan_id: 1024
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFB
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: EXT_POOL_sub-INFRA_VN
    vlan_id: 1025
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: INFRA_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
- virtual_networks:
  - vn_name: VN_SanJose_1
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN7
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WirelessVNFGuest
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
  - vn_name: test_vlan_layer3
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN1
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
  - vn_name: DEFAULT_VN
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
  - vn_name: INFRA_VN
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
  - vn_name: SGT_Port_test
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN6
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: Fabric_VN
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN3
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN5
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFBLayer2
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFB1
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WirelessVNFB
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
  - vn_name: VN4
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNStatic
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/SAN-FRANCISCO
      fabric_type: fabric_site
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: IntraSubnet_VN
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: VN2
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
- anycast_gateways:
  - vn_name: WirelessVNFB
    ip_pool_name: WSClients_sub
    vlan_name: WSClients_sub-WirelessVNFB
    vlan_id: 1023
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: true
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFB1
    ip_pool_name: 64net_sub
    vlan_name: 64net_sub-WiredVNFB1
    vlan_id: 1022
    traffic_type: VOICE
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFBLayer2
    ip_pool_name: 96net_sub
    vlan_name: 96net_sub-WiredVNFBLayer2
    vlan_id: 1030
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: true
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: DEFAULT_VN
    ip_pool_name: 80net_nyc
    vlan_name: 80net_nyc-WiredVNFB1
    vlan_id: 1021
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: WirelessVNFB
    ip_pool_name: WClients_sub
    vlan_name: WClients_sub-WirelessVNFB
    vlan_id: 1024
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: true
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFBLayer2
    ip_pool_name: CR_VOICE_sub
    vlan_name: VOICE_VLAN
    vlan_id: 2046
    traffic_type: VOICE
    is_critical_pool: true
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: test_vlan_layer3
    ip_pool_name: Fabric_VN-sub
    vlan_name: 40_10_1_0-test_vlan_layer3
    vlan_id: 1049
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: INFRA_VN
    ip_pool_name: WClients_nyc
    vlan_name: test2
    vlan_id: 1023
    traffic_type: DATA
    pool_type: FABRIC_AP
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: false
    fabric_site_location:
      site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: WirelessVNFGuest
    ip_pool_name: GP_sub
    vlan_name: GP_sub-WirelessVNFGuest
    vlan_id: 1031
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: Fabric_VN
    ip_pool_name: GP_nyc
    vlan_name: test1
    vlan_id: 1024
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: WiredVNFB1
    ip_pool_name: 112net_nyc
    vlan_name: test
    vlan_id: 1022
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: WiredVNFB1
    ip_pool_name: 80net_sub
    vlan_name: 80net_sub-WiredVNFB1
    vlan_id: 1021
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFBLayer2
    ip_pool_name: 112net_sub
    vlan_name: 112net_sub-WiredVNFBLayer2
    vlan_id: 1028
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: true
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNStatic
    ip_pool_name: SENSORPool_sub
    vlan_name: SENSORPool_sub-WiredVNStatic
    vlan_id: 1027
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: SGT_Port_test
    ip_pool_name: SGT_Port_test_sub
    vlan_name: SGT_Port_test_sub-SGT_Port_test
    vlan_id: 1032
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WirelessVNFGuest
    ip_pool_name: 96net_nyc
    vlan_name: test5
    vlan_id: 1025
    traffic_type: DATA
    is_critical_pool: false
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
  - vn_name: INFRA_VN
    ip_pool_name: EXT_POOL_sub
    vlan_name: EXT_POOL_sub-INFRA_VN
    vlan_id: 1025
    traffic_type: DATA
    pool_type: EXTENDED_NODE
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: false
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
  - vn_name: WiredVNFBLayer2
    ip_pool_name: CR_POOL_sub
    vlan_name: CRITICAL_VLAN
    vlan_id: 1029
    traffic_type: DATA
    is_critical_pool: true
    layer2_flooding_enabled: false
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    ip_directed_broadcast: false
    intra_subnet_routing_enabled: false
    multiple_ip_to_mac_addresses: false
    supplicant_based_extended_node_onboarding: false
    group_policy_enforcement_enabled: true
    fabric_site_location:
      site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site

```

### Example 2: Fabric VLAN Filters only

Extract all fabric VLANs.

```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/fabric_vlan_audit.yml"
    component_specific_filters:
      components_list: ["fabric_vlan"]
```
After running the playbook, the following YAML configuration is generated:

```yaml
---
config:
- fabric_vlan:
  - vlan_name: test1
    vlan_id: 1024
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: Fabric_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 80net_sub-WiredVNFB1
    vlan_id: 1021
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: Test_Vlan
    vlan_id: 1000
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    is_wireless_flooding_enable: true
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: 112net_sub-WiredVNFBLayer2
    vlan_id: 1028
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: test2
    vlan_id: 1023
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: INFRA_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: CRITICAL_VLAN
    vlan_id: 1029
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: test5
    vlan_id: 1025
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WirelessVNFGuest
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: VOICE_VLAN
    vlan_id: 2046
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: a4_lay2
    vlan_id: 3444
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    is_wireless_flooding_enable: false
    is_resource_guard_enable: true
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.1
  - vlan_name: SGT_Port_test_sub-SGT_Port_test
    vlan_id: 1032
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: SGT_Port_test
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: WSClients_sub-WirelessVNFB
    vlan_id: 1023
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFB
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: SENSORPool_sub-WiredVNStatic
    vlan_id: 1027
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNStatic
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 96net_sub-WiredVNFBLayer2
    vlan_id: 1030
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFBLayer2
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: 40_10_1_0-test_vlan_layer3
    vlan_id: 1049
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: test_vlan_layer3
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: GP_sub-WirelessVNFGuest
    vlan_id: 1031
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFGuest
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: test
    vlan_id: 1022
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 80net_nyc-WiredVNFB1
    vlan_id: 1021
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/New York
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: DEFAULT_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: 64net_sub-WiredVNFB1
    vlan_id: 1022
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: VOICE
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: WiredVNFB1
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
  - vlan_name: WClients_sub-WirelessVNFB
    vlan_id: 1024
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: true
    associated_layer3_virtual_network: WirelessVNFB
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED
    flooding_address: 239.0.17.3
  - vlan_name: EXT_POOL_sub-INFRA_VN
    vlan_id: 1025
    fabric_site_locations:
    - site_name_hierarchy: Global/USA/SAN JOSE
      fabric_type: fabric_site
    traffic_type: DATA
    fabric_enabled_wireless: false
    associated_layer3_virtual_network: INFRA_VN
    is_wireless_flooding_enable: false
    is_resource_guard_enable: false
    flooding_address_assignment: SHARED

```


### Example 3: Virtual Network Filters only

Extract all virtual networks

```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/migration_virtual_networks.yml"
    component_specific_filters:
      components_list: ["virtual_networks"]
      virtual_networks:
        - vn_name: "Production-VN"
        - vn_name: "Development-VN"
```

### Example 4: Anycast Gateway Filters only


```yaml
sda_fabric_virtual_networks_config:
  - file_path: "/tmp/critical_gateways_backup.yml"
    component_specific_filters:
      components_list: ["anycast_gateways"]
      anycast_gateways:
        - ip_pool_name: "Critical-Pool-1"
        - ip_pool_name: "Critical-Pool-2"
```

### Example 5: Multi-Filter configurations


```yaml
sda_fabric_virtual_networks_config:
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
sda_fabric_virtual_networks_config:
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
sda_fabric_virtual_networks_config:
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
sda_fabric_virtual_networks_config:
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