# Workflow Playbook for Device Config Backup
This Ansible playbook automates the process of backing up device configurations in your network inventory. It is designed to work with Catalyst Center Release version 2.3.7.6 or later.

# Key Points:
## Supported Catalyst Center Version: 
2.3.7.6 and above
## Workflow Definition: 
device_configs_backup_details specifies the devices and their details to include in the backup.
## Full Workflow Specification: 
Refer to the official documentation for detailed information on defining workflows: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/device_configs_backup_workflow_manager

# Procedure
1. ## Prepare your Ansible environment:
Install Ansible if you haven't already
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

2. ## Configure Host Inventory:
The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
## The Sample host_inventory_dnac1/hosts.yml
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
3. ## Generate your Input:
The workflows/device_config_backup/vars/device_config_backup_workflow_input.yml file should be configured with device details
Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/device_configs_backup_workflow_manager


4. ## Validate Input (Recommended):
Validate the input with schema using yamale
```bash
yamale -s workflows/device_config_backup/schema/device_config_backup_workflow_schema.yml workflows/device_config_backup/vars/device_config_backup_workflow_input.yml
```

# Example run:
5. ## Collect device running configurations through Catalyst Center APIs.
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_config_backup/playbook/device_config_backup_workflow_playbook.yml --e VARS_FILE_PATH=../vars/device_config_backup_workflow_input.yml -vvvv
```

# Important Notes:
1. Ensure the Catalyst Center version is compatible.
2. Carefully configure inventory and input variables.
3. Validate input using yamale to prevent errors.
4. Review execution logs for troubleshooting.
