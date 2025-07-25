# Assurance Issues Management Workflow Playbook

This workflow playbook automates the management of assurance issues within Cisco Catalyst Center (formerly Cisco DNA Center).      

It provides tasks to interact with assurance issues, such as creating, updating, and deleting custom assurance issues and issue resolution functionalities. The workflow also enables configuration of thresholds, rules, and other assurance settings, helping streamline issue detection and response within the Catalyst Center platform. For more details, refer to the [Ansible Galaxy documentation](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/assurance_issue_workflow_manager/).

## Workflow Key Features
- **Create, Update, and Delete Assurance Issues**: Automate the management of custom assurance issues.
- **Modify System Define issues**: Update existing system-defined assurance issues.
- **Threshold Configuration**: Set and modify thresholds for various assurance metrics. 
- **Resolve, Ignore, and Execute Suggested Commands**: Take automated actions to resolve issues, ignore specific ones, or execute recommended commands as suggested by Cisco Catalyst Center.

**Version Added:**  
`6.32.0`

## Workflow Steps

### This workflow typically involves the following steps:

### Step 1: Install and Configure Host Inventory

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

### Step 2: Define Inputs and Schema Overview

This step involves preparing the input data for creating or managing assurance issue setting and validating your setup.

1.  **Define Input Variables:** Create variable files (e.g., `vars/assurance_issues_management_inputs.yml`) that define the desired state of your assurance issue setting, including details for creation, update, and deletion. 

#### Schema for Assurance Issues Management
The schema file (e.g., `schema/assurance_issues_management_schema.yml`) defines the structure and validation rules for the input variables. It includes details such as required fields, data types, and constraints.

**assurance_issues_settings_type**

| **Parameter**                        | **Type**   | **Required** | **Description**                                        |
|--------------------------------------|------------|--------------|--------------------------------------------------------|
| assurance_user_defined_issue_settings| list       | No           | List of user-defined issue settings                    |
| assurance_system_issue_settings      | list       | No           | List of system-defined issue settings                  |
| assurance_issue                   | list       | No           | List of assurance issues to resolve, ignore, or execute commands |

**assurance_user_defined_issue_settings_type**

| **Parameter**            | **Type**   | **Required** | **Allowed Values**           | **Description**                  |
|-------------------------|------------|--------------|------------------------------|---------------------------------- |
| name                    | string     | Yes          |                              | Issue name                       |
| description             | string     | No           |                              | A brief explanation of the issue                                 |
| rules                   | list       | No           | List of `rules_type`         |A set of rules that define the parameters                                   |
| is_enabled              | bool       | No           |                              |Enables or disables the issue setting                                  |
| priority                | enum       | No           | P1, P2, P3, P4               |Specifies the priority of the issue between p1 to p4                                  |
| is_notification_enabled | bool       | No           |                              |Boolean value to specify if notifications should be enabled                                  |
| prev_name               | string     | No           |                              | For updating existing issues     |

**rules_type**

| **Parameter**         | **Type**   | **Required** | **Allowed Values**                | **Description** |
|----------------------|------------|--------------|-----------------------------------------------------------------------------------------------------------------------|-----------------|
| pattern              | string     | No           |                                                                                                                       |     A pattern or regular expression defining the issue detection criteria            |
| occurrences          | number     | No           |                                                                                                                       |    The number of times the issue pattern must occur before triggering the issue             |
| duration_in_minutes  | number     | No           |                                                                                                                       |The duration, in minutes, for which the issue pattern must persist to be considered valid.                 |
| severity             | enum       | No           | 0, 1, 2, 3, 4, 5, 6, Emergency, Alert, Critical, Error, Warning, Notice, Info                                        |Specifies the severity level of the issue. can be an integer (0 to 6) or corresponding string representation.                  |
| facility             | enum       | No           | CI, PLATFORM_ENV, ..., STACKMGR (see schema for full list)                                                           | The facility type that the rule applies to.                |
| mnemonic             | enum       | No           | SHUT_LC_FANGONE, SHUTFANGONE, ..., STACK_LINK_CHANGE (see schema for full list)                                      |A system-generated identifier or label representing the issue.                 |

**assurance_system_issue_settings_type**

| **Parameter**                | **Type**   | **Required** | **Allowed Values**                                   | **Description**                  |
|-----------------------------|------------|--------------|------------------------------------------------------|----------------------------------|
| name                        | string     | Yes          |                                                      | Issue name                       |
| description                 | string     | Yes          |                                                      |Explains system issue settings and required threshold updates for defined issue names.                                  |
| device_type                 | enum       | Yes          | Router, SWITCH_AND_HUB, UNIFIED_AP, FIREWALL, CONTROLLER, WIRED_CLIENT | Specifies the type of device to which the issue configuration applies. for choices check Allowed Values.                                  |
| synchronize_to_health_threshold | bool   | Yes          |                                                      |A boolean value indicating whether the system issue should be synchronized to the health threshold.                                  |
| priority                    | enum       | Yes          | P1, P2, P3, P4                                       |Specifies the priority level of the issue.                       |
| issue_enabled               | bool       | Yes          |                                                      | A boolean value that determines whether the issue is enabled or disabled.                                 |
| threshold_value             | int        | Yes          |                                                      | The threshold value that triggers the issue. This is usually specified as a percentage or a numerical value depending on the nature of the issue.                                 |
| prev_name                   | string     | No           |                                                      | The previous name of the issue setting (used when updating an existing issue setting).                                 |
| issue_name                  | string     | No           |                                                      | Name of the issue                                 |
| issue_process_type          | enum       | No           | resolution, ignore, command_execution                |Defines the action to be taken on the issue. Possible values: resolution: Resolves the issue. ignore: Ignores the issue.                                  |
| start_datetime              | string     | No           |                                                      | A filter to select issues that started at or after this date and time.                                 |
| end_datetime                | string     | No           |                                                      | A filter to select issues that ended at or before this date and time.                                 |
| site_hierarchy              | string     | No           |                                                      | A filter to select issues based on the site location hierarchy. The format is "Global/Region/Location/Building"                                 |
| priority                    | enum       | No           | P1, P2, P3, P4                                       | A filter to select issues based on their priority                                 |
| issue_status                | enum       | No           | ACTIVE, RESOLVED, IGNORED                            | A filter to select issues based on their status.                                 |
| device_name                 | string     | No           |                                                      | A filter to select issues based on the device name that is associated with the issue                                 |
| mac_address                 | string     | No           |                                                      | A filter to select issues based on the MAC address of the device associated with the issue                                 |
| network_device_ip_address   | string     | No           |                                                      | A filter to select issues based on the network device's IP                                 |

**assurance_issue_type**

| **Parameter**                | **Type**   | **Required** | **Allowed Values**                          | **Description**                                      |
|------------------------------|------------|--------------|---------------------------------------------|------------------------------------------------------|
| issue_name                   | string     | Yes          |                                             | Name of the assurance issue                          |
| issue_process_type           | enum       | Yes          | resolution, ignore, command_execution       | Action to perform on the issue                       |
| start_datetime               | string     | No           |                                             | Filter: issues that started at or after this date     |
| end_datetime                 | string     | No           |                                             | Filter: issues that ended at or before this date      |
| site_hierarchy               | string     | No           |                                             | Filter: issues based on site location hierarchy       |
| device_name                  | string     | No           |                                             | Filter: issues based on device name                  |
| priority                     | enum       | No           | P1, P2, P3, P4                              | Filter: issues based on priority                     |
| issue_status                 | enum       | No           | ACTIVE, RESOLVED, IGNORED                   | Filter: issues based on status                       |
| mac_address                  | string     | No           |                                             | Filter: issues based on device MAC address           |
| network_device_ip_address    | string     | No           |                                             | Filter: issues based on network device IP address |

> **Note:** For full lists of allowed values for `facility` and `mnemonic`, refer to the schema file `schema/assurance_issues_management_schema.yml` or [ansible galaxy document](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/assurance_issue_workflow_manager/). All lists can have 0 to 1000 items unless otherwise specified.

## Workflow overview with example

## a. **Create Assurance Issues**: 
### Create a new assurance issue with the specified parameters

In this example, we are creating a custom assurance issue called **"High CPU Usage Alert issue"**. This issue is designed to trigger an alert when CPU usage on a device exceeds a defined threshold. 

**Prerequisites**: The device(s) you want to monitor must be managed by Cisco Catalyst Center and sending telemetry data relevant to the rule you define (e.g., LISP events for this example).

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

#### Upon successful completion, the issue will be created and you will see an output similar to the following:

![alt text](./images/User_def_issue_created.png)

```yaml
"msg": {
    "High CPU Usage Alert issue": "user-defined issue created successfully"
},
```

### Example: Input YAML for Creating Multiple Issues

You can also create multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_user_defined_issue_settings`:
```yaml
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
      - name: critical temperature warning
        description: temperature levels above safe operating limits.
        rules:
          - severity: Error
            facility: CMRP_ENVMON
            mnemonic: TEMP_WARN_CRITICAL
            pattern: "Error: Failed or underperforming cooling for System:*"
            occurrences: 1
            duration_in_minutes: 2
        is_enabled: true
        priority: P1
        is_notification_enabled: false
      - name: High Availability role has changed
        description: The system is part of an HA pair, and one unit changed its role
        rules:
          - severity: Info
            facility: SMART_LIC
            mnemonic: HA_ROLE_CHANGED
            pattern: Smart Agent HA role changed to *
            occurrences: 1
            duration_in_minutes: 3
        is_enabled: true
        priority: P1
        is_notification_enabled: true
```

## b. **Update Assurance Issues**: 
### Update an existing assurance issue

In this example, we are updating the previously created **"High CPU Usage Alert issue"**. The updates include:
- **Changing the issue name** from "High CPU Usage Alert issue" to **"Excessive CPU Utilization Alert"** for better clarity.
- **Modifying the rule's duration_in_minutes** from 2 to 3, which means the alert will now trigger if the high CPU usage condition persists for 3 minutes instead of 2.

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

#### Upon successful completion, the issue details will be updated and you will see an output similar to the following:

![alt text](./images/User_def_issue_updated.png)

```yaml
"msg": {
    "High CPU Usage Alert issue": "User defined issues updated Successfully"
},
```

### Example: Input YAML for Updating Multiple Issues

You can also update multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_user_defined_issue_settings`:
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
            pattern: The LISP map-cache limit warning threshold * entries for instance-id * has been reached.
            occurrences: 1
            duration_in_minutes: 3
        is_enabled: true
        priority: P2
        is_notification_enabled: false
      - prev_name: critical temperature warning
        name: critical temperature warning updated
        description: Updated description for temperature warning.
        rules:
          - severity: Error
            facility: CMRP_ENVMON
            mnemonic: TEMP_WARN_CRITICAL
            pattern: "Error: Failed or underperforming cooling for System:*"
            occurrences: 2
            duration_in_minutes: 5
        is_enabled: true
        priority: P2
        is_notification_enabled: true
```

## c. **Delete Assurance Issues**: 
### Delete an existing assurance issue

In this example, we are deleting the previously updated assurance issue named **"Excessive CPU Utilization Alert"**. Deleting an assurance issue will remove its configuration from Cisco Catalyst Center, and the system will no longer monitor or alert based on the rules defined in that issue.  

**Important Note**: To delete an assurance issue, you must run the playbook specifically designed for deletion (for example, `delete_assurance_issues_management_playbook.yml` and input file `delete_assurance_issues_management_inputs.yml`). This playbook will process the input file in "deleted" state and remove the specified issue from the system.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
    - name: Excessive CPU Utilization Alert
```

#### Upon successful completion, issue will be removed from Cisco Catalyst Center and you will see an output similar to the following:

![alt text](./images/User_def_issue_deleted.png)

```yaml
"msg": {
        "High CPU Usage Alert issue": "Assurance user-defined issue deleted successfully"
        },
```

### Example: Input YAML for Deleting Multiple Issues

You can also delete multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_user_defined_issue_settings`:

```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_user_defined_issue_settings:
      - name: Excessive CPU Utilization Alert
      - name: critical temperature warning updated
      - name: High Availability role has changed
```

## d. **Update System Defined Issues**:
### Modify an existing system-defined assurance issue.

In this example, we are updating the system-defined issue named **"Radio Down (2.4 GHz)"**. based on the name, description, and device type. we can update the issue settings to better fit our environment. The update includes: priority, issue_enabled and threshold_value depends on the issue we are updating. here we are updating the priority to P2.

### Example: Input YAML
```yaml
catalyst_center_version: 2.3.7.9
assurance_issues_settings:
  - assurance_system_issue_settings:
      - name: "Radio Down (2.4 GHz)"
        description: 2.4 GHz Radio on the AP is down.
        device_type: UNIFIED_AP
        priority: P2
        issue_enabled: true
```

#### Upon successful completion, the issue will be updated in Cisco Catalyst Center and you will see an output similar to the following:

#### Before Updating
![alt text](./images/system_def_issu_before_update.png)

#### After Updating
![alt text](./images/System_def_issu_after_update.png)

```yaml
"msg": {
        "High CPU Usage Alert issue": "System issue updated successfully"
        },
```

### Example: Input YAML for Updating Multiple System Defined Issues
You can also update multiple system-defined assurance issues in a single playbook run by specifying more than one entry under `assurance_system_issue_settings`:

```yaml
assurance_issues_settings:
  - assurance_system_issue_settings:
    - name: "TCAM Utilization High Issues"
      description: TCAM Utilization
      device_type: SWITCH_AND_HUB
      priority: P1
      issue_enabled: true
      threshold_value: 80
    - name: "Dual-Active Detection Link has failed"
      description: Dual-Active Detection Link has failed on the Network Device
      device_type: SWITCH_AND_HUB
      priority: P2
      issue_enabled: true
```

## e. **Resolve an Assurance Issues**:
### Resolve an existing assurance issue, can be system define/user define

In this example, we are resolving the assurance issue named **"Fabric BGP session issue"**. This action will mark the issue as resolved in Cisco Catalyst Center.

**Important Note**: When resolving an assurance issue, you must provide either `site_hierarchy` or one of `device_name`, `mac_address`, or `network_device_ip_address`—but not both.

### Example: Input YAML
```yaml
  - assurance_issue:
    - issue_name: BGP v4 neighborship(s) on Fabric Border 'NY-BN-9500.cisco.local' in Fabric Site 'Global/USA/New York' is down  # required field
      issue_process_type: resolution  # required field
      # start_datetime: "2024-04-23 11:30:00"  # optional field
      # end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/New York/NY_BLD1  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.4  # optional field
```
#### Upon successful completion, the issue will be resolved in Cisco Catalyst Center and you will see an output similar to the following:

**Note**: You can view resolved issues in Cisco Catalyst Center by navigating to **Assurance > Dashboards > Issue and Events**. In the **Issues** dropdown, select the **Resolved** option to see all the resolved issues.

Assurance issue Landing page:
![alt text](./images/Resolve_issue_landing_page.png)

Assurance issue Resolved page for specific issue:
![alt text](./images/Resolved_issue_listing.png)

```yaml
"msg": "Issue resolved successfully. '[{'successfulIssueIds': ['b357feeb-67ad-4f1b-9106-16627dd4004b']}]'.",
"response": [
    {
        "successfulIssueIds": [
            "b357feeb-67ad-4f1b-9106-16627dd4004b"
        ]
    }
],
"status": "success"
```

### Example: Input YAML for Resolving Multiple Issues
You can also resolve multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_issue`:

```yaml
  - assurance_issue:
    - issue_name: Internet service on Fabric Border 'SJ-BN-9300.cisco.local' is unavailable on Transit Control Plane 'DC-T-9300.cisco.local'  # required field
      issue_process_type: resolution  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/SAN JOSE/SJ_BLD23  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.4  # optional field
    - issue_name: MACFLAP_NOTIF  # required field
      issue_process_type: resolution  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/India/Bangalore/bld1  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.1  # optional field
```

## f. **Ignore an Assurance Issues**:
### Ignore an existing assurance issue, can be system define/user define

In this example, we are ignoring the assurance issue named **"PKI - Non authoritative clock"**. This action will mark the issue as ignored in Cisco Catalyst Center.

**Important Note**: When ignoring an assurance issue, you must provide either `site_hierarchy` or one of `device_name`, `mac_address`, or `network_device_ip_address`—but not both.

### Example: Input YAML
```yaml
  - assurance_issue:
    - issue_name: PKI - Non authoritative clock  # required field
      issue_process_type: ignore  # required field
      # start_datetime: "2024-04-23 11:30:00"  # optional field
      # end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/New York/NY_BLD1  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.1
```

#### Upon successful completion, the issue will be ignored in Cisco Catalyst Center and you will see an output similar to the following:

Assurance ignore issue Landing page:
![alt text](./images/Ignore_issue_landing_page.png)

Assurance ignore issue page for specific issue:
![alt text](./images/Ignore_issue_listing.png)

```yaml
"msg": "Find the list of issue ids: [\n    \"2764b515-c5d5-46bb-bcbf-74d49d6b6656\",\n    \"1b4b0c4f-cc2e-4de4-aaab-f35ce4474cb9\",\n    \"dcaf06e3-64aa-4cc8-a534-11a40e9538cd\"\n]Issue ignored successfully. '[{'successfulIssueIds': ['1b4b0c4f-cc2e-4de4-aaab-f35ce4474cb9', '2764b515-c5d5-46bb-bcbf-74d49d6b6656', 'dcaf06e3-64aa-4cc8-a534-11a40e9538cd']}]'.",
"response": [
    {
        "successfulIssueIds": [
            "1b4b0c4f-cc2e-4de4-aaab-f35ce4474cb9",
            "2764b515-c5d5-46bb-bcbf-74d49d6b6656",
            "dcaf06e3-64aa-4cc8-a534-11a40e9538cd"
        ]
    }
],
"status": "success"
```

**Note** Multiple issues were ignored in the above example because the same issue occurred on different devices and site hierarchies. Since only the issue name and hierarchy were specified, all matching issues were ignored.

### Example: Input YAML for Ignoring Multiple Issues

You can also ignore multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_issue`:

```yaml
  - assurance_issue:
    - issue_name: PKI - Non authoritative clock  # required field
      issue_process_type: ignore  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/SAN JOSE/SJ_BLD23  # optional field
      #device_name: SJ-IM-1-9300.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: 24:6c:84:d3:7f:80  # optional field
      #network_device_ip_address: 204.1.2.1
    - issue_name: Internet service on Fabric Border 'SJ-BN-9300.cisco.local' is unavailable on Transit Control Plane 'DC-T-9300.cisco.local'  # required field
      issue_process_type: ignore  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/SAN JOSE/SJ_BLD23  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.2 # optional field
```

## g. **Execute Suggested Commands**:
### Execute suggested commands for an existing assurance issue

In this example, we are executing suggested commands for the assurance issue named **"Fabric BGP session issue - BGP v6 neighborship(s)"**. This action will execute the recommended commands in Cisco Catalyst Center.

**Important Note**: When executing suggested commands for an assurance issue, you must provide either `site_hierarchy` or one of `device_name`, `mac_address`, or `network_device_ip_address`—but not both.
### Example: Input YAML
```yaml
  - assurance_issue:
    - issue_name: Fabric BGP session issue - BGP v6 neighborship(s)  # required field
      issue_process_type: command_execution  # required field
      # start_datetime: "2024-04-23 11:30:00"  # optional field
      # end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/New York/NY_BLD1  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.1  # optional field
```

#### Upon successful completion, the suggested commands will be executed and you will see an output similar to the following:

```yaml
"msg": "Find the list of issue ids: [\n    \"14fe319a-211d-487e-97ac-e904987c7508\"\n]Command executed successfully for [{'bapiKey': 'cfb2-ab10-4cea-bfbb', 'bapiName': 'Execute Suggested Actions Commands', 'bapiExecutionId': '5b825558-9b08-48c3-bee8-cb8e2d043ba8', 'startTime': 'Tue May 20 10:26:52 UTC 2025', 'startTimeEpoch': 1747736812732, 'endTime': 'Tue May 20 10:27:15 UTC 2025', 'endTimeEpoch': 1747736835031, 'timeDuration': 22299, 'status': 'SUCCESS', 'bapiSyncResponse': '[{\"actionInfo\":\"Cisco Catalyst Center Suggested Action 1: Verify the BGP session status.\",\"stepsCount\":1,\"entityId\":\"2ae93b4d-2e69-4e2d-aa73-b1737dace9bd\",\"hostname\":\"SF-BN-1-ISR.cisco.local\",\"stepsDescription\":\"Verify the BGP session status for all vpnv6 neighbors\",\"command\":\"show bgp vpnv6 unicast all summary\",\"commandOutput\":{\"show bgp vpnv6 unicast all summary\":\"show bgp vpnv6 unicast all summary\\\\nBGP router identifier 204.1.2.6, local AS number 6100\\\\nBGP table version is 184, main routing table version 184\\\\n64 network entries using 18432 bytes of memory\\\\n64 path entries using 10752 bytes of memory\\\\n25/25 BGP path/bestpath attribute entries using 7800 bytes of memory\\\\n1 BGP community entries using 24 bytes of memory\\\\n8 BGP extended community entries using 192 bytes of memory\\\\n0 BGP route-map cache entries using 0 bytes of memory\\\\n0 BGP filter-list cache entries using 0 bytes of memory\\\\nBGP using 37200 total bytes of memory\\\\nBGP activity 222/69 prefixes, 255/102 paths, scan interval 60 secs}}], 'runtimeInstanceId': 'DNACP_Runtime_e68edbdb-c028-4cef-a3b7-5e25a2c3513a'}].",
    "response": [
        {
            "issue_name": "BGP v6 neighborship(s) on Fabric Border 'SF-BN-1-ISR.cisco.local' in Fabric Site 'Global/USA/SAN-FRANCISCO' is down",
            "issue_process_type": "command_execution",
            "issue_status": "ACTIVE",
            "priority": "P1",
            "site_hierarchy": "Global/USA/SAN-FRANCISCO"
        }
    ],
    "status": "success"
```

#### Example: Input YAML for Executing Suggested Commands for Multiple Issues

You can also execute suggested commands for multiple assurance issues in a single playbook run by specifying more than one entry under `assurance_issue`:

```yaml
  - assurance_issue:
    - issue_name: Excessive time lag between Cisco Catalyst Center and device "SF-BN-1-ISR.cisco.local"  # required field
      issue_process_type: command_execution  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/SAN-FRANCISCO/SF_BLD1  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P3  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.1  # optional field
    - issue_name: Internet service on Fabric Border 'SJ-BN-9300.cisco.local' in Fabric Site 'Global/USA/SAN JOSE' is unavailable on Local Control Plane 'SJ-BN-9300.cisco.local'  # required field
      issue_process_type: command_execution  # required field
      #start_datetime: "2024-04-23 11:30:00"  # optional field
      #end_datetime: "2024-05-20 11:50:00"  # optional field
      site_hierarchy: Global/USA/SAN JOSE/SJ_BLD23  # optional field
      #device_name: NY-BN-9500.cisco.local  # optional field
      priority: P1  # optional field
      issue_status: ACTIVE  # optional field
      #mac_address: e4:38:7e:42:bc:40  # optional field
      #network_device_ip_address: 204.1.2.2  # optional field
```

### Step 3: Deploy and Verify

a.  **Validate Configuration:** 
To ensure a successful execution of the playbooks with your specified inputs, follow these steps:

**Input Validation Against Schema**:
Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command *./tools/validate.sh -s* to perform the validation providing the schema path -d and the input path.

```bash
#validates input file against the schema
./tools/validate.sh -s ./workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml -d ./workflows/assurance_issues_management/vars/assurance_issues_management_inputs.yml
```

b.  **Run the Playbook:**

Run the playbook to seamlessly apply the assurance issue setting configuration defined in your input variables to Cisco Catalyst Center. 

Before proceeding, ensure that the input validation step has been completed successfully, with no errors detected in the provided variables. Once validated, execute the playbook by specifying the input file path using the --e variable as VARS_FILE_PATH. The VARS_FILE_PATH must be provided as a full path to the input file.

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_issues_management/playbook/assurance_issues_management_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_issues_management_inputs.yml -vvvv  
```

c. **Verify Deployment:** 
After the playbook execution, you can verify the results in the Cisco Catalyst Center UI under the Assurance section. If dnac_debug is enabled in your inventory, you can also review the Ansible logs for detailed information on the API calls and responses.

## Run line parameters description:

- `-i`: Specifies the inventory file containing host details.  
- `--e VARS_FILE_PATH`: Path to the variable file containing workflow inputs.  
- `-vvvv`: Enables verbose mode for detailed output.  

## Reference
Refer to the workflow's schema file (workflows/assurance_issues_management/schema/assurance_issues_management_schema.yml) for the definitive list of input parameters and their descriptions.

## Note: The environment used for the references in the above instructions is as follows:

```bash
python: 3.10.10
dnac_version: 2.3.7.9
ansible: 9.9.0
cisco.dnac: 6.32.0
dnacentersdk: 2.10.14
```
