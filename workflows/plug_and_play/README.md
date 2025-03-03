# Plug and Play Provisioning Ansible Playbook

## **Overview**

**PnP** (Plug-and-Play) is a network deployment solution that simplifies the process of onboarding new devices by automatically assigning configurations and images to new network devices upon discovery. This automation can be driven by **Cisco Catalyst Center** via **Ansible Playbooks** to handle various deployment scenarios, including:

- **Routers**
- **Switches**
- **Wireless LAN Controllers (WLCs)**
- **Access Points (APs)**

## Prerequisites

Before starting, ensure the following requirements are met:
- **Access to Cisco Catalyst Center (DNAC)**: Ensure that PnP (Plug-and-Play) is enabled. 
- **Devices that Support PnP**: Confirm that the devices you intend to onboard are PnP-capable.
- **Ansible Installation**: Ansible must be installed on the machine managing the automation process.
- **Cisco DNA Ansible Collection**: The `cisco.dnac.pnp_workflow_manager` module must be available from the Cisco DNA Ansible Collection.
- **dnacentersdk Python SDK**: This SDK is required to interact with Cisco Catalyst Center.
- **Ansible installation**: Ensure that Ansible is installed.
- **Yamale Python Library**: The `yamale` Python library installed (`pip install yamale`)
- **Cisco DNA Center or Plug and Play Connect Access**: Ensure access is configured

## **Key Features**

* **Zero-Touch Provisioning:** Remotely configure devices onboarded through PnP
* **Planned Provisioning:** Pre-configure settings and apply them when the device comes online.
* **Unclaimed Provisioning:** Discover and configure new devices that join the network unexpectedly.

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

## Overview of PnP Onboarding Process with Example
The following diagram illustrates the **PnP onboarding process**, initiated through an Ansible playbook utilizing the **cisco.dnac.pnp_workflow_manager** module. This module communicates with **Cisco Catalyst Center** via its API, enabling seamless device onboarding into the network.

## Task: Device onboarding

This task demonstrates how to add a single device to Plug and Play (PnP) without claiming it.

### Note:
- Ensure that the device is not already onboarded or claimed.

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  add_network_device:
    - device_info:
      - serial_number: FJC27212582
        hostname: DC-T-9300.cisco.local
        state: Unclaimed
        pid: C9300-48T
```

### Step 1: Execute the pnp playbook.

Run the following command to onboard the device:

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/catalyst_center_pnp_vars.yml -vvvv
```

Upon successful completion, the device is added to the plug and play.

![alt text](images/Device_added_successfully.png)

### Step 2: Verify the playbook output

Upon successful completion, you will see an msg similar to:

```bash
"failed": false,
"msg": "Only Device Added Successfully",
```

## Task: Bulk Device Onboarding

This task demonstrates how to add multiple devices in bulk. Bulk onboarding is useful when multiple devices need to be configured and onboarded simultaneously, such as in large-scale deployments.

### Note:
- This example includes router, switch and wlc devices

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  add_bulk_network_devices:
    - device_info:
      - serial_number: FXS2502Q2HC
        hostname: SF-BN-2-ASR.cisco.local
        state: Unclaimed
        pid: ASR1001-X
      - serial_number: FJC271923AK
        hostname: NY-EN-9300
        state: Unclaimed
        pid: C9300-48UXM
      - serial_number: FOX2639PAYD
        hostname: SJ-EWLC-1.cisco.local
        state: Unclaimed
        pid: C9800-40-K9      
```

### Step 1: Execute the pnp playbook.

Run the following command to onboard bulk the device:

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/catalyst_center_pnp_vars.yml -vvvv
```

Upon successful execution, all devices are added to Plug and Play (PnP).

![alt text](images/Bulk_pnp_device_addition.png)

### Step 2: Verify the playbook output

Upon successful completion, you should see a message similar to:

```bash
"failed": false,
"msg": "3 device(s) imported successfully",
```

## Task: Delete a Device from PnP

This task demonstrates how to delete a device from Plug and Play (PnP).

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  delete_network_device:
    - site_name: Global/USA/SAN JOSE/SJ_BLD23/FLOOR1
      project_name: Onboarding Configuration
      template_name: PnP-Devices_No-Vars
      image_name: cat9k_iosxe.17.09.04a.SPA.bin
      device_info:
          - serial_number: FJC271923AK
            hostname: NY-EN-9300
            state: Unclaimed
            pid: C9300-48UXM
```

### Step 1: Ensure that the device exists in Plug and Play (PnP) before executing the playbook.

![alt text](images/Device_is_present.png)

Run the following command to delete the device:

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/delete_catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/delete_catalyst_center_pnp_vars.yml -vvvv
```

### Step 2: Execute the pnp playbook.

Upon successful execution, the device will be deleted from PnP.

![alt text](images/Device_is_removed.png)

### Step 3: Verify the playbook output

Upon successful completion, you should see a message similar to:

```bash
"failed": false,
"msg": "1 Device(s) Deleted Successfully",
```

### Step 4: Verify that device is removed

To ensure the device has been successfully removed, verify the PnP UI.

![alt text](images/verify_device_deletion.png)

## Task: Bulk Device Deletion

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  delete_bulk_network_devices:
    - device_info:
      - serial_number: FXS2502Q2HC
        hostname: SF-BN-2-ASR.cisco.local
        state: Unclaimed
        pid: ASR1001-X
      - serial_number: FJC271923AK
        hostname: NY-EN-9300
        state: Unclaimed
        pid: C9300-48UXM
      - serial_number: FOX2639PAYD
        hostname: SJ-EWLC-1.cisco.local
        state: Unclaimed
        pid: C9800-40-K9
```

### Step 1: Ensure that the device exists in Plug and Play (PnP) before trying to remove them.

![alt text](images/All_devices_present.png)

### Step 2: Execute the PnP Playbook:

Run the following command to delete the device:

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/delete_catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/delete_catalyst_center_pnp_vars.yml -vvvv
```

Upon successful execution, the device will be deleted from PnP.

![alt text](images/Device_is_removed.png)

### Step 3: Verify the playbook output

Upon successful completion, you should see a message similar to:

```bash
"failed": false,
"msg": "3 Device(s) Deleted Successfully",
```

### Step 4: Verify that all devices is removed

To ensure the devices has been successfully removed, verify the PnP UI.

![alt text](images/All_devices_get_removed.png)


## Task: Claiming a Cisco Catalyst 9K Switch

This task demonstrates how to add and claim a Cisco Catalyst 9K switch using the Plug and Play (PnP)

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  claim_switching_devices:
      - site_name: Global/USA/SAN JOSE/SJ_BLD21
        project_name: Onboarding Configuration
        template_name: PnP-Devices-SW
        image_name: cat9k_iosxe.17.12.04.SPA.bin
        template_params:
          PNP_VLAN_ID: 2000
          LOOPBACK_IP: 204.1.2.100
        device_info:
          - serial_number: FJC272127LW
            hostname: DC-FR-9300.cisco.local
            state: Unclaimed
            pid: C9300-48T
```

### Step 1: Execute the PnP playbook

To initiate the device onboarding and claim process execute the PnP workflow playbook using below command.

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/catalyst_center_pnp_vars.yml -vvvv
```

### Step 2: Verify the playbook output 

Ensure that no failures are observed after playbook execution complete.

### Step 3: Confirm Device Onboarding in Cisco Catalyst Center

Verify that the device is onboarded and successfully claimed in the Cisco Catalyst Center UI.

### Mapping Example to UI Actions

#### The screenshots below demonstrate how to manually onboard and claim a device in the Cisco Catalyst Center UI:

![alt text](images/claim_switch_device_img1.png)
![alt text](images/claim_switch_device_img2.png)
![alt text](images/claim_switch_device_img3.png)
![alt text](images/claim_switch_device_img4.png)
![alt text](images/clain_switch_device_img5.png)
![alt text](images/claim_switch_device_img6.png)


## Task: Claiming a Cisco Catalyst 9K Switch Stack

Similar to the task for claiming a single switch, this task relies on a predefined configuration template in Cisco Catalyst Center. However, in this case, the **StackSwitch** option is selected in the UI to indicate that the device being onboarded is part of a switch stack.

![alt text](images/Claim_siwtch_stack_9k.png)

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  claim_cat9k_switch_stack:
    - site_name:  Global/USA/New York/NY_BLD1
      project_name: Onboarding Configuration
      template_name: PnP-Devices-SW
      image_name: cat9k_iosxe.17.12.02.SPA.bin
      template_params:
        PNP_VLAN_ID: 2005
        LOOPBACK_IP: 204.1.2.2
      device_info:
        - serial_number: FJC271925Q1
          hostname: NY-EN-9300
          state: Unclaimed
          pid: C9300-48UXM
      pnp_type: StackSwitch
```

### Step 1: Execute the PnP playbook

Run the PnP workflow playbook to initiate the onboarding and claim process using below command.

```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/catalyst_center_pnp_vars.yml -vvvv
```

### Step 2: Verify the playbook output 

Ensure that the playbook execution completes successfully without any failures.

### Step 3: Confirm Device Onboarding in Cisco Catalyst Center

Verify that the switch stack is onboarded and successfully claimed in the Cisco Catalyst Center UI.

## Task: Claiming a Cisco Router Device
 
Similar to the task of claiming a single switch, we can onboard the router device as well using the pnp workflow playbook.

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  claim_router_devices:
    - site_name: Global/USA/SAN-FRANCISCO/BLD_SF1
      project_name: Onboarding Configuration
      template_name: PnP-Devices_SF-ISR_No-Vars
      image_name: isr4400-universalk9.17.12.02.SPA.bin
      device_info:
        - serial_number: FXS2502Q2HC
          hostname: SF-BN-2-ASR.cisco.local
          state: Unclaimed
          pid: ASR1001-X
```

### Note:
- Ensure that the required configurations are in place before proceeding, including: Template, Image and Device ID Certificate which is compatible to router device

![alt text](images/Claim_router_device_img1.png)

## Task: Claiming a Cisco Embedded Wireless Controller (EWLC)

In the Cisco Catalyst Center UI, onboarding a Cisco Embedded Wireless Controller (EWLC) involves specifying parameters such as the site, project, device information, and network settings. This configuration aligns with actions like assigning a site, selecting an image, and setting network interfaces.

### Note:
- Ensure that the required configurations are in place before proceeding, including: Template, Image and Catalyst Wireless LAN Controller Settings which is compatible to ewlc device

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  claim_embedded_wireless_controller:
    - site_name: Global/USA/SAN JOSE/SJ_BLD23
      project_name: Onboarding Configuration
      image_name: C9800-40-universalk9_wlc.17.12.02.SPA.bin
      template_name: PnP-Devices_SJ-EWLC
      template_params:
        MGMT_IP: 10.22.40.244
        MGMT_SUBNET: 255.255.255.0
        NTP_SERVER_IP: 171.68.38.66
      device_info:
        - serial_number: FOX2639PAYD
          hostname: SJ-EWLC-1
          state: Unclaimed
          pid: C9800-40-K9
      pnp_type: CatalystWLC
      static_ip: 204.192.50.200
      subnet_mask: 255.255.255.0
      gateway: 204.192.50.1
      ip_interface_name: TenGigabitEthernet0/0/2
      vlan_id: 2050
```

### Mapping Example to UI Actions

#### The screenshots below demonstrate how to manually onboard and claim a device in the Cisco Catalyst Center UI:

![alt text](images/Claim_ewlc_img1.png)
![alt text](images/Claim_ewlc_img2.png)
![alt text](images/Claim_ewlc_img3.png)
![alt text](images/Claim_ewlc_img4.png)
![alt text](images/Claim_ewlc_img5.png)


## Task: Claiming Multiple EWLC Devices for High Availability (HA)

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  claim_multiple_ewlc_ha:
    - site_name: Global/USA/New York/NY_BLD2
      project_name: Onboarding Configuration
      image_name: C9800-40-universalk9_wlc.17.13.01.SPA.bin
      template_name: PnP-Devices_NY-EWLC_No-Vars
      device_info:
        - serial_number: TTM2737020R
          hostname: NY-EWLC-1
          state: Unclaimed
          pid: C9800-40-K9
      pnp_type: CatalystWLC
      static_ip: 10.4.218.230
      subnet_mask: 255.255.255.240
      gateway: 10.4.218.225
      ip_interface_name: TenGigabitEthernet0/0/1
      vlan_id: 2014
    - site_name: Global/USA/New York/NY_BLD2
      project_name: Onboarding Configuration
      image_name: C9800-40-universalk9_wlc.17.13.01.SPA.bin
      template_name: PnP-Devices_NY-EWLC_No-Vars
      device_info:
        - serial_number: TTM2737021L
          hostname: NY-EWLC-1
          state: Unclaimed
          pid: C9800-40-K9
      pnp_type: CatalystWLC
      static_ip: 10.4.218.232
      subnet_mask: 255.255.255.240
      gateway: 10.4.218.225
      ip_interface_name: TenGigabitEthernet0/0/1
      vlan_id: 2014
```
#### Key Points

- **HA Setup**: Both EWLCs in the HA pair are configured with their unique IP addresses, subnets, and interfaces.
- **VLAN Configuration**: Each EWLC is assigned to VLAN 2014 and connected through a specific TenGigabitEthernet interface.
- **Templates and Images**: The devices are onboarded using the same project, image, and configuration template.

#### Mapping Config to UI Actions

#### Step 1: Assign a site to each device

![alt text](images/claim_multiple_ewlc_img2.png)
![alt text](images/claim_multiple_ewlc_img3.png)

#### Step 2: Assign Configuration for each device, Catalyst WLC Controller Setting is mandatory

![alt text](images/claim_multiple_ewlc_img4.png)
![alt text](images/claim_multiple_ewlc_img6.png)
![alt text](images/claim_multiple_ewlc_img7.png)

#### Step 3: Provision Templates, if there won't be any template configure there won't be any action required
![alt text](images/claim_multiple_ewlc_img8.png)

#### Step 4: Summary, can preview the device configuration details
![alt text](images/claim_multiple_ewlc_img9.png)


## Task: Resetting an Error PnP Device (EWLC Type)

In scenarios where a device encounters errors during onboarding, it can be reset and reattempted. The following task demonstrates how to reset a Catalyst EWLC that is in an error state.

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
  pnp_ewlc_reset:
    - site_name: Global/USA/SAN JOSE/SJ_BLD23
      project_name: Onboarding Configuration
      template_name: PnP-Devices_SJ-EWLC_No-Vars
      device_info:
        - serial_number: FOX2639PAYD
          hostname: SJ-EWLC-1
          state: Error
          pid: C9800-40-K9
```

#### Key Points

- **Error State**: The device is identified as being in an error state.
- **Reset**: The playbook ensures that the device is reset and ready for another onboarding attempt.

#### Mapping Config to UI Actions

![alt text](images/reset_error_ewlc_pnp.png)

## Task: Claiming Access Points (APs)

Access Points (APs) play a crucial role in wireless networks, and onboarding them can be automated through Cisco Catalyst Center. The following example shows how to onboard an Access Point (AP) into the network.

### Example: Input (YAML)
```bash
---
catalyst_center_version: 2.3.7.6
pnp_details:
 claim_access_points:
    - site_name: Global/USA/New York/NY_BLD2/FLOOR1
      rf_profile: HIGH
      device_info:
        - serial_number: FGL2402LCYH
          hostname: NY-AP1-C9120AXE
          state: Unclaimed
          pid: C9120AXE-E
      pnp_type: AccessPoint
```

#### Mapping Config to UI Actions

![alt text](images/claim_ap_device_img1.png)

#### Key Points

- **RF Profile**: Specifies the RF profile (e.g., HIGH) that will be applied to the Access Point.
- **Access Point Details**: The serial number, hostname, and product ID (PID) are provided for identification.
- **Important**: Ensure that the Wireless LAN Controller (WLC) is fully onboarded before claiming any Access Points; otherwise, you may encounter an error.

![alt text](images/ap_failure_img1.png)

### Usage

1. **Configure Variables**
    * Edit `catalyst_center_pnp_vars.yml` with your specific settings:
        * Catalyst Center credentials
        * Device information
        * Desired configuration templates
        
2. **Prepare Inventory**
    * Create `host_inventory_dnac1/hosts.yml` listing target devices.

3. **Validate Inputs**
```bash
    yamale -s workflows/plug_and_play/schema/plug_and_play_schema.yml workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml 
```

4. **Example Command To Run Playbook**
```bash
ansible-playbook -i ./inventory/demo_lab/inventory_demo_lab.yml ./workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/catalyst_center_pnp_vars.yml -vvvv
```

### Important Notes

* Customize the playbook and variables to match your network environment.
* Consult Cisco documentation for in-depth information about Plug and Play.

### Disclaimer

* This playbook is provided as-is. Use at your own risk.
* Ensure you have proper backups and understand the potential impact before running in a production environment.

## References

```yaml
  ansible: 9.9.0
  ansible-core: 2.16.10
  ansible-runner: 2.4.0

  dnacentersdk: 2.8.3
  cisco.dnac: 6.29.0
  ansible.utils: 5.1.2
```

---