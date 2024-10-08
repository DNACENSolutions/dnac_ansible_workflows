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


## How to Validate Input

* Use `yamale`:

```bash
yamale -s workflows/device_templates/schema/template_workflow_schema.yml workflows/device_templates/vars/template_workflow_inputs.yml 
Validating /Users/pawansi/dnac_ansible_workflows/workflows/device_templates/vars/template_workflow_inputs.yml...
Validation success! 👍
```

## How to Run
* Execute the Ansible Playbook to add, update, provision devices:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_templates/playbook/template_workflow_playbook.yml --e VARS_FILE_PATH=../vars/template_workflow_inputs.yml
```

*  How to Delete Existing Devices from inventory
*  Run the Delete Playbook:
```bash
    ansible-playbook -i host_inventory_dnac10_195_243_53/hosts.yml workflows/device_templates/playbook/delete_template_workflow_playbook.yml --e VARS_FILE_PATH=../vars/template_workflow_inputs.yml
```
##  Important Notes
* Always refer to the detailed input specification for comprehensive information on available options and their structure.