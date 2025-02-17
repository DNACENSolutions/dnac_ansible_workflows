# Catalyst Center SDA Fabric sites and fabric Zones Playbooks

## Fabric Sites

A **fabric site** is an independent fabric area with a unique set of network devices, including:

- Control plane
- Border
- Edge
- Wireless controller
- ISE PSN

Different levels of redundancy and scale can be designed per site by including local resources such as DHCP, AAA, DNS, Internet, and more.

### Fabric Site Coverage

A fabric site can cover:

- **Single location**: Branch, campus, or metro campus
- **Multiple locations**: Metro campus + multiple branches
- **Subset of a location**: Building or area within a campus

### Benefits of a Software-Defined Access Fabric Network

A Software-Defined Access fabric network may comprise multiple sites, offering:

- **Scale**
- **Resiliency**
- **Survivability**
- **Mobility**

The overall aggregation of fabric sites accommodates a large number of endpoints and scales modularly or horizontally. Multiple fabric sites are interconnected using a transit.

## Before you begin

You can create a fabric site only if IP Device Tracking (IPDT) is already configured for the site.

## In the Authentication Profile you do the following:

Choose an authentication template for the fabric site:

- **Closed Authentication**: Any traffic before authentication is dropped, including DHCP, DNS, and ARP.
- **Open Authentication**: A host is allowed network access without having to go through 802.1X authentication.
- **Low Impact**: Security is added by applying an ACL to the switch port, allowing very limited network access before authentication. After a host has been successfully authenticated, additional network access is granted.
- **None**

(Optional) If you choose Closed Authentication, Open Authentication, or Low Impact, you can customize the authentication settings:

- **First Authentication Method**: Choose `802.1x` or `MAC Authentication Bypass (MAB)`.
- **802.1x Timeout (in seconds)**: Use the slider to specify the 802.1x timeout, in seconds.
- **Wake on LAN**: Choose `Yes` or `No`.
- **Number of Hosts**: Choose `Unlimited` or `Single`.
- **BPDU Guard**: Use this checkbox to enable or disable the Bridge Protocol Data Unit (BPDU) guard on all the Closed Authentication ports.

## Fabric Site Zone Management Workflow Overview

This diagram illustrates the flow of a Fabric Site Zone management workflow initiated from an **Ansible Playbook**, utilizing the `cisco.dnac.sda_fabric_sites_zones_workflow_manager` module to interact with **Cisco Catalyst Center**.

### Workflow Steps

#### 1. Ansible Playbook
The process begins with the **Ansible Playbook**, which triggers the execution of the `cisco.dnac.sda_fabric_sites_zones_workflow_manager` module. The playbook defines the tasks and configurations needed to manage users and roles.

#### 2. Ansible Module
Within the **Ansible Module**, the `cisco.dnac.sda_fabric_sites_zones_workflow_manager` module interacts with the **Cisco Catalyst Center SDK** to perform tasks such as creating or updating users, assigning roles, and managing role-based access control.

#### 3. Cisco Catalyst Center SDK
The **SDK** acts as an intermediary between the Ansible Module and the **Cisco Catalyst Center APIs**. It handles the construction and execution of API calls to Cisco Catalyst Center.

#### 4. Cisco Catalyst Center APIs
The final step involves direct interaction with the **Cisco Catalyst Center APIs** to perform the Fabric Site Zone management tasks.

## Understanding the Configs for Fabric Site Zone Management Tasks

- **config_verify** (bool): 
  - Set to `True` to verify the Cisco Catalyst Center configuration after applying the playbook configuration. 
  - **Defaults**: `False`.

- **state** (str): 
  - The desired state of Cisco Catalyst Center after the module execution. 
  - **Choices**: [merged, deleted]. 
  - **Defaults**: `merged`.

- **config** (list[dict]): 
  - A list containing detailed configurations for creating, updating, or deleting fabric sites or zones in an SDA environment. 
  - Includes specifications for updating the authentication profile template for these sites. 
  - Each element represents an operation (add, modify, delete) on SDA infrastructure. 
  - **Required**.

  - **fabric_sites** (dict): 
    - Detailed configurations for managing fabric sites and zones, including REST Endpoints for Audit logs and Events. 
    - Essential for specifying attributes and parameters for fabric site/zone lifecycle management and authentication profile updates.

    - **site_name_hierarchy** (str): 
      - The unique name identifying the site for create, update, delete operations on fabric sites or zones, and for updating the authentication profile template. 
      - **Required** for any fabric site/zone management.

    - **fabric_type** (str): 
      - Specifies the type of site to be managed. 
      - **Choices**: ['fabric_site', 'fabric_zone']. 
      - **Defaults**: 'fabric_site'. 
      - 'fabric_site' refers to a broader network area, while 'fabric_zone' refers to a specific segment within the site. 
      - **Required**.

    - **authentication_profile** (str): 
      - The authentication profile applied to the fabric. 
      - **Choices**: ['Closed Authentication', 'Low Impact', 'No Authentication', 'Open Authentication']. 
      - Critical for creating/updating fabric sites and updating the authentication profile template.

    - **is_pub_sub_enabled** (bool): 
      - A flag indicating whether the pub/sub mechanism is enabled for control nodes in the fabric site. 
      - Relevant only for creating/updating fabric sites (not zones). 
      - **Defaults**: `True` for fabric sites. Not applicable for fabric zones.

    - **update_authentication_profile** (dict): 
      - Details for updating the authentication profile template associated with the fabric site. 
      - Includes advanced authentication settings.

      - **authentication_order** (str): 
        - The primary authentication method for the site. 
        - **Choices**: ['dot1x', 'mac']. 
        - Determines the authentication mechanism attempt order.

      - **dot1x_fallback_timeout** (int): 
        - The timeout (in seconds) for falling back from 802.1X authentication (3-120 seconds). 
        - Defines the wait time before attempting an alternative method if 802.1X fails.

      - **wake_on_lan** (bool): 
        - Enables/disables the Wake-on-LAN feature. 
        - Allows remote wake-up of low-power devices.

      - **number_of_hosts** (str): 
        - Specifies the number of hosts allowed per port. 
        - **Choices**: ['Single', 'Unlimited']. 
        - Controls network access and maintains security.

      - **enable_bpu_guard** (bool): 
        - Enables/disables BPDU Guard. 
        - A security mechanism that disables a port upon receiving a BPDU. 
        - **Defaults**: `True` when the authentication profile is "Closed Authentication".

### Task: Create Fabric Sites

This task creates **Fabric Sites** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Sites
      cisco.dnac.sda_fabric_sites_zones_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - fabric_sites:
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10
                authentication_profile: "No Authentication"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD11
                authentication_profile: "No Authentication"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD12
                authentication_profile: "No Authentication"
      tags: create_fabric_site
```

### Task: Create Fabric zone

This task creates **Fabric zone** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Zone
      cisco.dnac.sda_fabric_sites_zones_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - fabric_sites:
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD11/FLOOR1
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD11/FLOOR2
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD11/FLOOR3
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD11/FLOOR4
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
      tags: create_fabric_zone
```

### Task: Create Fabric Site and Fabric Zone

This task creates **Fabric Site** and **Fabric zone** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Create Fabric Site and Fabric Zone
      cisco.dnac.sda_fabric_sites_zones_workflow_manager:
        <<: *common_config
        state: merged
        config:
            - fabric_sites:
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10
                authentication_profile: "No Authentication"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR1
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR2
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR3
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
                - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR4
                authentication_profile: "No Authentication"
                fabric_type: "fabric_zone"
      tags: create_fabric_site_zone
```

### Task: Delete Fabric zone

This task Delete **Fabric zone** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Delete Fabric Zone
      cisco.dnac.sda_fabric_sites_zones_workflow_manager:
        <<: *common_config
        state: deleted
        config:
        - fabric_sites:
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR1
            fabric_type: "fabric_zone"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR2
            fabric_type: "fabric_zone"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR3
            fabric_type: "fabric_zone"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR4
            fabric_type: "fabric_zone"
      tags: delete_fabric_site
```

### Task: Create Fabric zone

This task creates **Fabric zone** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

```yaml
    - name: Delete Fabric site
      cisco.dnac.sda_fabric_sites_sites_workflow_manager:
        <<: *common_config
        state: deleted
        config:
        - fabric_sites:
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR1
            fabric_type: "fabric_site"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR2
            fabric_type: "fabric_site"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR3
            fabric_type: "fabric_site"
            - site_name_hierarchy: Global/USA/RTP/RTP_BLD10/FLOOR4
            fabric_type: "fabric_site"
      tags: delete_fabric_site
```

## Create an Fabric sites and fabric zones: Running the Playbook
Figure 1 Creating Fabric site and fabric Zones
![Alt text](./images/Fabric_sites.png)

Figure 2 Select the Authentication profile for the fabric site
![Alt text](./images/Fabric_site_auth_profile.png)

Figure 3 Select the fabric zones
![Alt text](./images/Fabric_zones.png)

Figure 4 Configuratin Summary
![Alt text](./images/Fabric_site_zone_summary.png)

1. **Validate Your Input:**

```bash
   yamale -s workflows/sda_fabric_sites_zones/schema/sda_fabric_sites_zones_schema.yml workflows/sda_fabric_sites_zones/vars/sda_fabric_sites_zones_inputs.yml
```
2. **Execute the Playbook**
User inputs: ./workflows/sda_fabric_sites_zones/vars/sda_fabric_sites_zones_inputs.yml
Playbook: workflows/sda_fabric_sites_zones/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=<your input file>

#===========================
    TASK [Print the fabric site(s)/zone(s) output] *************************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": {
        "ansible_facts": {
            "discovered_interpreter_python": "/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11"
        },
        "changed": true,
        "diff": [],
        "failed": false,
        "response": "Fabric site(s) '['Global/USA/AREA1/AREA1 BLD1']' created successfully in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR1', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR2']' created successfully in Cisco Catalyst Center.",
        "warnings": [
            "Platform darwin on host catalyst_center220 is using the discovered Python interpreter at /Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11, but future installation of another Python interpreter could change the meaning of that path. See https://docs.ansible.com/ansible-core/2.15/reference_appendices/interpreter_discovery.html for more information."
        ]
    }
}
TASK [run command module to find python version] ***********************************************************************************************************************************************************************************************************
changed: [catalyst_center220 -> catalyst_center_hosts]

PLAY RECAP *************************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=6    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

```
Figure 6 Post Creation UI View
![Alt text](./images/Fabric_site_and_zones.png)


###  To create or update the fabric sites and zones example
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_sites_zones_inputs.yml
```
###  To delete existing discoveries:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/delete_sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_sites_zones_inputs.yml
```
## Creating Bulk Site confiogurations using JINJA template and using the playbook

Create a Jinja template for your desired inopout, Example Jinja template for sites is as below
This Example create 3 Areas and in Each Areas create 3 buildings and in each building it creates 3 floors. 
This example can be reused and customized to your requirement and increase the requirement scale.

### Creating bulk sites with jinja template
workflow/sites/jinja_template/site_generation_template.j2 template can be used to customize the template and generate bulk sites.

```bash
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
fabric_sites_and_zones:
{% for i in range(1, 4) %}
    - fabric_sites:
        - fabric_type: fabric_site
          site_name: Global/USA/AREA{{i}}/AREA{{i}} BLD{{i}}
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
{% for j in range(1, 4) %}
        - fabric_type: fabric_zone
          site_name: Global/USA/AREA{{i}}/AREA{{i}} BLD{{i}}/AREA{{i}} BLD{{i}} FLOOR{{j}}
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
{% endfor %}
{% endfor %}
```

Use the input var file: jinja_template_site_hierarchy_design_vars.yml and secify the name of you Jinja template in the input vars file.

5. Execute with Jinja template:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_j2_template_fabric_sites_input.yml

TASK [Print the fabric site(s)/zone(s) output] *************************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": {
        "changed": true,
        "diff": [],
        "failed": false,
        "response": "Fabric site(s) '['Global/USA/AREA2/AREA2 BLD2', 'Global/USA/AREA3/AREA3 BLD3']' created successfully in Cisco Catalyst Center. Fabric site(s) '['Global/USA/AREA1/AREA1 BLD1']' need no update in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR1', 'Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR2', 'Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR3', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR1', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR2', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR3']' created successfully in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR1', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR2', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR3']' need no update in Cisco Catalyst Center."
    }
}
#=========run logs================================
TASK [Delete the template file] ****************************************************************************************************************************************************************************************************************************
changed: [catalyst_center220]

TASK [Fabric site(s)/zone(s) playbook end time] ************************************************************************************************************************************************************************************************************
ok: [catalyst_center220]

TASK [Print fabric site(s)/zone(s) playbook execution time] ************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": "Fabric site(s)/zone(s) playbook run time: 2024-10-17 17:07:33.629001, end: 2024-10-17 17:08:46.419055"
}

TASK [run command module to find python version] ***********************************************************************************************************************************************************************************************************
changed: [catalyst_center220 -> catalyst_center_hosts]

PLAY RECAP *************************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=9    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```
Figure 5 Jinja created fabric sites
![Alt text](./images/fabric_sites_with_jinja.png)

## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring fabric sites and fabric zones and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.
