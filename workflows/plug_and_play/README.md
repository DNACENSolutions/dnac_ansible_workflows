# Plug and Play Provisioning Ansible Workflow

## **Overview**

This Ansible playbook automates the provisioning and onboarding of new network devices leveraging Cisco's Plug and Play technology. It streamlines the process of configuring devices, minimizing manual efforts and promoting consistency. This guide explains how to use an Ansible Playbook to automate device onboarding using Cisco's Plug-and-Play (PnP) service within the Cisco Catalyst Center. This feature allows network administrators to onboard new devices into the network with minimal manual intervention, reducing deployment time and avoiding configuration errors.

**PnP** (Plug-and-Play) is a network deployment solution that simplifies the process of onboarding new devices by automatically assigning configurations and images to new network devices upon discovery. This automation can be driven by **Cisco Catalyst Center** via **Ansible Playbooks** to handle various deployment scenarios, including:

- **Switches**
- **Wireless LAN Controllers (WLCs)**
- **Access Points (APs)**

The following Ansible Playbook examples demonstrate the onboarding process for:

1. **Claiming a Cisco Catalyst 9K Switch**
2. **Claiming a Cisco Catalyst 9K Switch Stack**
3. **Claiming a Cisco Embedded Wireless Controller (EWLC)**
4. **Claiming Multiple EWLCs for High Availability (HA)**
5. **Onboarding Access Points (APs)**

## Prerequisites

Before starting, ensure the following requirements are met:
- **Access to Cisco Catalyst Center (DNAC)**: Ensure that PnP (Plug-and-Play) is enabled. 
- **Devices that Support PnP**: Confirm that the devices you intend to onboard are PnP-capable.
- **Ansible Installation**: Ansible must be installed on the machine managing the automation process.
- **Cisco DNA Ansible Collection**: The `cisco.dnac.pnp_workflow_manager` module must be available from the Cisco DNA Ansible Collection.
- **dnacentersdk Python SDK**: This SDK is required to interact with Cisco Catalyst Center.
* Ansible installed
* `yamale` Python library installed (`pip install yamale`)
* Cisco DNA Center or Plug and Play Connect access configured

## **Key Features**

* **Zero-Touch Provisioning:** Remotely configure devices onboarded through PnP
* **Planned Provisioning:** Pre-configure settings and apply them when the device comes online.
* **Unclaimed Provisioning:** Discover and configure new devices that join the network unexpectedly.

**Workflows**

* **Planned Provisioning:**
    * Devices are pre-configured in Catalyst Center.
    * Upon connecting to the network, they automatically receive their configuration.
* **Unclaimed Provisioning:**
    * New devices are detected.
    * An administrator can initiate the provisioning process through this playbook.

## Overview of the PnP Onboarding Process
This diagram provides an overview of the **PnP onboarding process** initiated by an Ansible playbook using the **cisco.dnac.pnp_workflow_manager** module. The module interacts with the **Cisco Catalyst Center** via its API, allowing devices to be onboarded seamlessly into the network.

## Key Components

### Ansible Playbook
- The playbook serves as the automation tool that executes the onboarding process.
- It triggers the **cisco.dnac.pnp_workflow_manager** module, passing configuration parameters for devices to be onboarded.

### Ansible Module: cisco.dnac.pnp_workflow_manager
- Manages the interaction between Ansible and the Catalyst Center APIs.
- Retrieves device details, checks the existence of sites, images, and templates, and processes the onboarding steps for each device.

### Cisco Catalyst Center SDK
Acting as the intermediary, the SDK communicates directly with the Catalyst Center APIs. It performs the following:
- **Retrieves device information** from the PnP database using the device’s `serial_number`.
- If the device does not exist in the PnP database, the SDK **adds the device**.
- If the device already exists, the SDK **updates its details** if necessary.
- If a device is in an "Error" state, the SDK **resets the device** before continuing with onboarding.

### API Calls
- **GET**: Requests details from Catalyst Center about the device (via the `/dna/intent/api/v1/onboarding/pnp-device` endpoint), checking if the device is already in the system.
- **POST**: For new devices or when the device needs to be claimed to a site, a POST request is sent to `/dna/intent/api/v1/onboarding/pnp-device` or `/dna/intent/api/v1/onboarding/pnp-device/site-claim`.
- **PUT**: If the device exists but requires updating, the module uses a PUT request to modify the existing record.

### Device Processing Loop
The playbook loops through each device defined in the `pnp_params` and handles onboarding as follows:
- **Initial Check**: Verify if the site, image, and template are available.
- **Device Handling**: The device is either added, updated, or reset based on its current state.
- **Claiming to a Site**: Each device is claimed and assigned to its designated site in Catalyst Center.

### Bulk Import
If several devices need to be imported at once (i.e., bulk processing), the module performs a bulk import by sending a POST request to the bulk import API endpoint (`/dna/intent/api/v1/onboarding/pnp-device/import`).

## Understanding the configs for PnP tasks
- `config_verify` (bool): Set to `True` to verify the Cisco Catalyst Center config after applying the playbook config. Defaults to `False`.
- `state` (str): The state of Cisco Catalyst Center after module completion. Choices: [`merged`, `deleted`]. Defaults to `merged`.
- `config` (list[dict]): List of device details being managed. **Required**.
  - `device_info` (list[dict]): Provides device-specific information for adding devices to the PnP database. **Required**.
    - For single device addition: The list should contain exactly one set of device information. If a `site_name` is also provided, the device can be claimed immediately.
    - For bulk import: The list must contain information for more than one device. Claiming must be performed separately.
      - `hostname` (str): Desired hostname for the PnP device after claiming. Can only be assigned/changed during the claim process.
      - `state` (str): Onboarding state of the PnP device. Choices: [`Unclaimed`, `Claimed`, `Provisioned`].
      - `pid` (str): PnP device's PID.
      - `serial_number` (str): PnP device's serial number.
      - `is_sudi_required` (bool): Flag indicating if SUDI authentication is required.
      - `site_name` (str): Name of the site for claiming the device.
      - `project_name` (str): Name of the project under which the template is present. Defaults to "Onboarding Configuration".
      - `template_name` (str): Name of the template to be configured on the device. Supported for EWLC from Cisco Catalyst Center release 2.3.7.x onwards.
      - `template_params` (dict): Parameter values for parameterized templates. Key-value pairs of variable names and values (e.g., `variable_name: variable_value`). Supported for EWLC from Cisco Catalyst Center release 2.3.7.x onwards.
      - `image_name` (str): Name of the image to be configured on the device.
      - `golden_image` (bool): Flag indicating if the image is tagged as a golden image.
      - `pnp_type` (str): Device type for the PnP device. Choices: [`Default`, `CatalystWLC`, `AccessPoint`, `StackSwitch`]. Defaults to `Default`.
        - `Default`: Applicable to switches and routers.
        - `CatalystWLC`: For 9800 series wireless controllers.
        - `AccessPoint`: For claiming an access point.
        - `StackSwitch`: For a group of switches operating as a single switch.
      - `static_ip` (str): Management IP address of the Wireless Controller.
      - `subnet_mask` (str): Subnet mask of the management IP address of the Wireless Controller.
      - `gateway` (str): Gateway IP address of the Wireless Controller.
      - `vlan_id` (str): VLAN ID allocated for claiming the Wireless Controller.
      - `ip_interface_name` (str): Interface name used for PnP by the Wireless Controller. Must be pre-configured on the controller.
      - `rf_profile` (str): Radio Frequency (RF) profile of the AP being claimed. Choices: [`HIGH`, `LOW`, `TYPICAL`].
        - `HIGH`: Allows more power and easier AP joining with clients.
        - `TYPICAL`: Blend of moderate power and client visibility.
        - `LOW`: Consumes less power and has least client visibility.

### Task: Claiming a Cisco Catalyst 9K Switch

The PnP onboarding process in Cisco Catalyst Center allows devices to be automatically recognized and configured as they join the network. This playbook uses the `cisco.dnac.pnp_workflow_manager` module to automate the onboarding process for a variety of device types such as switches, wireless controllers (EWLC), and access points (APs).

### Mapping Config to UI Actions

The `config` parameter within each task corresponds to actions you would normally perform manually in the Cisco Catalyst Center UI, such as: **Provision > Plug and Play > Claim**

``` yaml
    - name: Claim Cat9K switch
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - site_name: Global/USA/SAN JOSE/SJ_BLD23
            project_name: Onboarding Configuration
            template_name: PnP-Devices-SW
            image_name: cat9k_iosxe.17.12.02.SPA.bin
            template_params:
              PNP_VLAN_ID: 2000
              LOOPBACK_IP: 204.1.2.1
            device_info:
              - serial_number: FJC271924D9
                hostname: SJ-EN-1-9300
                state: Unclaimed
                pid: C9300-48UXM
      tags: claim_cat9k
```

### Task: Claiming a Cisco Catalyst 9K Switch Stack

#### Mapping Config to UI Actions

Similar to the task for claiming a single switch, this task relies on a predefined configuration template in Cisco Catalyst Center. However, in this case, the **StackSwitch** option is selected in the UI to indicate that the device being onboarded is part of a switch stack.

``` yaml
    - name: Claim Cat9K switches stack
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - site_name: Global/USA/New York/NY_BLD4
            project_name: Onboarding Configuration
            template_name: PnP-Devices-SW
            image_name: cat9k_iosxe.17.14.01.SPA.bin
            template_params:
              PNP_VLAN_ID: 2005
              LOOPBACK_IP: 204.1.2.2
            device_info:
              - serial_number: FJC271925Q1
                hostname: NY-EN-1-9300
                state: Unclaimed
                pid: C9300-48UXM
            pnp_type: StackSwitch
      tags: claim_cat9k_stack
```

### Task: Claiming a Cisco Embedded Wireless Controller (EWLC)

#### Mapping Config to UI Actions

In the Cisco Catalyst Center UI, onboarding a Cisco Embedded Wireless Controller (EWLC) involves specifying parameters such as the site, project, device information, and network settings. This configuration aligns with actions like assigning a site, selecting an image, and setting network interfaces.

``` yaml
    - name: Claim a single EWLC
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - site_name: Global/USA/SAN JOSE/SJ_BLD21
            project_name: Onboarding Configuration
            image_name: C9800-40-universalk9_wlc.17.12.02.SPA.bin
            template_name: PnP-Devices_NY-EWLC_No-Vars
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
      tags: claim_ewlc
```

### Task: Claiming Multiple EWLC Devices for High Availability (HA)

#### Mapping Config to UI Actions

``` yaml
    - name: Claim two EWLC devices for HA
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
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
      tags: claim_ewlc_ha
```
#### Key Points

- **HA Setup**: Both EWLCs in the HA pair are configured with their unique IP addresses, subnets, and interfaces.
- **VLAN Configuration**: Each EWLC is assigned to VLAN 2014 and connected through a specific TenGigabitEthernet interface.
- **Templates and Images**: The devices are onboarded using the same project, image, and configuration template.


### Task: Resetting an Error PnP Device (EWLC Type)

#### Mapping Config to UI Actions

In scenarios where a device encounters errors during onboarding, it can be reset and reattempted. The following task demonstrates how to reset a Catalyst EWLC that is in an error state.

``` yaml
    - name: Reset an Error PnP device - EWLC type
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - site_name: Global/USA/SAN JOSE/BLD23
            project_name: Onboarding Configuration
            template_name: PnP-Devices_SJ-EWLC_No-Vars
            device_info:
              - serial_number: TTM2737020R
                hostname: WLC
                state: Error
                pid: C9800-40-K9
      tags: reset_ewlc
```
#### Key Points

- **Error State**: The device is identified as being in an error state.
- **Reset**: The playbook ensures that the device is reset and ready for another onboarding attempt.

### Task: Claiming Access Points (APs)

#### Mapping Config to UI Actions

Access Points (APs) play a crucial role in wireless networks, and onboarding them can be automated through Cisco Catalyst Center. The following example shows how to onboard an Access Point (AP) into the network.

``` yaml 
    - name: Claim AP
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - site_name: Global/USA/New York/NY_BLD2/FLOOR1
            rf_profile: HIGH
            device_info:
              - serial_number: FGL2402LCYH
                hostname: NY-AP1-C9120AXE
                state: Unclaimed
                pid: C9120AXE-E
            pnp_type: AccessPoint
      tags: claim_ap
```
#### Key Points

- **RF Profile**: Specifies the RF profile (e.g., HIGH) that will be applied to the Access Point.
- **Access Point Details**: The serial number, hostname, and product ID (PID) are provided for identification.
- **Important**: Ensure that the Wireless LAN Controller (WLC) is fully onboarded before claiming any Access Points; otherwise, you may encounter an error.

### Task: Bulk Device Onboarding

This task demonstrates how to add multiple devices in bulk. Bulk onboarding is useful when multiple devices need to be configured and onboarded simultaneously, such as in large-scale deployments.

#### Mapping Config to UI Actions
``` yaml
    - name: Adding PnP devices in Bulk
      cisco.dnac.pnp_workflow_manager:
        <<: *common_config
        state: merged
        config:
          - device_info:
              - serial_number: FOX2639PAYD
                hostname: SJ-EWLC-1
                state: Unclaimed
                pid: C9800-40-K9
              - serial_number: FJC271924D9
                hostname: SJ-EN-9300
                state: Unclaimed
                pid: C9300-48UXM
              - serial_number: FJC271925Q1
                hostname: NY-EN-9300
                state: Unclaimed
                pid: C9300-48UXM
              - serial_number: FJC2402A0TX
                hostname: SF-BN-ISR
                state: Unclaimed
                pid: ISR4451-X/K9
      tags: bulk_add
```


**Usage**

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
3. **Execute Playbook**
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --e VARS_FILE_PATH=../vars/catalyst_center_pnp_vars.yml
```
**Important Notes**

* Customize the playbook and variables to match your network environment.
* Consult Cisco documentation for in-depth information about Plug and Play.

**Disclaimer**

* This playbook is provided as-is. Use at your own risk.
* Ensure you have proper backups and understand the potential impact before running in a production environment.

---