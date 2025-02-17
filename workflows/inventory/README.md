# Ansible Workflow: Inventory Workflow Manager

This Ansible workflow automates various inventory management tasks within your network, streamlining device and port configuration.

inventory_details defines the list of devices and device details for the devices to be run through the playbooks.

This workflow playbook is used for adding devices, assign devices to sites and provision, updating the devices, resync and reboot the devices, changing device roles and Deleteing the devices in Inventory. 

## Detailed Input Spec

Refer to: [https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/inventory_workflow_manager/](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/inventory_workflow_manager/)

## Inventory Description

### Main Tasks

* Add User-Defined Fields to a Device
* Add Network Device
* Change the Device Role in inventory
* Update Computed Device Credentials
* Update a Device's Management IP Address
* Update the Device Polling Interval
* Delete a Network Device
* Manage Port Details
* Provision Device (assign devices to sites and provision wired devices)
* Resync and reboot the devices
* Manage Port Details
* **To manage the port's admin status:**
    * **Port Shut:** To shut down the port and change its admin status to Down.
    * **Port No Shut:** To enable the port.
    * **Clear MAC Address:** To clear the port's MAC address.
    * To activate an error-disabled port, clear the MAC address and shut down the port.

* **To edit certain port details (port description, Access VLAN, Voice VLAN), use the following:**

| Name         | Description                                                                                                                                                              |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Access VLAN  | Provide access VLAN to assign to the port. (Cannot update access VLAN for ports with two preconfigured access VLANs)                                                  |
| Voice VLAN   | Provide a voice VLAN                                                                                                                               |
| Port Description | Enter or modify the port description. Delete the description by providing an empty port description.                                                                      |


## How to Validate Input

* Use `yamale`:

```bash
yamale -s workflows/inventory/schema/inventory_schema.yml workflows/inventory/vars/inventory_vars.yml 
Validating /Users/pawansi/dnac_ansible_workflows/workflows/inventory/vars/inventory_vars.yml...
Validation success! 👍
```

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
## Description of Vars in `hosts.yml`

    - **dnac_host**: IP address of the Catalyst Center.  
    - **dnac_username**: Catalyst Center login username.  
    - **dnac_password**: Catalyst Center login password.  
    - **dnac_version**: Catalyst Center version.  
    - **dnac_port**: Port number to which Catalyst Center listens.  
    - **dnac_timeout**: Timeout for API requests made to Catalyst Center.  
    - **dnac_verify**: Indicates whether to verify the SSL certificate of Catalyst Center.  
    - **dnac_debug**: Enables or disables debug mode.  
    - **dnac_log**: Enables or disables logging for Catalyst Center. 

3. ## Define Playbook input:

The workflow/inventory/vars/inventory_vars.yaml file stores the device details you want to add to catalyst center.
Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/inventory_workflow_manager/
```bash
---
# Provide the Catalyst Center Version
catalyst_center_version: 2.3.7.6
# This file contains the variables for the inventory workflow
inventory_details:
  network_devices:
  - ip_address_list: ["204.101.16.1","1.1.1.1", "2.2.2.2"]
    cli_transport: ssh
    compute_device: False
    password: Test@123
    enable_password: Test@1234
    extended_discovery_info: test
    http_username: "testuser"
    http_password: "test"
    http_port: "443"
    http_secure: False
    netconf_port: 830
    snmp_auth_passphrase: "Lablab@12"
    snmp_auth_protocol: SHA
    snmp_mode: AUTHPRIV
    snmp_priv_passphrase: "Lablab@123"
    snmp_priv_protocol: AES256
    snmp_retry: 3
    snmp_timeout: 5
    snmp_username: v3Public
    snmp_version: v3
    type: NETWORK_DEVICE
    username: cisco
```

## How to Run

Execute: Execute the playbooks with your inputs and Inventory, specify your input file using the --e variable VARS_FILE_PATH

## To execute the Ansible Playbook for adding devices:
* After the successful execution you will get the below message.
"device(s) '204.101.16.1', '1.1.1.1', '2.2.2.2' added successfully in Cisco Catalyst Center."
* verify the devices is successfully added to the inventory and present in the UI.
![alt text](images/add_devices.png)
* To run the add Devices Playbook:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/inventory/playbook/inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_vars.yml
```

## To execute the Ansible playbook for provision devices:
* After the successful execution you will get the below message.
"device(s) '137.1.3.1', '137.1.3.2', '137.1.3.3', '137.1.3.4', '137.1.3.5' provisioned successfully in Cisco Catalyst Center."
* verify the devices provision status in the UI and it will show provision status as success.
![alt text](images/provision_device.png)
*  To run the Provision Playbook:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/inventory/playbook/inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_provision_devices.yml
```

## To execute the Ansible playbook for resync/reboot devices:
* After the successful execution you will get the below message.
"Device(s) '['137.1.1.1', '137.1.1.2']' have been successfully resynced in the inventory in Cisco Catalyst Center."
*  To run the Resync/Reboot Playbook:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/inventory/playbook/inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_resync_reboot_vars.yml
```

## To execute the Ansible playbook for deleting devices.:
*  How to Delete Existing Devices/Provisioned devices from inventory
* After the successful execution you will get the below message.
"device(s) '204.101.16.1', '1.1.1.1', '2.2.2.2' successfully deleted in Cisco Catalyst Center"
*  To run the Delete Playbook:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/inventory/playbook/delete_inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_delete_devices.yml
```
## Parameters:

- `-i`: Specifies the inventory file containing host details.  
- `--e VARS_FILE_PATH`: Path to the variable file containing workflow inputs.  
- `-vvvv`: Enables verbose mode for detailed output. 

##  Important Notes
* Always refer to the detailed input specification for comprehensive information on available options and their structure.