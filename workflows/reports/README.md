# Cisco Catalyst Center Reports Management Playbooks

**Overview**

This module provides a comprehensive toolkit for managing reports in *Cisco Catalyst Center*. It supports creating, scheduling, and deleting reports with flexible configurations, enabling efficient report generation and management across your network infrastructure. Key features include:

- **Report Management**:  
  - **Create** reports with customizable views, field groups, and filters.
  - **Schedule** reports with immediate execution (SCHEDULE_NOW).
  - **Schedule** reports for later execution (SCHEDULE_LATER).
  - **Create recurring** reports with daily, weekly, or monthly schedules.
  - **Delete** existing reports and scheduled executions.

- **Flexible Delivery Options**:  
  - **Download** reports to a specified file path.
  - **Email notifications** with report attachments.
  - **Webhook integration** for automated report distribution.

- **Report Types and Views**:  
  - Support for multiple view groups including Compliance, Inventory, Network Devices, Access Point, Client, Security Advisories, and more.
  - Configurable field groups and custom field selection.
  - Multiple format options: CSV, PDF, JSON, TDE.

- **Advanced Filtering**:  
  - **Multi-select filters** for locations, device types, and other criteria.
  - **Time range filters** with predefined options (LAST_7_DAYS, LAST_24_HOURS, CUSTOM).
  - **Tree-based filters** for hierarchical site selection.

- **Bulk Operations**:  
  - **Create** and **schedule** multiple reports in a single operation.
  - **Delete** multiple reports with a single playbook execution.

**Version Added**: `6.43.0`  
*Note*: This version refers to the Cisco Catalyst Center Ansible collection.

---

## Workflow Steps

Follow these steps to configure and manage reports in *Cisco Catalyst Center* using Ansible playbooks.

### Step 1: Install and Generate Inventory

**Prepare your environment** by installing Ansible and the required *Cisco Catalyst Center* collection, then generate an inventory file.

1. **Install Ansible**:  
   Refer to the [official Ansible documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for installation instructions.

2. **Install Cisco Catalyst Center Collection**:  
   ```bash
   ansible-galaxy collection install cisco.dnac
   ```

3. **Generate Inventory**:  
   Create an Ansible inventory file (e.g., `inventory.yml`) with your *Cisco Catalyst Center* appliance details. Define variables such as `catalyst_center_host`, `catalyst_center_username`, and `catalyst_center_password`.  
   > **Note**: For security, consider using *Ansible Vault* to encrypt sensitive data like passwords.  
   ```yaml
   catalyst_center_hosts:
       hosts:
           your_catalyst_center_instance_name:
               catalyst_center_host: xx.xx.xx.xx
               catalyst_center_password: XXXXXXXX
               catalyst_center_port: 443
               catalyst_center_timeout: 60
               catalyst_center_username: admin
               catalyst_center_verify: false  # Enable for production with valid certificates
               catalyst_center_version: 2.3.7.9  # Specify the version
               catalyst_center_debug: true
               catalyst_center_log_level: INFO
               catalyst_center_log: true
   ```

---

### Step 2: Define Inputs and Validate

Define input variables and validate your configuration to ensure successful report management.

#### Define Input Variables
Create a variable file (e.g., `vars/reports_inputs.yml`) to specify the desired state of your reports for creation, scheduling, or deletion.

#### Schema for Reports Management

The following schema outlines the structure for configuring reports in *Cisco Catalyst Center*. Parameters are listed with their requirements and descriptions.

| **Parameter**       | **Type** | **Required** | **Default Value** | **Description**                                      |
|---------------------|----------|--------------|-------------------|------------------------------------------------------|
| `reports_details`   | List     | Yes          | `N/A`             | List of report configurations to create or manage.   |

##### Report Configuration (`generate_report`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `name`                | String     | Yes (for delete) | `N/A`        | Name of the report. Required for deletion, optional for creation.               |
| `new_report`          | Boolean    | No           | `true`            | Indicates if this is a new report creation.                                     |
| `view_group_name`     | String     | Yes          | `N/A`             | View group name (e.g., "Compliance", "Inventory", "Access Point").              |
| `view_group_version`  | String     | No           | `"2.0.0"`         | Version of the view group.                                                      |
| `tags`                | List       | No           | `N/A`             | List of tags for report categorization.                                         |
| `schedule`            | Dict       | Yes          | `N/A`             | Schedule configuration. See *Schedule Configuration*.                           |
| `deliveries`          | List       | Yes          | `N/A`             | List of delivery configurations. See *Delivery Configuration*.                  |
| `view`                | Dict       | Yes          | `N/A`             | View configuration including fields, format, and filters. See *View Configuration*. |

##### Schedule Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `schedule_type`       | String     | Yes          | `N/A`             | Type: "SCHEDULE_NOW", "SCHEDULE_LATER", "SCHEDULE_RECURRENCE".                  |
| `date_time`           | String     | Conditional  | `N/A`             | Date and time for scheduled execution. Format: "YYYY-MM-DD HH:MM AM/PM".        |
| `time_zone`           | String     | Yes          | `N/A`             | Time zone (e.g., "America/New_York", "Asia/Calcutta", "UTC").                   |
| `recurrence`          | Dict       | Conditional  | `N/A`             | Recurrence configuration for recurring reports. See *Recurrence Configuration*. |

##### Recurrence Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `recurrence_type`     | String     | Yes          | `N/A`             | Type: "WEEKLY" or "MONTHLY".                                                    |
| `days`                | List       | Conditional  | `N/A`             | Days for weekly recurrence: "MONDAY", "TUESDAY", etc., or "DAILY".              |
| `last_day_of_month`   | Boolean    | No           | `false`           | If true, report runs on the last day of the month (monthly only).               |
| `day_of_month`        | Integer    | No           | `N/A`             | Specific day of month (1-31) for monthly recurrence.                            |

##### Delivery Configuration

| **Parameter**            | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|--------------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `delivery_type`          | String     | Yes          | `N/A`             | Type: "DOWNLOAD", "NOTIFICATION", "WEBHOOK".                                    |
| `file_path`              | String     | Conditional  | `N/A`             | File path for DOWNLOAD delivery type.                                           |
| `notification_endpoints` | List       | Conditional  | `N/A`             | Email configuration for NOTIFICATION type. See *Notification Endpoints*.        |
| `email_attach`           | Boolean    | No           | `false`           | Whether to attach the report to notification emails.                            |
| `notify`                 | List       | No           | `N/A`             | Notification triggers: "IN_QUEUE", "IN_PROGRESS", "COMPLETED".                  |
| `webhook_name`           | String     | Conditional  | `N/A`             | Webhook name for WEBHOOK delivery type.                                         |

##### Notification Endpoints

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `email_addresses`     | List       | Yes          | `N/A`             | List of email addresses to receive notifications.                               |

##### View Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `view_name`           | String     | Yes          | `N/A`             | Name of the view to use for the report data.                                    |
| `field_groups`        | List       | Yes          | `N/A`             | List of field groups to include. See *Field Group Configuration*.              |
| `format`              | Dict       | Yes          | `N/A`             | Report format configuration. See *Format Configuration*.                        |
| `filters`             | List       | No           | `N/A`             | List of filters to apply to report data. See *Filter Configuration*.           |

##### Field Group Configuration

| **Parameter**               | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `field_group_name`          | String     | Yes          | `N/A`             | Name of the field group.                                                        |
| `field_group_display_name`  | String     | No           | `N/A`             | Display name for the field group.                                               |
| `fields`                    | List       | Yes          | `N/A`             | List of fields to include. See *Field Configuration*.                           |

##### Field Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `name`                | String     | Yes          | `N/A`             | Name of the field.                                                              |
| `display_name`        | String     | No           | `N/A`             | Display name for the field.                                                     |

##### Format Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `format_type`         | String     | Yes          | `N/A`             | Format type: "CSV", "PDF", "JSON", "TDE".                                       |

##### Filter Configuration

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `name`                | String     | Yes          | `N/A`             | Name of the filter.                                                             |
| `display_name`        | String     | No           | `N/A`             | Display name for the filter.                                                    |
| `filter_type`         | String     | Yes          | `N/A`             | Type: "MULTI_SELECT", "MULTI_SELECT_TREE", "SINGLE_SELECT_ARRAY", "TIME_RANGE". |
| `value`               | Dict/List  | Yes          | `N/A`             | Filter value configuration. Structure varies by filter type.                    |

#### Example Input Files

**Prerequisites**  
Before creating reports, ensure the following components exist in *Cisco Catalyst Center*:  
- **View Groups and Views**: Must be pre-configured in Catalyst Center for the report types you want to create.
- **Site Hierarchy**: Sites must be defined if using location-based filters.
- **Network Interfaces and VLANs**: Required if reporting on interface or VLAN configurations.
- **Webhook Endpoints**: Must be configured if using webhook delivery type.

##### 1. **Create Report with Immediate Execution**  
*Example*: Create a compliance report that executes immediately.

```yaml
catalyst_center_version: 3.1.3
reports_details:
  - generate_report:
      name: "Network Compliance Report - Immediate"
      new_report: true
      view_group_name: "Compliance"
      view_group_version: "2.0.0"
      tags:
        - compliance
        - immediate
      
      schedule:
        schedule_type: "SCHEDULE_NOW"
        time_zone: "America/New_York"
      
      deliveries:
        - delivery_type: "DOWNLOAD"
          file_path: "/tmp/reports"
      
      view:
        view_name: "Network Device Compliance"
        
        field_groups:
          - field_group_name: "Compliance"
            field_group_display_name: "Compliance Details"
            fields:
              - name: "deviceName"
                display_name: "Device Name"
              - name: "ipAddress"
                display_name: "IP Address"
              - name: "complianceStatus"
                display_name: "Compliance Status"
        
        format:
          format_type: "CSV"
        
        filters:
          - name: "Location"
            display_name: "Network Location"
            filter_type: "MULTI_SELECT_TREE"
            value:
              - value: "Global"
                display_value: "Global"
```

##### 2. **Schedule Report for Later Execution**  
*Example*: Schedule an executive summary report for a specific date and time with email notification.

```yaml
catalyst_center_version: 3.1.3
reports_details:
  - generate_report:
      name: "Executive Summary - Scheduled"
      new_report: true
      view_group_name: "Executive Summary"
      view_group_version: "2.0.0"
      tags:
        - executive
        - scheduled
      
      schedule:
        schedule_type: "SCHEDULE_LATER"
        date_time: "2025-12-25 09:00 AM"
        time_zone: "America/New_York"
      
      deliveries:
        - delivery_type: "NOTIFICATION"
          notification_endpoints:
            - email_addresses:
                - "admin@company.com"
                - "reports@company.com"
          email_attach: true
          notify:
            - "COMPLETED"
      
      view:
        view_name: "Executive Summary"
        
        field_groups: []
        
        format:
          format_type: "PDF"
        
        filters:
          - name: "Location"
            display_name: "Site Location"
            filter_type: "MULTI_SELECT_TREE"
            value:
              - value: "Global"
                display_value: "Global"
```

##### 3. **Create Recurring Weekly Report**  
*Example*: Create a weekly AP performance report with webhook delivery.

```yaml
catalyst_center_version: 3.1.3
reports_details:
  - generate_report:
      name: "Weekly AP Performance Report"
      new_report: true
      view_group_name: "Access Point"
      view_group_version: "2.0.0"
      tags:
        - wireless
        - weekly
        - performance
      
      schedule:
        schedule_type: "SCHEDULE_RECURRENCE"
        date_time: "2025-12-15 06:00 AM"
        time_zone: "UTC"
        recurrence:
          recurrence_type: "WEEKLY"
          days:
            - "MONDAY"
            - "WEDNESDAY"
            - "FRIDAY"
      
      deliveries:
        - delivery_type: "WEBHOOK"
          webhook_name: "report_webhook_endpoint"
      
      view:
        view_name: "AP"
        
        field_groups:
          - field_group_name: "apDetailByAP"
            field_group_display_name: "AP Details"
            fields:
              - name: "nwDeviceName"
                display_name: "AP Name"
              - name: "managementIpAddress"
                display_name: "Management IP"
              - name: "siteHierarchy"
                display_name: "Site"
        
        format:
          format_type: "JSON"
        
        filters:
          - name: "Location"
            display_name: "AP Location"
            filter_type: "MULTI_SELECT_TREE"
            value:
              - value: "Global/US"
                display_value: "United States"
          
          - name: "TimeRange"
            display_name: "Time Period"
            filter_type: "TIME_RANGE"
            value:
              time_range_option: "LAST_7_DAYS"
```

##### 4. **Create Monthly Recurring Report**  
*Example*: Create a monthly client detail report that runs on the last day of each month.

```yaml
catalyst_center_version: 2.3.7.9
reports_details:
  - generate_report:
      name: "Monthly Client Detail Report"
      new_report: true
      view_group_name: "Client"
      view_group_version: "2.0.0"
      tags:
        - client
        - monthly
      
      schedule:
        schedule_type: "SCHEDULE_RECURRENCE"
        date_time: "2025-12-01 08:00 AM"
        time_zone: "Asia/Calcutta"
        recurrence:
          recurrence_type: "MONTHLY"
          last_day_of_month: true
      
      deliveries:
        - delivery_type: "NOTIFICATION"
          notification_endpoints:
            - email_addresses:
                - "network-admin@example.com"
          email_attach: true
          notify:
            - "COMPLETED"
      
      view:
        view_name: "Client Detail"
        
        field_groups: []
        
        format:
          format_type: "CSV"
        
        filters:
          - name: "Location"
            display_name: "Client Location"
            filter_type: "MULTI_SELECT_TREE"
            value:
              - value: "Global"
                display_value: "Global"
          
          - name: "Time Range"
            display_name: "Analysis Period"
            filter_type: "TIME_RANGE"
            value:
              time_range_option: "LAST_30_DAYS"
```

##### 5. **Delete Reports**  
*Example*: Delete one or more reports by specifying their names and view information.  
> **Warning**: Deleting reports will remove all scheduled executions. Verify before proceeding.

```yaml
catalyst_center_version: 3.1.3
reports_details:
  - generate_report:
      name: "Network Compliance Report - Immediate"
      view_group_name: "Compliance"
      view:
        view_name: "Network Device Compliance"
  
  - generate_report:
      name: "Weekly AP Performance Report"
      view_group_name: "Access Point"
      view:
        view_name: "AP"
```

---

#### Validate Configuration
> **Important**: Validate your input schema before executing the playbook to ensure all parameters are correctly formatted.  
Run the following command to validate your input file against the schema:  
```bash
./tools/validate.sh -s ./workflows/reports/schema/reports_schema.yml -d ./workflows/reports/vars/reports_inputs.yml
```

---

### Step 3: Deploy and Verify

**Deploy** your configuration to *Cisco Catalyst Center* and **verify** the changes.

1. **Deploy Configuration**:  
   Run the playbook to apply the reports configuration. Ensure the input file is validated before execution. Specify the input file path using the `--e` variable (`VARS_FILE_PATH`).

   ### a. Create or Update Reports (state = 'merged')
   ```bash
   ansible-playbook -i inventory/demo_lab/hosts.yaml \
   workflows/reports/playbook/reports_workflow_playbook.yml \
   --e VARS_FILE_PATH=./../vars/reports_inputs.yml \
   -vvv
   ```

   ### b. Delete Reports (state = 'deleted')
   ```bash
   ansible-playbook -i inventory/demo_lab/hosts.yaml \
   workflows/reports/playbook/delete_reports_playbook.yml \
   --e VARS_FILE_PATH=./../vars/delete_reports_inputs.yml \
   -vvv
   ```

   > **Note**: If an error occurs (e.g., invalid input or API failure), the playbook will halt and display details. Check the execution logs for troubleshooting.

2. **Verify Deployment**:  
   After execution, verify the configuration in the *Cisco Catalyst Center* UI:
   - Navigate to **Reports** > **Report List** to view created reports.
   - Check **Scheduled Reports** to verify scheduled executions.
   - Review report execution history for completed reports.
   - Verify delivery configurations (email notifications, webhooks, or downloads).
   
   If `catalyst_center_debug` is enabled, review the logs for detailed operation information.

---

## Example Output

**Successful Report Creation:**
```yaml
msg: 'Reports created/scheduled successfully'
response:
  - profile_name: Network Compliance Report - Immediate
    profile_status: Report successfully created and scheduled for immediate execution
  - profile_name: Weekly AP Performance Report
    profile_status: Recurring report successfully created with weekly schedule
status: success
```

**Successful Report Deletion:**
```yaml
msg: 'Reports deleted successfully'
response:
  - Network Compliance Report - Immediate: Report successfully deleted
  - Weekly AP Performance Report: Report successfully deleted
status: success
```

---

## References

**Environment Details**  
The following environment was used for testing:  

| **Component**         | **Version** |
|-----------------------|-------------|
| Python                | `3.12.0`    |
| Cisco Catalyst Center | `3.1.3`     |
| Ansible               | `9.9.0`     |
| cisco.dnac Collection | `6.43.0`    |
| dnacentersdk          | `2.8.8`     |

For detailed documentation, refer to:  
- [Ansible Galaxy: Cisco Catalyst Center Collection](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/reports_workflow_manager/)  
- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Reports Workflow Manager Module Documentation](https://github.com/cisco-en-programmability/catalyst-center-ansible-dev/blob/main/plugins/modules/reports_workflow_manager.py)
