# Assurance Intelligent Capture Workflow Playbook

This workflow playbook automates the configuration and management of Intelligent Capture settings within Cisco Catalyst Center (formerly Cisco DNA Center) for network assurance.

## Workflow Description

The `assurance_intelligent_capture` workflow utilizes Cisco DNA Center Ansible modules to configure Intelligent Capture parameters, allowing administrators to set up targeted packet capture for troubleshooting and analysis of network issues.

## Prerequisites

*   An active Cisco Catalyst Center instance.
*   Ansible installed and configured.
*   The `cisco.dnac` Ansible collection installed (`ansible-galaxy collection install cisco.dnac`).
*   Appropriate API credentials for Cisco Catalyst Center with necessary permissions to configure Intelligent Capture.

## Step 1: Prepare Your Environment

### Install Ansible and Cisco.dnac Collection

Ensure you have Ansible installed (version 9.9.0 or higher is recommended). If not, follow the official Ansible installation guide.

Install the `cisco.dnac` Ansible collection:

```bash
ansible-galaxy collection install cisco.dnac
```

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

## Step 2: Define and Validate Input

### Define Playbook Input
Input variables for configuring Intelligent Capture are defined in a YAML file, typically located at workflows/assurance_intelligent_capture/vars/intelligent_capture_inputs.yml. The structure and required parameters for this file are defined in the workflow's schema.

Refer to the workflow's schema file (workflows/assurance_intelligent_capture/schema/intelligent_capture_schema.yml - Note: This schema file name is assumed based on the workflow name. Please verify the actual schema filename) for a detailed description of all available input parameters.

A sample input file might look like this (structure is illustrative and depends on the actual module/schema):

```yaml
---
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_inteligent_capture_settings:
  - assurance_icap_settings:
    - capture_type: ONBOARDING
      preview_description: "ICAP onboarding capture"
      duration_in_mins: 30
      client_mac: 50:91:E3:47:AC:9E  # required field
      wlc_name: NY-IAC-EWLC.cisco.local  # required field
    - capture_type: FULL
      preview_description: "Full ICAP capture for troubleshooting"
      duration_in_mins: 30
      client_mac: 50:91:E3:47:AC:9E  # required field
      wlc_name: NY-IAC-EWLC.cisco.local  # required field
  - assurance_icap_download:
    - capture_type: FULL
      client_mac: 50:91:E3:47:AC:9E
      start_time: "2025-03-05 11:56:00"
      end_time: "2025-03-05 12:01:00"
      file_path: ./
```
(Note: The actual input structure will depend on the specific tasks and the module used in the assurance_intelligent_capture playbook. Please refer to the actual playbook and schema files for the correct input format.)

### Validate Input File
Before running the playbook, validate your input YAML file against the workflow's schema using the yamale tool. This step helps catch formatting errors and missing required parameters.

```bash
yamale -s workflows/assurance_intelligent_capture/schema/intelligent_capture_schema.yml  workflows/assurance_intelligent_capture/vars/intelligent_capture_inputs.yml
```
(Note: Adjust the schema and input file paths as necessary based on the actual file locations in this workflow.)

A successful validation will output "Validation success! 👍".

## Step 3: Execute the Playbook
Once your input file is validated, execute the playbook using the ansible-playbook command. Specify your inventory file using the -i flag and your input variables file using the --extra-vars flag with VARS_FILE_PATH.

```bash
ansible-playbook -i your_inventory_path/hosts.yml workflows/assurance_intelligent_capture/playbook/intelligent_capture_playbook.yml --extra-vars VARS_FILE_PATH=workflows/assurance_intelligent_capture/vars/intelligent_capture_inputs.yml -vvv
```
(Note: Replace your_inventory_path/hosts.yml and the playbook/vars file paths with the actual paths in your environment. The -vvv flag enables verbose output, which can be helpful for debugging.)

If the playbook encounters errors during execution (e.g., API communication issues, incorrect parameters), it will stop and display the relevant error messages.

### Post-Execution Monitoring
After the playbook has finished, verify the Intelligent Capture configuration in the Cisco Catalyst Center UI. You can also review the Ansible output and logs (if dnac_debug is enabled) for details on the operations performed.

## Reference
For a complete list and description of all possible input parameters, refer to the workflow's schema file:
workflows/assurance_intelligent_capture/schema/intelligent_capture_schema.yml

