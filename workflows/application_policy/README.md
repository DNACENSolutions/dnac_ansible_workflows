# Cisco Catalyst Center Application Policy Workflow Playbooks

**short_description:** >
  Resource module for managing queuing profiles, applications, application sets and application
  policies for wired and wireless in Cisco Catalyst Center.

**description:**
  - Provides functionality to create, update, and delete applications in Cisco Catalyst Center.
  - Provides functionality to create, update, and delete application policies in Cisco Catalyst Center.
  - Provides functionality to create, update, and delete application queuing profiles in Cisco Catalyst Center.
  - Supports managing queuing profiles and application policies for traffic classification and prioritization.

**version_added:** "6.31.0"

---

This README outlines the steps to use the Ansible playbooks for managing Application Policies in Cisco Catalyst Center.

## Workflow Steps

This workflow follows a three-step approach:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary collections for Cisco Catalyst Center.

1.  **Install Ansible:** Follow the official Ansible documentation for installation instructions.
2.  **Install Cisco Catalyst Center Collection:**
    ```bash
    ansible-galaxy collection install cisco.dnac
    ```
3.  **Generate Inventory:** Create an Ansible inventory file (e.g., `inventory.yml`) that includes your Cisco Catalyst Center appliance details. You will need to define variables such as the host, username, and password (or other authentication methods).
### Configure Host Inventory
Update your Ansible hosts.yml inventory file with the connection details of your Cisco Catalyst Center instance. Replace the placeholder values with your actual Catalyst Center information.
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

### Step 2: Define Create Inputs, and Validate

This step involves preparing the input data for creating or managing application policies and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/application_policies.yml`) that define the desired state of your application policies, applications, queuing profiles, etc. Refer to the specific playbook documentation for the required variable structure.
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
# This file contains the variables for the inventory workflow
application_policy_details:
  - queuing_profile:
    - profile_name: "Enterprise-QoS-Profile"
      profile_description: "QoS profile optimized for business-critical applications"
      bandwidth_settings:
        is_common_between_all_interface_speeds: false
        interface_speed_settings:
          - interface_speed: "ALL"
            bandwidth_percentages:
              transactional_data: "5"
              best_effort: "10"
              voip_telephony: "15"
              multimedia_streaming: "10"
              real_time_interactive: "20"
              multimedia_conferencing: "10"
              signaling: "10"
              scavenger: "5"
              ops_admin_mgmt: "5"
              broadcast_video: "2"
              network_control: "3"
              bulk_data: "5"
          - interface_speed: "TEN_GBPS"
            bandwidth_percentages:
              transactional_data: "5"
              best_effort: "10"
              voip_telephony: "15"
              multimedia_streaming: "10"
              real_time_interactive: "20"
              multimedia_conferencing: "10"
              signaling: "10"
              scavenger: "5"
              ops_admin_mgmt: "5"
              broadcast_video: "2"
              network_control: "3"
              bulk_data: "5"
      dscp_settings:
        multimedia_conferencing: "20"
        ops_admin_mgmt: "23"
        transactional_data: "28"
        voip_telephony: "45"
        multimedia_streaming: "27"
        broadcast_video: "46"
        network_control: "48"
        best_effort: "0"
        signaling: "4"
        bulk_data: "10"
        scavenger: "2"
        real_time_interactive: "34"

    - profile_name: "Enterprise_DSCP_Profile"
      profile_description: "DSCP-based queuing profile for traffic prioritization."
      dscp_settings:
        multimedia_conferencing: "20"
        ops_admin_mgmt: "23"
        transactional_data: "28"
        voip_telephony: "45"
        multimedia_streaming: "27"
        broadcast_video: "46"
        network_control: "48"
        best_effort: "0"
        signaling: "4"
        bulk_data: "10"
        scavenger: "2"
        real_time_interactive: "34"
  - application:
    - name: "Security_Gateway_App"
      help_string: "Application for network security and access control"
      description: "Security Gateway Application"
      type: "server_name"
      server_name: "www.securitygateway.com"
      traffic_class: "BROADCAST_VIDEO"
      ignore_conflict: true
      rank: "23"
      engine_id: "4"
      application_set_name: "local-services"
    - name: "Security_Gateway_IP_App"
      help_string: "Security Gateway Application based on IP"
      description: "Defines security gateway policies using server IPs"
      type: "server_ip"
      network_identity:
        protocol: "UDP"
        port: "2000"
        ip_subnet: ["1.1.1.1","2.2.2.2","3.3.3.3"]
        lower_port: "10"
        upper_port: "100"
      dscp: 2
      traffic_class: "BROADCAST_VIDEO"
      ignore_conflict: true
      rank: "23"
      engine_id: "4"
      application_set_name: "local-services"

  - application_policy:
    - name: "WiredTrafficOptimizationPolicy"
      policy_status: "NONE"
      site_names: ["Global/INDIA"]
      device_type: "wired"
      application_queuing_profile_name: "WiredStreamingQueuingProfile"
      clause:
        - clause_type: "BUSINESS_RELEVANCE"
          relevance_details:
            - relevance: "BUSINESS_RELEVANT"
              application_set_name: ["collaboration-apps"]
            - relevance: "BUSINESS_IRRELEVANT"
              application_set_name: ["email","tunneling"]
            - relevance: "DEFAULT"
              application_set_name: ["backup-and-storage", "general-media", "file-sharing"]
    - name: "wireless_traffic_optimization_policy"
      policy_status: "NONE"
      site_names: ["global/Chennai/FLOOR1"]
      device_type: "wireless"
      device:
        device_ip: "204.1.2.3"
        wlan_id: "17"
      application_queuing_profile_name: "wireless_streaming_queuing_profile"
      clause:
        - clause_type: "BUSINESS_RELEVANCE"
          relevance_details:
            - relevance: "BUSINESS_RELEVANT"
              application_set_name: ["file-sharing"]
            - relevance: "BUSINESS_IRRELEVANT"
              application_set_name: ["email","backup-and-storage"]
            - relevance: "DEFAULT"
              application_set_name: ["collaboration-apps","tunneling", "general-media"]

```

2.  **Validate Configuration:** You can use yamale to validate the input against the schema

    ```bash
yamale -s workflows/application_policy/schema/application_policy_schema.yml workflows/application_policy/vars/application_policy_inputs.yml
Validating workflows/application_policy/vars/application_policy_inputs.yml...
Validation success! 👍

    ```

### Step 3: Deploy and Verify

This is the final step where you deploy the configuration to Cisco Catalyst Center and verify the changes.

1.  **Deploy Configuration:** Run the playbooks to apply the configuration defined in your input variables to Cisco Catalyst Center.

    ```bash
    ansible-playbook create_application_policy.yml -i inventory.yml -e VARS_FILE_PATH=<Path to your variables file>
    ```
