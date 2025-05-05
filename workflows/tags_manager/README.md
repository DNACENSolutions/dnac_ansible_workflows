# Tags Manager Workflow

This workflow automates the management of tags within your infrastructure using Ansible.

## Structure

- **images/**: Contains image assets related to the workflow.
- **jinja_template/**: Jinja2 templates used for dynamic content generation.
- **playbook/**: Ansible playbooks for tag management operations.
- **schema/**: Schema definitions for input validation and workflow structure.
- **vars/**: Variable files for customizing workflow behavior.

## Usage

1. Install and Generate Inventory

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
4. **Customize Variables:**  
   Adjust variables in the `vars/` directory to suit your environment and requirements.

5. **Validate Input:**
    Validate tags user input with yamale and playbook schema
    ```bash
    yamale -s tags_manager/schema/tags_manager_schema.yml tags_manager/vars/tags_manager_inputs.yml
    Validating tags_manager/vars/tags_manager_inputs.yml...
    Validation success! 👍
    ```
6. **Run the Workflow:**  
   Execute the main playbook to manage tags as needed.

7. **Example Variable File:**
  vars/tags_manager_inputs.yml
```yaml
  catalyst_center_version: 2.3.7.6
# Fabric Sites and Zones design.
tags_details:
  - tag:
      name: Server_Connected_Devices_and_Ports
      description: "Tag for devices and interfaces connected to servers"
  - tag:
      name: Border_9300_Tag
      description: Tag for border devices belonging to the Cisco Catalyst 9300 family.
      device_rules:
        rule_descriptions:
          - rule_name: device_name
            search_pattern: contains
            value: Border
            operation: ILIKE
          - rule_name: device_series
            search_pattern: ends_with
            value: "9300"
            operation: ILIKE
  - tag:
      name: HighSpeed_Server_Interfaces
      description: Tag for 10G interfaces connected to servers.
      port_rules:
        scope_description:
          scope_category: TAG
          scope_members:
            - NY_SERVER_TAG
            - SJC_SERVER_TAG
        rule_descriptions:
          - rule_name: speed
            search_pattern: equals
            value: "10000"
            operation: ILIKE
          - rule_name: port_name
            search_pattern: contains
            value: TenGigabitEthernet1/0/1
            operation: ILIKE
  - tag_memberships:
      tags:
        - High_Speed_Interfaces
      device_details:
        - ip_addresses:
            - 10.197.156.97
            - 10.197.156.98
            - 10.197.156.99
```

