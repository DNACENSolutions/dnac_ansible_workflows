# USERS AND ROLES Workflow
Workflow Playbook for configuring and updating Role based access control
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

user_details  defines the login, password, and role (permissions) of a user.

roledetails defines the accesss destails for the role.

To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/user_role_workflow_manager/


To run this workflow, you follow the README.md 

##Example run:

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/users_and_roles_workflow_playbook.yml --e VARS_FILE_PATH=../vars/users_and_roles_workflow_inputs.yml -vvvv


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
User Inputs for Users and roles are stored in  workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml

##Validate user input before running though ansible
```bash
    (pyats)  dnac_ansible_workflows % ./tools/validate.sh -s workflows/users_and_roles/schema/users_and_roles_workflow_schema.yml -d workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml                             
    workflows/users_and_roles/schema/users_and_roles_workflow_schema.yml
    workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml
    yamale   -s workflows/users_and_roles/schema/users_and_roles_workflow_schema.yml  workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml
    Validating /Users/pawansi/dnac_ansible_workflows/workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml...
    Validation success! 👍
```

