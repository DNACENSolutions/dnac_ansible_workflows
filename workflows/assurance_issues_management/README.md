# Assurance Issues Management Workflow Playbook

This workflow playbook automates the management of assurance issues within Cisco Catalyst Center (formerly Cisco DNA Center). It provides tasks to interact with assurance issues, such as retrieving, acknowledging, or clearing them using the `cisco.catalyst_center.path_trace_workflow_manager` module (Note: This module name seems incorrect based on the workflow name, it should likely be an assurance issues module. Please verify the correct module name used in the playbook).

## Prerequisites

*   An active Cisco Catalyst Center instance.
*   Ansible installed and configured.
*   The `cisco.catalyst_center` Ansible collection installed (`ansible-galaxy collection install cisco.catalyst_center`).
*   Appropriate API credentials for Cisco Catalyst Center with necessary permissions to manage assurance issues.

## Configure Host Inventory

Update your Ansible `hosts.yml` inventory file with the connection details of your Cisco Catalyst Center instance. A sample structure is shown below:

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

## Define Playbook Input
Input variables for this workflow are typically defined in a YAML file, for example, workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml. The structure of this file should conform to the workflow's schema.

Refer to the workflow's schema file (workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml - Note: This schema file name is assumed based on the workflow name. Please verify the actual schema filename) for a detailed description of the required and optional input parameters.

Based on the module specification provided earlier (which seems to be for path trace, not general assurance issues, but I will use its structure as an example for input definition), your input file might look like this:
```yaml
---
# Example input structure based on a hypothetical assurance issues module
assurance_issues_details:
  - state: merged # or deleted
    config:
      - issue_id: "some_issue_id" # Example parameter
        action: "acknowledge" # Example parameter
      - issue_id: "another_issue_id"
        action: "clear"
```

## Input Validation
It is highly recommended to validate your input file against the workflow's schema using yamale before running the playbook. This ensures that your input is correctly formatted and contains all necessary parameters.

```bash
yamale -s workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml  workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml 
Validating workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml...
Validation success! 👍

```
## Execute the Playbook
Once your input file is validated, you can execute the playbook using the ansible-playbook command. Provide your inventory file using the -i flag and your input variables file using the --extra-vars flag, specifying VARS_FILE_PATH.

```bash
ansible-playbook -i your_inventory_path/hosts.yml workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml -vvv

Example:
nsible-playbook -i your_inventory_path/hosts.yml workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml -vvv

 57542 1746338831.58739: starting run
ansible-playbook [core 2.18.3]
  config file = /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible.cfg
  configured module search path = ['/Users/pawansi/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/pawansi/workspace/CatC_Configs/venv-anisible/lib/python3.11/site-packages/ansible
  ansible collection location = /Users/pawansi/.ansible/collections:/usr/share/ansible/collections
  executable location = /Users/pawansi/workspace/CatC_Configs/venv-anisible/bin/ansible-playbook
  python version = 3.11.10 (main, Sep  7 2024, 01:03:31) [Clang 15.0.0 (clang-1500.3.9.4)] (/Users/pawansi/workspace/CatC_Configs/venv-anisible/bin/python)
  jinja version = 3.1.5
  libyaml = True
...

PLAY RECAP ***************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=5    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0   
```

(Note: Replace your_inventory_path/hosts.yml and the playbook/vars file paths with the actual paths in your environment. The -vvv flag enables verbose output, which can be helpful for debugging.)

If there are errors during execution, the playbook will stop and display the error details.

## Post-Execution Monitoring
After the playbook execution, you can verify the results in the Cisco Catalyst Center UI under the Assurance section. If dnac_debug is enabled in your inventory, you can also review the Ansible logs for detailed information on the API calls and responses.

## Reference
Refer to the workflow's schema file (workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml) for the definitive list of input parameters and their descriptions.
