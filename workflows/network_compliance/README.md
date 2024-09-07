# Network Compliance Workflow Playbook
Workflow Playbook for Assigning devices to sites network complianceing, Re-network complianceing and Deleteing the devices in Inventory. 
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

network_compliance_details  defines the list of devices and devices details for the devices to be run rough the playbooks


To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/network compliance_workflow_manager/


To run this workflow, you follow the README.md 

##Example run:

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml --e VARS_FILE_PATH=../vars/network_compliance_workflow_inputs.yml -vvvv

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
User Inputs for Users and roles are stored in  workflows/network compliance/vars/network_compliance_workflow_inputs.yml

##Validate user input before running though ansible
```bash
(pyats) dnac_ansible_workflows % ./tools/validate.sh -s workflows/network_compliance/schema/network_compliance_workflow_schema.yml -d workflows/network_compliance/vars/network_compliance_workflow_inputs.yml 
workflows/network compliance/schema/network_compliance_workflow_schema.yml
workflows/network compliance/vars/network_compliance_workflow_inputs.yml
yamale   -s workflows/network compliance/schema/network compliance_workflow_schema.yml  workflows/network_compliance/vars/network_compliance_workflow_inputs.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/vars/network compliance_workflow_inputs.yml...
Validation success! 👍
```
