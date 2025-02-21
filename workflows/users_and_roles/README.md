# Ansible User and Role Workflow Manager Guide for Cisco Catalyst Center

This guide provides an overview of how to use the **Ansible playbook** to automate user and role management workflows on **Cisco Catalyst Center**. The playbook utilizes the `cisco.dnac.user_role_workflow_manager` module to interact with Cisco Catalyst Center and perform tasks related to **creating**, **updating**, and **managing** users and roles.

## Overview of User and Role Management Functions

The user and role management workflow in Cisco Catalyst Center focuses on:

- **Creating** and **managing users**
- **Assigning roles**
- Configuring **role-based access control (RBAC)**


### Task: Create SUPER-ADMIN-ROLE User

This task creates a user with the **SUPER-ADMIN-ROLE** in **Cisco Catalyst Center**.

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **System > Users & Roles** action in the Cisco Catalyst Center UI. It initiates the creation of a user with the specified role.

![Alt text](image.png)

```yaml
      user_details:
        - username: super-admin
          email: "super_admin@example.com"
          password: xxxx
          role_list: ["SUPER-ADMIN-ROLE"]
```
### Task: Create NETWORK-ADMIN-ROLE User

This task creates a user with the **NETWORK-ADMIN-ROLE** in **Cisco Catalyst Center**.

```yaml
      user_details:
        - username: network-admin
          email: "network_admin@example.com"
          password: xxxx
          role_list: ["NETWORK-ADMIN-ROLE"]
```
### Task: Create OBSERVER-ROLE User

This task creates a user with the **OBSERVER-ROLE** in **Cisco Catalyst Center**.

```yaml
      user_details:
        - username: observer
          email: "observer@example.com"
          password: xxxx
          role_list: ["OBSERVER-ROLE"]
```

### Task: Create Default User

This task creates a user with the **Default** in **Cisco Catalyst Center**.

```yaml
      user_details:
        - username: default
          email: "default@example.com"
          password: xxxx
```

### Task: Create Multiple User

This task creates a user with the **Multiple** in **Cisco Catalyst Center**.

```yaml
- name: Create user
      user_details:
        - username: Admin_multiple
          email: "super_admin_multiple@example.com"
          password: xxxx
          role_list: ["SUPER-ADMIN-ROLE"]
        - username: Network-admin_multiple
          email: "net_admin_multiple@example.com"
          password: xxxx
          role_list: ["NETWORK-ADMIN-ROLE"]
        - username: Observer_multiple
          email: "observer_multiple@example.com"
          password: xxxx
          role_list: ["OBSERVER-ROLE"]
        - username: Guest
          email: "guest@example.com"
          password: xxxx
          role_list: ["SUPER-ADMIN-ROLE","NETWORK-ADMIN-ROLE","OBSERVER-ROLE"]
```

## Default Roles

* **SUPER-ADMIN-ROLE:** Grants full access to all Catalyst Center features, including creating custom roles.
* **NETWORK-ADMIN-ROLE:** Provides limited access for network administration tasks.
* **OBSERVER-ROLE:** Restricts access to view-only capabilities.

## Custom Role Creation

Users with the SUPER-ADMIN-ROLE can create custom roles to fine-tune access permissions.

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
3. ## Define User and Role Data:
The workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml file stores the user and role details you want to configure.
Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/user_role_workflow_manager/
### Define the Custom Role
User Inputs for Users and roles are stored in  workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml

Use the `role_details` section in your YAML configuration to define the role's name, description, and specific permissions.
   **Example:**
```yaml
role_details:
    - role_name: Assurance-role
    description: With write access overall
    assurance:
        - overall: write
        monitoring_and_troubleshooting: read
```
assign roles to the users
### Assign Users to the Role
In the user_details section, add users and specify their assigned roles in the role_list.
   **Example:**
```yaml
user_details:
- username: xxxxxxx
    first_name: Pawan
    last_name: Singh
    email: xxxxxxw@example.com
    password: xxxxx@123!45
    role_list: 
    - Admin_customized_role
    - Assurance-role
- username: "ajithandrewj"
    first_name: "ajith"
    last_name: "andrew"
    email: "ajith.andrew@example.com"
    role_list: ["SUPER-ADMIN-ROLE"]
```


## Validate Your Input:
##Validate user input before running though ansible
```command
yamale -s workflows/users_and_roles/schema/users_and_roles_workflow_schema.yml      workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml
```

Use the provided validation script to ensure your YAML input file adheres to the required schema.
## Execute the Playbook:
Run the create Playbook
```bash
    ansible-playbook -i inventory/iac2/host.yml  workflows/users_and_roles/playbook/users_and_roles_workflow_playbook.yml --e  VARS_FILE_PATH=../vars/users_and_roles_workflow_inputs.yml > logs/userrole.log -vvvvv 
```
Post the user and the roles will start reflecting in the catalyst center.

## Running playbook with passowrd in Ansible vault. 
Create your password file in folder: valted_passwords/<filename>
write your password in yaml format there example

---
test_password: sample123

### Generate encrypt the password file
```bash
    ansible-vault encrypt valted_passwords/<filename>
```
It will ask valt password, setup and remember it
in jinja template in jinja_template folder update your valt passowrd file
passwords_file: ../../../valted_passwords/mypasswordfile.yaml

### Run playbook with jinja template and Valt password
```bash
    dnac_ansible_workflows % ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/users_and_roles_workflow_playbook.yml --ask-vault-pass --e VARS_FILE_PATH=../jinja_template/template_users_and_roles_workflow_inputs.j2 -vvvv
```
it will prompt for valt password. Enter the val password which was used to encrypt the password. 
Alternatively:
1. Create valt password hidden file:
~/.vault_secret.sh

## file content:
```bash
#!/bin/bash
echo password
```
2. Add permissions to execute:
```bash
chmod 711 ~/.vault_secret.sh
```

3. Add to ansible.cfg: 
```bash
vi ~/.ansible.cfg
[defaults]
vault_password_file=~/.vault_secret.sh
```
4. Execute:
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/users_and_roles_workflow_playbook.yml --e VARS_FILE_PATH=../vars/users_and_roles_workflow_jinja_input.yml  -vvvv
```

## Deleting the users and the roles
Playbook can be used to delete roles and users
Run the delete Playbook
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/users_and_roles/playbook/delete_users_and_roles_workflow_playbook.yml --e VARS_FILE_PATH=../vars/users_and_roles_workflow_inputs.yml -vvvv
```
Roles and Users will get deleted from the Catalyst Center
