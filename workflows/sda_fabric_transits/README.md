# Catalyst Center SDA Fabric transits (IP/SDA) workflow

## Fabric Transits

### Transits
A transit is a site that interconnects two or more fabric sites or connects the fabric site with external networks (Internet, data center, and so on). There are two types of transit networks:

### IP transit: 
Uses a regular IP network to connect to an external network or to connect two or more fabric sites. It leverages a traditional IP-based (VRF-LITE, MPLS) network, which requires remapping of VRFs and SGTs between sites.

### SD-Access transit: 
Uses LISP/VxLAN encapsulation to connect two fabric sites. The SD-Access transit area may be defined as a portion of the fabric that has its own control plane nodes, but does not have edge or border nodes. However, it can work with a fabric that has an external border. With an SD-Access transit, an end-to-end policy plane is maintained using SGT group tags.

## Before you begin

Few things to know:

### Note:
1. You can’t add an SD-Access (LISP Pub/Sub) transit to a fabric site that uses LISP/BGP control plane. You can’t add SD-Access (LISP/BGP) transit to a fabric site that uses LISP Pub/Sub control plane.

2. To complete the native multicast configuration over multiple sites that are connected to the SD-Access transit, ensure that you enable multicast over SD-Access transit on the border nodes.

3. To create SD-Access Transit atleast one Transit CP device must be provided. 


## Fabric Site Zone Management Workflow Overview

This diagram illustrates the flow of a Fabric Site Zone management workflow initiated from an **Ansible Playbook**, utilizing the `cisco.dnac.sda_fabric_transits_workflow_manager` module to interact with **Cisco Catalyst Center**.

### Workflow Steps

#### 1. Ansible Playbook
The process begins with the **Ansible Playbook**, which triggers the execution of the `cisco.dnac.sda_fabric_transits_workflow_manager` module. The playbook defines the tasks and configurations needed to manage users and roles.

#### 2. Ansible Module
Within the **Ansible Module**, the `cisco.dnac.sda_fabric_transits_workflow_manager` module interacts with the **Cisco Catalyst Center SDK** to perform tasks such as creating or updating users, assigning roles, and managing role-based access control.

#### 3. Cisco Catalyst Center SDK
The **SDK** acts as an intermediary between the Ansible Module and the **Cisco Catalyst Center APIs**. It handles the construction and execution of API calls to Cisco Catalyst Center.

#### 4. Cisco Catalyst Center APIs
The final step involves direct interaction with the **Cisco Catalyst Center APIs** to perform the Fabric Site Zone management tasks.

## Understanding the Configs for Fabric Site Zone Management Tasks
- **config_verify** (bool): 
  - Set to `True` to verify the Cisco Catalyst Center configuration after applying the playbook configuration. 
  - **Defaults**: `False`.
- **state** (str): 
  - The state of Cisco Catalyst Center after module completion. 
  - **Choices**: [merged, deleted]. 
  - **Defaults**: `merged`.
- **config** (list[dict]): 
  - A list of SDA fabric transit configurations. Each entry represents a transit network configuration. 
  - **Required**.
  - **sda_fabric_transits** (list[dict]): 
    - SDA fabric transit configurations.
    - **name** (str): 
      - The name of the SDA fabric transit. 
      - **Required**.
    - **transit_type** (str): 
      - Type of the fabric transit. 
      - **Choices**: [IP_BASED_TRANSIT, SDA_LISP_PUB_SUB_TRANSIT, SDA_LISP_BGP_TRANSIT]. 
      - **Defaults**: `IP_BASED_TRANSIT`.
        - **IP_BASED_TRANSIT**: Manages IP routing and data flow between network segments.
        - **SDA_LISP_PUB_SUB_TRANSIT**: Decouples device location and identity information for dynamic routing.
        - **SDA_LISP_BGP_TRANSIT**: Integrates LISP with BGP for optimized routing decisions.

    - **ip_transit_settings** (dict): 
      - Configuration settings for IP-based transit. 
      - **Required** when `transit_type` is `IP_BASED_TRANSIT`. 
      - **Note**: `IP_BASED_TRANSIT` cannot be updated.
      
      - **routing_protocol_name** (str): 
        - The routing protocol. 
        - **Choices**: [BGP]. 
        - **Defaults**: `BGP`.

      - **autonomous_system_number** (str): 
        - The Autonomous System Number (ASN) (1-4294967295). 
        - Must be unique for every IP-based transit. 
        - **Required** when `transit_type` is `IP_BASED_TRANSIT`.

    - **sda_transit_settings** (dict): 
      - Configuration settings for SDA-based transit. 
      - **Required** when `transit_type` is `SDA_LISP_PUB_SUB_TRANSIT` or `SDA_LISP_BGP_TRANSIT`.

      - **is_multicast_over_transit_enabled** (bool): 
        - Enables/disables multicast traffic over the transit network. 
        - Available only when `transit_type` is `SDA_LISP_PUB_SUB_TRANSIT`.

      - **control_plane_network_device_ips** (list[str]): 
        - IP addresses of the control plane network devices. 
        - **Required** when `transit_type` is `SDA_LISP_BGP_TRANSIT` or `SDA_LISP_PUB_SUB_TRANSIT`.
        - At least one device is required.
        - Maximum of 2 devices allowed for `SDA_LISP_BGP_TRANSIT`.
        - Maximum of 4 devices allowed for `SDA_LISP_PUB_SUB_TRANSIT`.
        - `SDA_LISP_PUB_SUB_TRANSIT` supports devices with IOS XE 17.6 or later.
        - Devices must be in the fabric site or zone.

### Task: Create Fabric Transits

This task creates **Fabric Transits** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Transits
      cisco.dnac.sda_fabric_transits_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - sda_fabric_transits:
                - name: ansible_test
                transit_type: IP_BASED_TRANSIT
                ip_transit_settings:
                    routing_protocol_name: BGP
                    autonomous_system_number: 1111
      tags: create_ip_base_single
```

### Task: Create Fabric Transits

This task creates **Fabric Transits** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Transits
      cisco.dnac.sda_fabric_transits_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - sda_fabric_transits:
                - name: ansible_test2
                transit_type: IP_BASED_TRANSIT
                ip_transit_settings:
                    routing_protocol_name: BGP
                    autonomous_system_number: 1112
                - name: ansible_test3
                transit_type: IP_BASED_TRANSIT
                ip_transit_settings:
                    routing_protocol_name: BGP
                    autonomous_system_number: 1113
                - name: ansible_test4
                transit_type: IP_BASED_TRANSIT
                ip_transit_settings:
                    routing_protocol_name: BGP
                    autonomous_system_number: 1114
                - name: ansible_test5
                transit_type: IP_BASED_TRANSIT
                ip_transit_settings:
                    routing_protocol_name: BGP
                    autonomous_system_number: 1115
      tags: create_ip_base_multiple
```

### Task: Create Fabric Transits

This task creates **Fabric Transits** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Transits
      cisco.dnac.sda_fabric_transits_workflow_manager:
        <<: *common_config
        state: merged
        config:
        - sda_fabric_transits:
            - name: ansible_bgp_test
            transit_type: SDA_LISP_BGP_TRANSIT
            sda_transit_settings:
                control_plane_network_device_ips:
                - 204.1.2.4
      tags: create_lisp_bgp
```

### Task: Create Fabric Transits

This task creates **Fabric Transits** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Transits
      cisco.dnac.sda_fabric_transits_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - sda_fabric_transits:
                - name: ansible_pub_sub_test
                transit_type: SDA_LISP_PUB_SUB_TRANSIT
                sda_transit_settings:
                    is_multicast_over_transit_enabled: false
                    control_plane_network_device_ips:
                    - 204.1.2.5
      tags: create_lisp_pub_sub
```

### Task: Create Fabric Transits

This task creates **Fabric Transits** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Deleted Fabric Transits
      cisco.dnac.sda_fabric_transits_workflow_manager:
        <<: *common_config
        state: deleted
        config:
            - sda_fabric_transits:
            - name: ansible_test
            - name: ansible_test2
            - name: ansible_test3
            - name: ansible_test4
            - name: ansible_test5
            - name: ansible_test6
      tags: delete_transits_multiple
```

## Create an Fabric transits: Running the Playbook
Playbook: workflows/sda_fabric_transits/playbook/playbook/sda_fabric_transits_workflow_playbook.yml
Schema: workflows/sda_fabric_transits/schema/sda_fabric_transits_workflow_schema.yml
Input Variables: [Title](vars/sda_fabric_transits_workflow_inputs.yml)
1. **Validate Your Input:**

```bash
   yamale -s workflows/sda_fabric_transits/schema/sda_fabric_transits_workflow_schema.yml workflows/sda_fabric_transits/vars/sda_fabric_transits_workflow_inputs.yml
```
2. **Execute the Playbook**
User inputs: ./workflows/sda_fabric_transits/vars/fabric_sites_zones_inputs.yml
Playbook: workflows/sda_fabric_transits/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=<your input file>
```
###  To create or update the fabroc transits and zones example
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml
```
###  To delete existing fabric transits:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/delete_sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml
```
## Important Notes
Refer to the Catalyst Center documentation for detailed instructions on configuring fabric sites and fabric transits and using the Ansible playbooks.
Consider backing up your configuration before running the playbooks, especially the delete playbook.
If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.
