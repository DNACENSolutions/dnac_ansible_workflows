# Cisco Catalyst Center Network Profile Wireless Workflow Playbooks

**short_description:** Resource module for managing wireless network profiles in Cisco Catalyst Center

**description:** >
  This module allows the creation, update, and deletion of wireless network profiles in Cisco Catalyst Center.
  - Supports creating, updating, and deleting wireless profiles.
  - Allows configuration of wireless settings within profiles.

**version_added:** '6.31.0'

---

This README outlines the steps to use the Ansible playbooks for managing Wireless Network Profiles in Cisco Catalyst Center.

## Workflow Steps

This workflow typically involves the following steps:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary collections for Cisco Catalyst Center.

1.  **Install Ansible:** Follow the official Ansible documentation for installation instructions.
2.  **Install Cisco Catalyst Center Collection:**
    ```bash
    ansible-galaxy collection install cisco.catalystcenter
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
                catalyst_center_version: 2.3.7.6 # Specify your DNA Center version
                catalyst_center_debug: true
                catalyst_center_log_level: INFO
                catalyst_center_log: true
    ```

### Step 2: Define Inputs and Validate

This step involves preparing the input data for creating or managing wireless network profiles and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/network_profile_wireless_inputs.yml`) that define the desired state of your wireless network profiles, including details for creation, update, and deletion. Refer to the specific playbook documentation for the required variable structure.
    ```yaml
    ---
    catalyst_center_version: 2.3.7.9
    # network_profile_wireless/vars/merged.yml
    wireless_nw_profiles_details
    - profile_name: "Corporate_Wireless_Profile"
        site_names:
        - "Global/USA/SAN_JOSE"
        - "Global/USA/SAN-FRANCISCO"
        ssid_details:
        - ssid: "iac-open"
            enable_fabric: true
            enable_broadcast: true
        - ssid: "iac-employees"
            enable_fabric: true
            enable_broadcast: true
        - ssid: "iac-guests"
            enable_fabric: true
            enable_broadcast: true
        ap_zones:
        - ap_zone_name: "HQ_AP_Zone"
            rf_profile_name: "HIGH"
            ssids:
            - "iac-open"
        - ap_zone_name: "Branch_AP_Zone"
            rf_profile_name: "TYPICAL"
            ssids:
            - "iac-guests"
        additional_interfaces:
        - interface_name: "Corp_Interface_1"
            vlan_id: 100
        - interface_name: "Guest_Interface_1"
            vlan_id: 3002
    ```

2.  **Validate Configuration:** You can use Ansible's `--check` and `--diff` flags to validate your playbooks and input variables without making any changes to the Catalyst Center.

    ```bash
    ansible-playbook manage_wireless_profiles.yml -i inventory.yml --check --diff
    ```

### Step 3: Deploy and Verify

This is the final step where you deploy the configuration to Cisco Catalyst Center and verify the changes.

1.  **Deploy Configuration:** Run the playbooks to apply the configuration defined in your input variables to Cisco Catalyst Center.

    ```bash
    ansible-playbook manage_wireless_profiles.yml -i inventory.yml
    ```
    Replace `manage_wireless_profiles.yml` with the actual playbook file you intend to run.

2.  **Verify Deployment:** After the playbook execution completes, verify the changes in Cisco Catalyst Center GUI or by using other playbooks designed for verification (e.g., playbooks to retrieve the state of configured profiles).

    ```bash
    ansible-playbook verify_wireless_profiles.yml -i inventory.yml
    ```
    (Assuming you have a `verify_wireless_profiles.yml` playbook).

---

Refer to the individual playbook files within this directory for specific usage examples and required variables.
