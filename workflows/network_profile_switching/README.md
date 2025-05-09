# Cisco Catalyst Center Network Profile Switching Workflow Playbooks

**short_description:** Resource module for managing switch profiles in Cisco Catalyst Center

**description:** >
  This module allows the creation and deletion of network switch profiles in Cisco Catalyst Center.
  - Supports creating and deleting switch profiles.
  - Allows assignment of profiles to sites, onboarding templates, and Day-N templates.

**version_added:** '6.31.0'

---

This README outlines the steps to use the Ansible playbooks for managing Network Profile Switching in Cisco Catalyst Center.

## Workflow Steps

This workflow typically involves the following steps:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary collections for Cisco Catalyst Center.

1.  **Install Ansible:** Follow the official Ansible documentation for installation instructions.
2.  **Install Cisco Catalyst Center Collection:**
    ```bash
    ansible-galaxy collection install cisco.dnac
    ```
3.  **Generate Inventory:** Create an Ansible inventory file (e.g., `hosts.yml`) that includes your Cisco Catalyst Center appliance details. You will need to define variables such as the host, username, and password (or other authentication methods).
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

This step involves preparing the input data for creating or managing network profiles and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/network_profiles.yml`) that define the desired state of your network switch profiles, including details for creation, deletion, and assignment. Refer to the specific playbook documentation for the required variable structure.

    ```yaml
    # Example vars/network_profiles.yml
    network_profiles:
      - name: "My_Switch_Profile"
        site_name: "Building_1"
        # ... other profile parameters and assignments
    ```

2.  **Validate Configuration:** 
Use yamale to validate the user created configurations against the playbooks required spfcification
```yaml
yamale -s workflows/network_profile_switching/schema/network_profile_switching_schema.yml workflows/network_profile_switching/vars
Validating workflows/network_profile_switching/vars...
Found 2 yaml files to validate...
Validation success! 👍
```

### Step 3: Deploy and Verify

This is the final step where you deploy the configuration to Cisco Catalyst Center and verify the changes.

1.  **Deploy Configuration:** Run the playbooks to apply the configuration defined in your input variables to Cisco Catalyst Center.

    ```bash
    ansible-playbook -i ansible_inventory/catalystcenter_inventory/hosts.yml ../catc_ansible_workflows/workflows/network_profile_switching/playbook/delete_network_profile_switching_playbook.yml -e VARS_FILE_PATH=/Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/../catc_ansible_workflows/workflows/network_profile_switching/vars/network_profile_switching_inputs.yml -vvv
    ```
