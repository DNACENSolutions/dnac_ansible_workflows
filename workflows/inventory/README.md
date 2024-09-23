# Ansible Workflow: Inventory Workflow Manager

This Ansible workflow automates various inventory management tasks within your network, streamlining device and port configuration.

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
* Provision Device (assign devices to sites and provision wired/wireless devices)
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

## How to Run
* Execute the Ansible Playbook to add, update, provision devices:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/inventory/playbook/inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_vars.yml
```

*  How to Delete Existing Devices from inventory
*  Run the Delete Playbook:
```bash
    ansible-playbook -i host_inventory_dnac10_195_227_14/hosts.yml workflows/inventory/playbook/delete_inventory_playbook.yml --e VARS_FILE_PATH=../vars/inventory_delete_devices.yml
```
##  Important Notes
* Always refer to the detailed input specification for comprehensive information on available options and their structure.