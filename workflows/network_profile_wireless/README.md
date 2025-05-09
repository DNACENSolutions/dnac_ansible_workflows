# Cisco Catalyst Center Network Profile Wireless Workflow Playbooks

This is a comprehensive resource module for managing wireless network profiles in Cisco Catalyst Center.

**Description:**  
This module provides robust capabilities for creating, updating, and deleting wireless network profiles in Cisco Catalyst Center. It supports a wide range of configurations and workflows, enabling efficient management of wireless settings across sites, devices, and profiles. Key features include:  

- **Wireless Profile Management:**  
  - Create wireless network profiles with SSIDs, RF profiles, AP zones, and advanced settings.  
  - Update and delete single, multiple, or bulk wireless profiles.  
  - Bind SSIDs to profiles with different policy profiles.

- **Site Assignment and Hierarchy:**  
  - Assign wireless network profiles to sites, buildings, and floors.  
  - Add site tags (e.g., Power Profile, Calendar Profile).  

- **Interface and VLAN Settings:**  
  - Configure valid interfaces, VLAN groups, and anchor groups.  
  - Support for advanced VLAN configurations, including Local-to-VLAN mappings.  

- **AP Zone, RF Profile, and Device Tags:**  
  - Assign AP zones and RF profiles to wireless profiles.  
  - Configure device tags for granular control.  

- **Onboarding and DayN Templates:**  
  - Associate onboarding and DayN templates with wireless profiles.   

- **Bulk Operations:**  
  - Create and delete wireless profiles in bulk, ensuring scalability for large deployments.  


**Version Added:**  
`6.32.0`

---

This README outlines the steps to use the Ansible playbooks for managing Wireless Network Profiles in Cisco Catalyst Center.

## Workflow Steps

This workflow typically involves the following steps:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary collections for Cisco Catalyst Center.

1.  **Install Ansible:** Follow the official Ansible documentation for installation instructions.
2.  **Install Cisco Catalyst Center Collection:**
    ```bash
    ansible-galaxy collection install cisco.dnac
    ```
3.  **Generate Inventory:** Create an Ansible inventory file (e.g., `inventory.yml`) that includes your Cisco Catalyst Center appliance details. You will need to define variables such as the host, username, and password (or other authentication methods).
    ```yaml
    catalyst_center_hosts:
        hosts:
            your_catalyst_center_instance_name:
                catalyst_center_host: xx.xx.xx.xx
                catalyst_center_password: XXXXXXXX
                catalyst_center_port: 443
                catalyst_center_timeout: 60
                catalyst_center_username: admin
                catalyst_center_verify: false # Set to true for production with valid certificates
                catalyst_center_version: 2.3.7.9 # Specify your DNA Center version
                catalyst_center_debug: true
                catalyst_center_log_level: INFO
                catalyst_center_log: true
    ```

### Step 2: Define Inputs and Validate

This step involves preparing the input data for creating or managing wireless network profiles and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/network_profile_wireless_inputs.yml`) that define the desired state of your wireless network profiles, including details for creation, update, and deletion. 

##### Schema for Wireless Network Profiles
This schema defines the structure of the input file for configuring wireless network profiles in Cisco Catalyst Center. Below is a breakdown of the parameters, including their requirements and descriptions.


| **Parameter**                | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|------------------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `wireless_nw_profiles_details` | List       | Yes          | N/A               | A list of wireless network profiles to be created or managed.                  |

#### Wireless Network Profile (`wireless_nw_profiles_type`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `profile_name`        | String     | Yes          | N/A               | The name of the wireless network profile.                                      |
| `site_names`          | List       | No           | N/A               | A list of site hierarchies where the profile will be applied.                  |
| `ssid_details`        | List       | No           | N/A               | A list of SSIDs to be associated with the profile. See `ssid_details_type`.    |
| `ap_zones`            | List       | No           | N/A               | A list of AP zones to be associated with the profile. See `ap_zones_type`.     |
| `onboarding_templates`| List       | No           | N/A               | A list of onboarding templates to be associated with the profile.              |
| `day_n_templates`     | List       | No           | N/A               | A list of Day-N templates to be associated with the profile.                   |
| `additional_interfaces`| List      | No           | N/A               | A list of additional interfaces to be configured. See `additional_interfaces_type`. |

#### SSID Details (`ssid_details_type`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `ssid`               | String     | Yes          | N/A               | The name of the SSID.                                                          |
| `dot11be_profile_name`| String     | No           | N/A               | The name of the 802.11be profile associated with the SSID.                     |
| `enable_fabric`       | Boolean    | No           | `false`           | Indicates whether fabric is enabled for the SSID.                              |
| `vlan_group_name`     | String     | No           | N/A               | The VLAN group name associated with the SSID.                                  |
| `interface_name`      | String     | No           | N/A               | The interface name associated with the SSID.                                   |
| `anchor_group_name`   | String     | No           | N/A               | The anchor group name associated with the SSID.                                |
| `local_to_vlan`       | Integer    | No           | N/A               | The VLAN ID for local-to-VLAN mapping (range: 1–4094).                         |

#### AP Zones (`ap_zones_type`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `ap_zone_name`        | String     | Yes          | N/A               | The name of the AP zone.                                                       |
| `ssids`               | List       | No           | N/A               | A list of SSIDs to be associated with the AP zone.                             |
| `rf_profile_name`     | String     | No           | N/A               | The name of the RF profile associated with the AP zone.                        |

#### Additional Interfaces (`additional_interfaces_type`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `interface_name`      | String     | Yes          | N/A               | The name of the interface.                                                     |
| `vlan_id`             | Integer    | Yes          | N/A               | The VLAN ID to be assigned to the interface (range: 1–4094).                   |



##### Example Input File
Here’s an example input file based on the schema:
This example defines a wireless network profile named "Corporate_Wireless_Profile" for Cisco Catalyst Center, designed to streamline and manage wireless connectivity across two distinct sites: "Global/Headquarters" and "Global/BranchOffice". The profile includes two SSIDs, "Corporate_WiFi" and "Guest_WiFi", each tailored for specific use cases. The "Corporate_WiFi" SSID is associated with the "Corporate_VLAN" and "Corporate_VLAN_Group", ensuring secure and optimized connectivity for internal users, while the "Guest_WiFi" SSID is mapped to VLAN ID 3002 using the "guest_network" interface, providing isolated access for guest users. To enhance wireless performance, two AP zones are configured: "HQ_AP_Zone" with the "HIGH" RF profile for "Corporate_WiFi", and "Branch_AP_Zone" with the "TYPICAL" RF profile for "Guest_WiFi". Additional interfaces, "Corp_Interface_1" (VLAN ID 100) and "Guest_Interface_1" (VLAN ID 3002), ensure proper traffic segmentation and routing. Furthermore, the profile integrates a Day-N template, "Wireless_Controller_Config", enabling advanced post-deployment configurations to adapt to evolving network requirements. 

    ```yaml
    ---
    catalyst_center_version: 2.3.7.9
    # network_profile_wireless/vars/merged.yml
    wireless_nw_profiles_details:
        - profile_name: "Corporate_Wireless_Profile"
            site_names:
                - "Global/USA"
            ssid_details:
                - ssid_name: "Corporate_WiFi"
                enable_fabric: false
                dot11be_profile_name: "Corporate_VLAN"
                vlan_group_name: "Corporate_VLAN_Group"
                - ssid_name: "Guest_WiFi"
                enable_fabric: false
                dot11be_profile_name: "Corporate_VLAN"
                interface_name: "guest_network"
                local_to_vlan: 3002
            ap_zones:
                - ap_zone_name: "HQ_AP_Zone"
                rf_profile_name: "HIGH"
                ssids:
                    - "Corporate_WiFi"
                - ap_zone_name: "Branch_AP_Zone"
                    rf_profile_name: "TYPICAL"
                    ssids:
                    - "Guest_WiFi"
            additional_interfaces:
                - interface_name: "Corp_Interface_1"
                  vlan_id: 100
                - interface_name: "Guest_Interface_1"
                  vlan_id: 3002
            day_n_templates:
                - "Wireless_Controller_Config"
    ```

2.  **Validate Configuration:** 
To ensure a successful execution of the playbooks with your specified inputs, follow these steps:

*Input Validation*:
Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command *./tools/validate.sh -s* to perform the validation providing the schema path -d and the input path.

```bash

     ./tools/validate.sh -s ./workflows/wireless_design/schema/wireless_design_schema.yml -d ./workflows/wireless_design/vars/wireless_design_inputs.yml
```

### Step 3: Deploy and Verify

This is the final step where you deploy the configuration to Cisco Catalyst Center and verify the changes.

1.  **Deploy Configuration:** 

Run the playbook to seamlessly apply the wireless network profile configuration defined in your input variables to Cisco Catalyst Center. 
Before proceeding, ensure that the input validation step has been completed successfully, with no errors detected in the provided variables. Once validated, execute the playbook by specifying the input file path using the --e variable as VARS_FILE_PATH. 
This ensures that the configuration is accurately deployed to Cisco Catalyst Center, automating the setup process and reducing the risk of manual errors.

```bash

     ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/network_profile_wireless/playbook/network_profile_wireless_playbook.yml  --e VARS_FILE_PATH=/Users/majlona/Desktop/dnac_ansible_workflows/workflows/network_profile_wireless/vars/network_profile_wireless_inputs.yml -vvvv
```

If there is an error in the input or an issue with the API call during execution, the playbook will halt and display the relevant error details.


2.  **Verify Deployment:** 
After executing the playbook, check the Catalyst Center UI to verify wireless design. If *debug_log* is enabled, you can also review the logs for detailed information on operations performed and any updates made.

![Alt text](./images/network_profiles.png)

---

### References

*Note: The environment used for the references in the above instructions is as follows:*

```yaml
python: 3.12.0
dnac_version: 2.3.7.9
ansible: 9.9.0
cisco.dnac: 6.32.0
dnacentersdk: 2.8.8
```

For detailed information on network wireless profile workflow refer to the following documentation: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/network_profile_wireless_workflow_manager/

