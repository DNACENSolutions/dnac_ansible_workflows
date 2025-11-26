# Fabric Devices Info Workflow

## Overview

The Fabric Devices Info workflow retrieves comprehensive fabric device information from Cisco Catalyst Center for Software-Defined Access (SDA) deployments. This workflow enables administrators to collect detailed information about fabric devices including configuration, health metrics, onboarding status, and connectivity details.

## Features

- Retrieve fabric device information from SDA fabric sites
- Filter devices by fabric site hierarchy and device role
- Support multiple device identification methods (IP address, hostname, serial number, IP range)
- Selective information retrieval across six categories (fabric_info, handoff_info, onboarding_info, connected_devices_info, device_health_info, device_issues_info)
- Configurable retry mechanisms and timeout handling
- File output support with JSON/YAML formats
- Append or overwrite file modes with optional timestamps

## Prerequisites

- Cisco Catalyst Center 2.3.7.9 or later
- Ansible 2.9 or higher
- Python 3.9 or higher
- dnacentersdk 2.9.3 or higher
- cisco.dnac collection 6.42.0 or higher
- SDA fabric site(s) configured in Catalyst Center
- Fabric devices provisioned and operational

## Workflow Structure

```
fabric_devices_info/
├── README.md
├── playbook/
│   └── fabric_devices_info_playbook.yml
├── vars/
│   └── fabric_devices_info_input.yml
└── schema/
    └── fabric_devices_info_schema.yml
```

## Schema File

The workflow uses a Yamale schema file to validate input parameters before execution. The schema ensures all required fields are present and values are within acceptable ranges.

**Location**: `schema/fabric_devices_info_schema.yml`

**Key Validations**:
- `fabric_site_hierarchy`: Required string field
- `fabric_device_role`: Optional enum with valid fabric roles
- `device_identifier`: Optional list with IP address, hostname, serial number, or IP range
- `timeout`: Integer between 1-3600 seconds
- `retries`: Integer between 0-10
- `interval`: Integer between 1-300 seconds
- `requested_info`: Optional list of valid information categories
- `output_file_info`: Optional file output configuration with format and mode validation

## Input Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fabric_site_hierarchy` | string | Hierarchical path of the fabric site |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fabric_device_role` | enum | None | Filter by fabric device role (CONTROL_PLANE_NODE, BORDER_NODE, EDGE_NODE, EXTENDED_NODE, WIRELESS_CONTROLLER_NODE) |
| `device_identifier` | list | None | Device identification criteria |
| `timeout` | integer | 120 | Maximum wait time in seconds (1-3600) |
| `retries` | integer | 3 | Number of retry attempts (0-10) |
| `interval` | integer | 10 | Delay between retries in seconds (1-300) |
| `requested_info` | list | all | Information types to retrieve |
| `output_file_info` | dict | None | File output configuration |

### Device Identifier Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip_address` | list | List of management IP addresses |
| `ip_address_range` | string | IP range in "start-end" format |
| `serial_number` | list | Device serial numbers |
| `hostname` | list | Device hostnames |

**Note**: `ip_address` and `ip_address_range` are mutually exclusive.

### Output File Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | string | - | Absolute path without extension |
| `file_format` | enum | yaml | Output format: 'json' or 'yaml' |
| `file_mode` | enum | w | Write mode: 'w' or 'a' |
| `timestamp` | boolean | false | Include timestamp in output |

## Getting Started

### Step 1: Update Credentials File

Ensure your Catalyst Center credentials are configured in the credentials file:

```yaml
catalyst_center_host: "xxxxx"
catalyst_center_username: "xxxxx"
catalyst_center_password: "xxxxx"
catalyst_center_verify: false
catalyst_center_port: 443
catalyst_center_version: "2.3.7.9"
catalyst_center_debug: false
catalyst_center_log: true
catalyst_center_log_level: "INFO"
```

### Step 2: Customize Input Variables

1. Navigate to the vars directory:
   ```bash
   cd dnac_ansible_workflows/workflows/fabric_devices_info/vars/
   ```

2. Edit the input file with your fabric device query parameters:
   ```bash
   vi fabric_devices_info_input.yml
   ```

3. Configure the following parameters:
   - **fabric_site_hierarchy**: (Required) The full hierarchical path of your SDA fabric site
   - **fabric_device_role**: (Optional) Filter by device role (CONTROL_PLANE_NODE, BORDER_NODE, EDGE_NODE, EXTENDED_NODE, WIRELESS_CONTROLLER_NODE)
   - **device_identifier**: (Optional) Filter by IP address, hostname, serial number, or IP range
   - **requested_info**: (Optional) Select specific information categories or leave blank for all
   - **timeout/retries/interval**: (Optional) Adjust retry mechanisms as needed
   - **output_file_info**: (Optional) Configure file output with path, format, and mode

Example configuration:
```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/San Jose/Building23"
        fabric_device_role: "BORDER_NODE"
        device_identifier:
          - ip_address:
              - "204.1.2.2"
        requested_info:
          - fabric_info
          - handoff_info
        output_file_info:
          file_path: "/tmp/fabric_devices/border_nodes"
          file_format: "yaml"
          file_mode: "w"
          timestamp: true
```

### Step 3: Validate Input Schema

Validate your input file against the schema before running the playbook:

```bash
cd dnac_ansible_workflows/workflows/network_devices_info/
yamale -s schema/network_devices_info_schema.yml vars/network_devices_info_input.yml
```

If validation passes, you'll see:
```
Validating fabric_devices_info_input.yml...
Validation success! 👍
```

### Step 4: Run the Playbook

Execute the playbook with your inventory:

```bash
ansible-playbook playbook/fabric_devices_info_playbook.yml -e @dnac_ansible_workflows/workflows/fabric_devices_info/vars/fabric_devices_info_input.yml -vvvv
```

### Step 5: Verify the Results

1. **Check Ansible Output**: Review the playbook execution results showing:
   - List of fabric devices that match your filters
   - Retrieved information for each requested category
   - Success or error messages

2. **Review File Output** (if configured):
   ```bash
   cat /tmp/fabric_devices/border_nodes.yaml
   ```

3. **Verify Information Retrieved**: Confirm that the expected information categories are present in the output

## Usage Examples

### Example 1: Retrieve All Information for Control Plane Nodes

This example retrieves all available information (fabric configuration, handoffs, onboarding status, connected devices, health metrics, and issues) for control plane nodes in a specific fabric site. The results are saved to a YAML file with a timestamp.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/San Jose/Building23"
        fabric_device_role: "CONTROL_PLANE_NODE"
        device_identifier:
          - ip_address:
              - "204.1.2.2"
        output_file_info:
          file_path: "/tmp/fabric_devices/control_plane_info"
          file_format: "yaml"
          file_mode: "w"
          timestamp: true
```

**What this does**: Targets the control plane node at IP 204.1.2.2 in the San Jose Building23 fabric site, retrieves all six information categories, and saves the complete inventory to a timestamped YAML file for audit purposes.

### Example 2: Retrieve Handoff Information Using IP Range

This example focuses on retrieving only fabric configuration and handoff details for border nodes within an IP address range. This is useful for documenting external connectivity configurations across multiple border devices.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/New York/NY_BLD1"
        fabric_device_role: "BORDER_NODE"
        device_identifier:
          - ip_address_range: "192.168.1.1-192.168.1.50"
        requested_info:
          - fabric_info
          - handoff_info
        output_file_info:
          file_path: "/tmp/fabric_devices/border_handoffs"
          file_format: "json"
```

**What this does**: Scans all border nodes in the IP range 192.168.1.1 to 192.168.1.50 at the New York site, retrieves only fabric configuration and Layer 2/3 handoff details, and exports the results to a JSON file for integration with external tools.

### Example 3: Retrieve Health and Issues by Hostname

This example monitors the operational status of specific edge nodes by hostname. It retrieves only health metrics and active issues, making it ideal for troubleshooting or routine health checks.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/Austin/Building5"
        fabric_device_role: "EDGE_NODE"
        device_identifier:
          - hostname:
              - "AUS-EDGE-01.cisco.local"
        requested_info:
          - device_health_info
          - device_issues_info
```

**What this does**: Queries the edge node "AUS-EDGE-01.cisco.local" at the Austin Building5 site for health metrics (CPU, memory, temperature) and active issues/alerts. This focused approach reduces API calls and provides quick health assessment without file output.

### Example 4: Retrieve All Fabric Devices in a Site

This example retrieves comprehensive information for all fabric devices in a site without any role or device filtering. It includes extended timeout and retry settings for large fabric deployments.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/Europe/London/LDN_Office"
        timeout: 150
        retries: 3
        interval: 10
```

**What this does**: Performs a complete inventory of all fabric devices (control plane, border, edge, extended, and wireless controller nodes) at the London office site. The extended timeout (150 seconds) and retry mechanism ensure reliable data collection even in environments with many devices or network latency.

### Example 5: Wireless Controller SSID Details

This example retrieves onboarding information for wireless controllers, including SSID configurations, WLAN profiles, and radio policies. This is particularly useful for wireless fabric deployments.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/San Francisco/SF_Campus"
        fabric_device_role: "WIRELESS_CONTROLLER_NODE"
        device_identifier:
          - serial_number:
              - "FCW2345A0B1"
        requested_info:
          - onboarding_info
```

**What this does**: Targets a specific wireless controller by serial number at the San Francisco campus and retrieves detailed onboarding information including SSID configurations, port channel assignments, and wireless-specific fabric settings. Serial number identification ensures accuracy when IP addresses may change.



## References

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [cisco.dnac Collection](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/)
- [Module Documentation](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/fabric_devices_info_workflow_manager/)

