# Assurance Issues Management Workflow Playbook

This workflow playbook automates the management of assurance issues within Cisco Catalyst Center (formerly Cisco DNA Center). It provides tasks to interact with assurance issues, such as creating, updating and deleting custom assurance issues using `cisco.dnac.assurance_issue_workflow_manager` module. The workflow also enables configuration of thresholds, rules, and other assurance settings, helping streamline issue detection and response within the Catalyst Center platform. 

## Workflow Key Features
- **Create, Update, and Delete Assurance Issues**: Automate the management of custom assurance issues.
- **Modify System Define issues**: Update existing system-defined assurance issues.
- **Threshold Configuration**: Set and modify thresholds for various assurance metrics. 

**Version Added:**  
`6.32.0`

## Workflow Steps
### This workflow typically involves the following steps:

### Step 1: Prepare Your Ansible Environment

*   An active Cisco Catalyst Center instance.
*   Ansible installed and configured (recommend ansible:9.9.0 or higher).
*   The `cisco.dnac` Ansible collection installed (`ansible-galaxy collection install cisco.dnac`).
*   Appropriate API credentials for Cisco Catalyst Center with necessary permissions to manage assurance issues.

### Step 2: Configure Host Inventory

Create an Ansible inventory file (e.g., `inventory.yml`) that includes your Cisco Catalyst Center appliance details. You will need to define variables such as the host, username, and password (or other authentication methods).

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

### Step 3: Define Inputs and Validate

This step involves preparing the input data for creating or managing assurance issue setting and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/assurance_issues_management_inputs.yml`) that define the desired state of your assurance issue setting, including details for creation, update, and deletion. 

2.  **Validate Configuration:** 
To ensure a successful execution of the playbooks with your specified inputs, follow these steps:

  **Input Validation**:
  Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command *./tools/validate.sh -s* to perform the validation providing the schema path -d and the input path.

  ```bash
  #validates input file against the schema
  ./tools/validate.sh -s ./workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml -d ./workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml

  #sample output validation
  yamale -s workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml  workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml 
  Validating workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml...
  Validation success! 👍
  ```

#### Schema for Assurance Issues Management
The schema file (e.g., `schema/assurance_issues_management_schema.yml`) defines the structure and validation rules for the input variables. It includes details such as required fields, data types, and constraints.


| **Parameter**                       | **Type**   | **Required** | **Allowed Values / Default**                                                                 | **Description**                          |
|--------------------------------------|------------|--------------|---------------------------------------------------------------------------------------------|------------------------------------------|
| catalyst_center_version              | string     | No           |                                                                                             | Catalyst Center version                  |
| catalyst_center_verify               | bool       | No           |                                                                                             | SSL certificate verification             |
| catalyst_center_config_verify        | bool       | No           |                                                                                             |                                          |
| catalyst_center_task_timeout         | int        | No           | Default: 1200                                                                               |                                          |
| catalyst_center_debug                | bool       | No           | Default: False                                                                              |                                          |
| catalyst_center_log                  | bool       | No           | Default: False                                                                              |                                          |
| catalyst_center_log_append           | bool       | No           | Default: True                                                                               |                                          |
| catalyst_center_log_file_path        | string     | No           | Default: dnac.log                                                                           |                                          |
| catalyst_center_log_level            | enum       | No           | CRITICAL, ERROR, WARNING, INFO, DEBUG                                                       |                                          |
| catalyst_center_task_poll_interval   | int        | No           |                                                                                             |                                          |
| assurance_issues_settings            | list       | No           | List of `assurance_issues_settings_type`                                                    |                                          |

**assurance_issues_settings_type**

| **Parameter**                        | **Type**   | **Required** | **Description**                                        |
|--------------------------------------|------------|--------------|--------------------------------------------------------|
| assurance_user_defined_issue_settings| list       | No           | List of user-defined issue settings                    |
| assurance_system_issue_settings      | list       | No           | List of system-defined issue settings                  |

**assurance_user_defined_issue_settings_type**

| **Parameter**            | **Type**   | **Required** | **Allowed Values**           | **Description**                  |
|-------------------------|------------|--------------|------------------------------|----------------------------------|
| name                    | string     | Yes          |                              | Issue name                       |
| description             | string     | No           |                              |                                  |
| rules                   | list       | No           | List of `rules_type`         |                                  |
| is_enabled              | bool       | No           |                              |                                  |
| priority                | enum       | No           | P1, P2, P3, P4               |                                  |
| is_notification_enabled | bool       | No           |                              |                                  |
| prev_name               | string     | No           |                              | For updating existing issues     |

**rules_type**

| **Parameter**         | **Type**   | **Required** | **Allowed Values**                | **Description** |
|----------------------|------------|--------------|-----------------------------------------------------------------------------------------------------------------------|-----------------|
| pattern              | string     | No           |                                                                                                                       |                 |
| occurrences          | number     | No           |                                                                                                                       |                 |
| duration_in_minutes  | number     | No           |                                                                                                                       |                 |
| severity             | enum       | No           | 0, 1, 2, 3, 4, 5, 6, Emergency, Alert, Critical, Error, Warning, Notice, Info                                        |                 |
| facility             | enum       | No           | CI, PLATFORM_ENV, ..., STACKMGR (see schema for full list)                                                           |                 |
| mnemonic             | enum       | No           | SHUT_LC_FANGONE, SHUTFANGONE, ..., STACK_LINK_CHANGE (see schema for full list)                                      |                 |

**assurance_system_issue_settings_type**

| **Parameter**                | **Type**   | **Required** | **Allowed Values**                                   | **Description**                  |
|-----------------------------|------------|--------------|------------------------------------------------------|----------------------------------|
| name                        | string     | Yes          |                                                      | Issue name                       |
| description                 | string     | Yes          |                                                      |                                  |
| device_type                 | enum       | Yes          | Router, SWITCH_AND_HUB, UNIFIED_AP, FIREWALL, CONTROLLER, WIRED_CLIENT |                                  |
| synchronize_to_health_threshold | bool   | Yes          |                                                      |                                  |
| priority                    | enum       | Yes          | P1, P2, P3, P4                                       |                                  |
| issue_enabled               | bool       | Yes          |                                                      |                                  |
| threshold_value             | int        | Yes          |                                                      |                                  |
| prev_name                   | string     | No           |                                                      |                                  |
| issue_name                  | string     | No           |                                                      |                                  |
| issue_process_type          | enum       | No           | resolution, ignore, command_execution                |                                  |
| start_datetime              | string     | No           |                                                      |                                  |
| end_datetime                | string     | No           |                                                      |                                  |
| site_hierarchy              | string     | No           |                                                      |                                  |
| priority                    | enum       | No           | P1, P2, P3, P4                                       |                                  |
| issue_status                | enum       | No           | ACTIVE, RESOLVED, IGNORED                            |                                  |
| device_name                 | string     | No           |                                                      |                                  |
| mac_address                 | string     | No           |                                                      |                                  |
| network_device_ip_address   | string     | No           |                                                      |                                  |

> **Note:** For full lists of allowed values for `facility` and `mnemonic`, refer to the schema file `schema/assurance_issues_management_schema.yml` or [ansible galaxy document](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/assurance_issue_workflow_manager/). All lists can have 0 to 1000 items unless otherwise specified.

## Workflow overview with example

## 1. **Create Assurance Issues**: 
### Create a new assurance issue with the specified parameters.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
      - name: High CPU Usage Alert issue
        description: Triggers an alert when CPU usage exceeds threshold
        rules:
          - severity: Warning
            facility: LISP
            mnemonic: MAP_CACHE_WARNING_THRESHOLD_REACHED
            pattern: The LISP map-cache limit warning threshold * entries for instance-id * has been reached.
            occurrences: 1
            duration_in_minutes: 2
        is_enabled: true
        priority: P1
        is_notification_enabled: false
```

### Step1: Execute the assurance issue management playbook. 

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_issues_management_inputs.yml -vvvv 
```

#### Upon successful completion, issue will be created

![alt text](./images/User_def_issue_created.png)

### Step 3: Verify the playbook output

#### Upon successful completion, you will see an output similar to:

```yaml
"msg": {
        "High CPU Usage Alert issue": "user-defined issue created successfully"
        },
```

## 2. **Update Assurance Issues**: 
### Update an existing assurance issue.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
      - prev_name: High CPU Usage Alert issue
        name: Excessive CPU Utilization Alert
        description: Triggers an alert when CPU usage exceeds threshold
        rules:
          - severity: Warning
            facility: LISP
            mnemonic: MAP_CACHE_WARNING_THRESHOLD_REACHED
            pattern: The LISP map-cache limit warning threshold * entries for instance-id * has been reac.
            occurrences: 1
            duration_in_minutes: 3
        is_enabled: true
        priority: P1
        is_notification_enabled: false
```

### Step1: Execute the assurance issue management playbook. 

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_issues_management_inputs.yml -vvvv 
```

#### Upon successful completion, issue will be updated

![alt text](./images/User_def_issue_updated.png)

### Step 3: Verify the playbook output

#### Upon successful completion, you will see an output similar to:

```yaml
"msg": {
        "High CPU Usage Alert issue": "User defined issues updated Successfully"
        },
```

## 3. **Delete Assurance Issues**: 
### Delete an existing assurance issue.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
    - name: Excessive CPU Utilization Alert
```

### Step1: Execute the assurance issue management playbook. 

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_issues_management/playbook/delete_assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_issues_management_inputs.yml -vvvv 
```

#### Upon successful completion, issue will be removed from cisco catalyst center

![alt text](./images/User_def_issue_deleted.png)

### Step 3: Verify the playbook output

#### Upon successful completion, you will see an output similar to:

```yaml
"msg": {
        "High CPU Usage Alert issue": "Assurance user-defined issue deleted successfully"
        },
```
## 4. **Update System Defined Issues**:
### Modify an existing system-defined assurance issue.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_system_issue_settings:
      - name: "Assurance telemetry status is poor"
        description: RF Noise (5GHz)
        device_type: WIRED_CLIENT
        synchronize_to_health_threshold: true
        priority: P1
        issue_enabled: false
        threshold_value: -10

```

### Step 1: Execute the assurance issue management playbook. 

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_issues_management_inputs.yml -vvvv 
```

### Upon successful completion, the issue will be updated in Cisco Catalyst Center

#### Before Updating
![alt text](./images/system_def_issu_before_update.png)

#### After Updating
![alt text](./images/System_def_issu_after_update.png)

### Step 3: Verify the playbook output

#### Upon successful completion, you will see an output similar to:

```yaml
"msg": {
        "High CPU Usage Alert issue": "System issue updated successfully"
        },
```

## Run line parameters description:

- `-i`: Specifies the inventory file containing host details.  
- `--e VARS_FILE_PATH`: Path to the variable file containing workflow inputs.  
- `-vvvv`: Enables verbose mode for detailed output.  

## Post-Execution Monitoring
After the playbook execution, you can verify the results in the Cisco Catalyst Center UI under the Assurance section. If dnac_debug is enabled in your inventory, you can also review the Ansible logs for detailed information on the API calls and responses.

## Reference
Refer to the workflow's schema file (workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml) for the definitive list of input parameters and their descriptions.
