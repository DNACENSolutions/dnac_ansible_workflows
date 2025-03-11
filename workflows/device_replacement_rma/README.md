
# Catalyst Center Return Material Authorization Playbook:

## Return Material Authorization (RMA) Overview

The Return Material Authorization (RMA) workflow lets you replace failed devices quickly. RMA provides a common workflow to replace routers, switches, and APs.

For more information , Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/user_role_workflow_manager/

## Configure Environment
- Update hosts.yml with the connection details of your DNA Center instance. 

```bash
catalyst_center_hosts:
    hosts:
        catalyst_center220:
            catalyst_center_host: xx.xx.xx.xx.
            catalyst_center_password: XXXXXXXX
            catalyst_center_port: 443
            catalyst_center_timeout: 60
            catalyst_center_username: admin
            catalyst_center_verify: false
            catalyst_center_version: 2.3.7.6
            catalyst_center_debug: true
            catalyst_center_log_level: INFO
            catalyst_center_log: true
```


## Please ensure the following conditions are met before proceeding with the verification of the RMA (Return Merchandise Authorization) workflow:

1. The software image version of the faulty device must be imported in the image repository before marking the device for replacement.
2. The faulty device must be in an unreachable state.
3. If the replacement device onboards to Catalyst Center through Plug and Play (PnP), the faulty device must be assigned to a user-defined site.
4. The replacement device must not be in a provisioning state while triggering the RMA workflow.
5. For switch stacks replacement, the number of stacks for the faulty and replacement device must be the same.

## The Steps coverd by the automation
1. Mark the faulty device for replacement
    From the top-left corner, click the menu icon and choose Provision > Inventory.
    From the Actions drop-down list, choose Inventory > Device Replacement > Mark Device for Replacement.
    In the Mark for Replacement window, click Mark.
    Figure1: Mark Faulty Device for replacement UI
    ![Alt text](./images/mark_device_replacement.png)

2. To replace the device, do the following:
    Select the device that you want to replace and choose Actions > Replace Device.
    In the Choose Replacement Device window, choose a replacement device from the Unclaimed tab or the Managed tab.

    The Unclaimed tab shows the devices that are onboarded through PnP. The Managed tab shows the devices that are onboarded through the Inventory or the discovery process.
    If the replacement device is not yet onboarded, do the following:
    In the Choose Replacement Device window, click Add Device.
    In the Add New Device window, enter the Serial Number of the device and click Add New Device.
    In the Choose Replacement Device window, click Sync with Smart Account.
    In the Sync with Smart Account window, click Sync.
    The Automation does not support scheduling through Catalyst Center. 
    User should schedule their script run from automation.
    ![Alt text](./images/replacement.png)

## Inputs:
```yaml
---
catalyst_center_version: 2.3.7.6
rma_devices: 
  - faulty_device_serial_number: "KWC224709LV"
    replacement_device_serial_number: "KWC2333037V"
```

```yaml
---
catalyst_center_version: 2.3.7.6
rma_devices: 
  - faulty_device_ip_address: "204.192.3.40"
    replacement_device_ip_address: "204.1.2.5"
```

```yaml
---
catalyst_center_version: 2.3.7.6
rma_devices: 
  - faulty_device_name: "SJ-EN-9300.cisco.local"
    replacement_device_name: "SJ-EN-9300.cisco-1.local"
```

## Validate the inputs:
```bash
yamale -s workflows/device_replacement_rma/schema/device_replacement_rma_schema.yml workflows/device_replacement_rma/vars/device_replacement_rma_input.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/device_replacement_rma/vars/device_replacement_rma_input.yml...
Validation success! 👍
```
## Run Playbook with input:

```bash
ansible-playbook -i host_inventory_dnac1 workflows/device_replacement_rma/playbook/device_replacement_rma_playbook.yml --e VARS_FILE_PATH=../vars/device_replacement_rma_input.yml  -vvv
```

## Run playbook with state set to deleted
```bash
ansible-playbook -i host_inventory_dnac1 workflows/device_replacement_rma/playbook/delete_device_replacement_rma_playbook.yml --e VARS_FILE_PATH=../vars/device_replacement_rma_input.yml  -vvv
```

3. Unmark the faulty devicew replacement
    If you your faulty device came up and is not more required to be replace, you can un marked the already marked faulty device from replacement as below. 
    From the Inventory drop-down list, choose Marked for Replacement.
    A list of devices that are marked for replacement is displayed.
    If you don't want to replace the device, select the device and choose Actions > Unmark for Replacement.
    Figure3: Mark Faulty Device for replacement UI
    ![Alt text](./images/unmark_faulty_device.png)


## References
  \* Note: The environment is used for the references in the above instructions.
  ```
  dnacentersdk: 2.8.3
  cisco.dnac: 6.30.0
  dnac version: 2.3.7.6



