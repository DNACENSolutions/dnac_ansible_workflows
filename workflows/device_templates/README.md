# Ansible Workflow: Device Template Workflow Manager

This Ansible workflow automates crating and managing template projects, device templates and deploying the templates to the devices. One of the many powerful features of Cisco's DNA Center is its templating engine. You can configure nearly your entire network from here.

## Detailed Input Spec
Refer to: [https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/template_workflow_manager/](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/template_workflow_manager/)

## Template Workflow Manager Description

### Main Tasks

*  Manage operations create, update and delete of the resource Configuration Template.
*    API to create a template by project name and template name.
*    API to update a template by template name and project name.
*    API to delete a template by template name and project name.
*    API to export the projects for given projectNames.
*    API to export the templates for given templateIds.
*    API to manage operation create of the resource Configuration Template Import Project.
*    API to manage operation create of the resource Configuration Template Import Template.
*  Deploy Templates to devices with device specific parameters.

# Procedure
1. ## Prepare your Ansible environment:

Install Ansible if you haven't already
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git
2. ## Configure Host Inventory:
The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
##The Sample host_inventory_dnac1/hosts.yml

```bash
catalyst_center_hosts:
    hosts:
        catalyst_center220:
            dnac_host: xx.xx.xx.xx.
            dnac_password: XXXXXXXX
            dnac_port: 443
            dnac_timeout: 60
            dnac_username: admin
            dnac_verify: false
            dnac_version: 2.3.7.6
            dnac_debug: true
            dnac_log_level: INFO
            dnac_log: true
```
3. ## Define Playbook input:
The /vars/template_workflow_inputs.yml file stores the sites details you want to configure.

```bash
template_details:
    - configuration_templates:
        author: Pawan Singh
        composite: false
        custom_params_order: true
        description: Template to configure Access Vlan n Access Interfaces
        device_types:
        - product_family: Switches and Hubs
        product_series: Cisco Catalyst 9300 Series Switches
        product_type: Cisco Catalyst 9300 Switch
        failure_policy: ABORT_TARGET_ON_ERROR
        language: VELOCITY
        name: access_van_template_9300_switches
        project_name: access_van_template_9300_switches
        project_description: This project contains all the templates for Access Switches
        software_type: IOS-XE
        software_version: null
        template_name: PnP-Upstream-SW
        template_content: |
        vlan $vlan
        interface $interface
        switchport access vlan $vlan
        switchport mode access
        description $interface_description
        version: "1.0"
    - configuration_templates:
      name: PnP-Upstream-SW
      template_name: PnP-Upstream-SW
      project_name: Onboarding Configuration
      tags: []
      author: admin
      device_types:
        - product_family: Switches and Hubs
          product_series: Cisco Catalyst 9500 Series Switches
        - product_family: Switches and Hubs
          product_series: Cisco Catalyst 9300 Series Switches
      software_type: IOS-XE
      language: VELOCITY
      template_content: 
        vlan $vlan
        interface $interface
        switchport access vlan $vlan
        switchport mode access
        description $interface_description
    
deploy_device_details:
    - host_name: SJC-Switch-1
      management_ip: 10.1.1.1
      site_name: Global/USA/SAN JOSE/BLD23
      device_role: ACCESS
      device_tag: all_9300_Access_tag1
      device_template_params:
          - param_name: "vlan"
            param_value: "100"
          - param_name: "interface"
            param_value: "TwoGigabitEthernet1/0/2"
          - param_name: "interface_description"
            param_value: "Access Port"
```
4. ## How to Validate Input

* Use `yamale`:

```bash
yamale -s workflows/device_templates/schema/template_workflow_schema.yml workflows/device_templates/vars/template_workflow_inputs.yml 
Validating /Users/pawansi/dnac_ansible_workflows/workflows/device_templates/vars/template_workflow_inputs.yml...
Validation success! 👍
```

5. ## How to Run
* Execute the Ansible Playbook to add, update, provision devices:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_templates/playbook/template_workflow_playbook.yml --e VARS_FILE_PATH=../vars/template_workflow_inputs.yml
```

*  How to Delete Existing Devices from inventory
*  Run the Delete Playbook:
```bash
    ansible-playbook -i host_inventory_dnac10_195_243_53/hosts.yml workflows/device_templates/playbook/delete_template_workflow_playbook.yml --e VARS_FILE_PATH=../vars/template_workflow_inputs.yml
```
6. ##  Important Notes
* Always refer to the detailed input specification for comprehensive information on available options and their structure.