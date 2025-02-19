# Workflow Playbook for Device Config Backup
### Overview

This Ansible playbook automates the process of backing up device configurations in your network inventory. It is designed to work with Catalyst Center Release version 2.3.7.6 or later.

The device configuration backup workflow in Cisco Catalyst Center focuses on creating backups of device configurations. The primary function of this workflow is to ensure that device configurations are backed up and stored securely for future reference or restoration.

### Features

- Backup device configurations using hostnames.
- Backup device configurations without requiring passwords.
- Backup device configurations for all devices.
- Backup device configurations using site names.

### Important Notes:
1. Ensure the Catalyst Center version is compatible.
2. Carefully configure inventory and input variables.
3. Validate input using yamale to prevent errors.
4. Review execution logs for troubleshooting.


## 
## I. Key Points:
### Supported Catalyst Center Version: 
2.3.7.6 and above
### Workflow Definition: 
device_configs_backup_details specifies the devices and their details to include in the backup.
### Full Workflow Specification: 
Refer to the official documentation for detailed information on defining workflows: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/device_configs_backup_workflow_manager

## II. Procedure
### Prepare your Ansible environment:
Install Ansible if you haven't already
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

### Configure Host Inventory:
The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
#### **The Sample host_inventory_dnac1/hosts.yml**
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

### Define Schema:
The workflows/device_config_backup/vars device_config_backup_workflow_input.yml file stores the sites details you want to configure

```bash
catalyst_center_version: 2.3.7.6
catalyst_center_task_timeout: 1200
catalyst_center_task_poll_interval: 60

# Network Settings an IP Pools design.
device_configs_backup_details_type:
  collection_status: str(required=False)
  family: str(required=False)
  file_password: str(required=False)
  file_path: str(required=False)
  hostname_list: str(required=False)
  ip_address_list: str(required=False)
  mac_address_list: str(required=False)
  serial_number_list: str(required=False)
  series: str(required=False)
  site_list: str(required=False)
  type: str(required=False)
  unzip_backup: bool(required=False)
```

### Generate your Input:
The workflows/device_config_backup/vars/device_config_backup_workflow_input.yml file should be configured with device details
Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/device_configs_backup_workflow_manager


### Validate Input (Recommended):
Validate the input with schema using yamale
```bash
yamale -s workflows/device_config_backup/schema/device_config_backup_workflow_schema.yml workflows/device_config_backup/vars/device_config_backup_workflow_input.yml
```

### Example run:
#### **Collect device running configurations through Catalyst Center APIs.**
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_config_backup/playbook/device_config_backup_workflow_playbook.yml --e VARS_FILE_PATH=../vars/device_config_backup_workflow_input.yml -vvvv
```

## III. Detailed steps to perform

### 1. Take Backup Using Hostname

#### **Mapping config to UI Actions**

The config parameter within this task corresponds to the Provision > Inventory > Actions > Export Inventory" action in the Cisco Catalyst Center UI.

![alt text](./images/hostname.png)


#### **Example Input**

```
hostname:
  - file_password: qsaA12!asdasd
    hostname_list: ['DC-T-9300.cisco.local','SJ-IM-1-9300.abc.com','SJ-EN-10-9300.cisco.local']
    file_path: backup
```

- file_password: The password used to encrypt the backup file.
- hostname_list: A list of hostnames for which the device configurations will be backed up.
- file_path: The directory path where the backup files will be stored.


### 2. Take Backup Without Defined Passwords


#### **Example Input **

```
device_configs_backup_details:
  - hostname_list: ['DC-T-9300.cisco.local']
    file_path: "./"
```
- hostname_list: A list of hostnames for which the device configurations will be backed up.
- file_path: The directory path where the backup files will be stored.

### 3. Take Backup with ip_address_list unzip

#### **Example Input **

```
device_configs_backup_details:
  - ip_address_list: 204.1.2.2
    file_path: "./"
    unzip_backup: true
```

### 4. Take Backup Using collection_status and ip_address_list

#### **Example Input **

```
device_configs_backup_details:
  - ip_address_list: 204.1.2.1
    collection_status: Managed
    file_path: "./"
    unzip_backup: false
```




## IV. References

Note: The environment is used for the references in the above instructions.

```
  ansible: 9.9.0
  ansible-core: 2.16.10
  ansible-runner: 2.4.0

  dnacentersdk: 2.8.3
  cisco.dnac: 6.29.0
  ansible.utils: 5.1.2
```