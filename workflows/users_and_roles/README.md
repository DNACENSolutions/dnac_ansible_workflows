# User Profile Roles and Permissions
Catalyst Center supports role-based access control (RBAC). The roles assigned to a user profile define the capabilities that a user has permission to perform. Catalyst Center has three main default user roles:
SUPER-ADMIN-ROLE
NETWORK-ADMIN-ROLE
OBSERVER-ROLE
The SUPER-ADMIN-ROLE gives users broad capabilities and permits them to perform all actions in the Catalyst Center GUI, including creating custom roles and assigning them to user profiles. The NETWORK-ADMIN-ROLE and the OBSERVER-ROLE have more limited and restricted capabilities in the Catalyst Center GUI.
# Configure Role-Based Access Control
Catalyst Center supports role-based access control (RBAC), which enables a user with SUPER-ADMIN-ROLE privileges to define custom roles that permit or restrict user access to certain Catalyst Center functions.

Use this procedure to define a custom role and then assign a user to that role.

## Before you begin
Only a user with SUPER-ADMIN-ROLE permissions can perform this procedure.

## Procedure
### Step 1 Define a custom role.
In role_details Section define the custome roles with necessary permissions.
for Reference check sample inputs at vars/users_and_roles_workflow_inputs.yml
```bash
  role_details:
    - role_name: Assurance-role
      description: With write access overall
      assurance:
        - overall: write
          monitoring_and_troubleshooting: read

```
### Step 2 To assign a user to the custom role you just created
Under users details add your users with role list give the list of all roles listed.
```bash
  user_details:
    - username: xxxxxxx
      first_name: Pawan
      last_name: Singh
      email: xxxxxxw@example.com
      password: xxxxx@123!45
      role_list: 
        - Admin_customized_role
        - Assurance-role
```
# USERS AND ROLES Workflow
Workflow Playbook for configuring and updating Role based access control
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

user_details  defines the login, password, and role (permissions) of a user.

role_details defines the accesss destails for the role.

To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/user_role_workflow_manager/

To run this workflow, you follow the README.md 

##Example run: (Create and Update users and ROle)

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/users_and_roles_workflow_playbook.yml --e VARS_FILE_PATH=../vars/users_and_roles_workflow_inputs.yml -vvvv

##Example run: Delete Users and Role

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/delete_users_and_roles_workflow_playbook.yml --e VARS_FILE_PATH=../vars/users_and_roles_workflow_inputs.yml -vvvv

# Modify Roles and Users
## Allowed to make changed to users and roles, like changing the passwords of the users to apply password policy, providing more permission to users or revoling some permissions etc, On the role side enabling certail read or write addess for the custom roles. 
### Procedure
Make amendment to your roles and users and rerun the input and through the workflow playbook. The Modification will reflect in the Catalyst Cennter Post success full workflow playbook execution.

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

