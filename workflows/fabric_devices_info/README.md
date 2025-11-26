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

Ensure your Catalyst Center credentials are configured in the credentials file (`ex: inventory/demo_lab/hosts.yaml`):

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

For verbose output:
```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
workflows/fabric_devices_info/playbook/fabric_devices_info_playbook.yml \
--e VARS_FILE_PATH=./../vars/fabric_devices_info_input.yml \
-v
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
The UI display (example):
 ![alt text](./images/example_fabric_device_info.png)

### Example 1: Retrieve All Information in Fabric Site

This example retrieves all available information (fabric configuration, handoffs, onboarding status, connected devices, health metrics, and issues) for all device in a specific fabric site. If the requested_info parameter is not provided, it will default to retrieving all information.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
```
+ Playbook return:
```yaml
  msg:
  - 'The fabric devices filtered from the network devices are: [''204.1.2.1'', ''204.192.4.200'', ''204.1.2.3'', ''204.1.2.69'']'
  - - fabric_info:
      ...
  - - device_issues_info:
      ...
  - - fabric_devices_layer3_handoffs_sda_info:
      ...
  - - fabric_devices_layer3_handoffs_ip_info:
      ...
  - - fabric_devices_layer2_handoffs_info:
      ...
  - - connected_device_info:
      ...
  - - device_health_info:
      ...
  - - port_assignment_info:
      ...
  - - port_channel_info:
      ...
  - - ssid_info:
      ...
  - - provision_status_info:
      ...
```

### Example 2: Retrieve Fabric Information for Control Plane Nodes

This example retrieves all available information (fabric configuration) for control plane nodes in a specific fabric site. The results are saved to a YAML file with a timestamp.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
        fabric_device_role: "CONTROL_PLANE_NODE"
        requested_info:
          - fabric_info
        output_file_info:
          file_path: "tmp/fabric_devices/control_plane_info"
          file_format: "yaml"
          file_mode: "w"
          timestamp: true
```
+ Playbook return:
```yaml
    msg:
    - 'The fabric devices filtered from the network devices are: [''204.1.2.3'']'
    - - fabric_info:
        - device_ip: 204.1.2.3
          fabric_details:
          - borderDeviceSettings:
              borderTypes:
              - LAYER_3
              layer3Settings:
                borderPriority: 10
                importExternalRoutes: false
                isDefaultExit: true
                localAutonomousSystemNumber: '6100'
                prependAutonomousSystemCount: 0
            deviceRoles:
            - BORDER_NODE
            - CONTROL_PLANE_NODE
            fabricId: 47837ae3-be0e-4d47-bf64-4c048b401a7e
            id: de69ba65-90a7-47cc-8802-1db877cc0031
            networkDeviceId: d9116ff2-2b64-47bf-9f3a-8552e11b0c59
```

+ The file will be generated in:
```
fabric_devices_info/
├── README.md
├── playbook/
│   └── fabric_devices_info_playbook.yml
│   └── tmp/fabric_devices/control_plane_info.yaml
```

**What this does**: Targets the control plane node at IP 204.1.2.3 in the SAN JOSE fabric site, retrieves all 1 information categories (fabric_info), and saves the complete inventory to a timestamped YAML file for audit purposes (`control_plane_info.yaml`).

### Example 3: Retrieve Handoff Information Using IP Range

This example focuses on retrieving only fabric configuration and handoff details for border nodes within an IP address range. This is useful for documenting external connectivity configurations across multiple border devices.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
        fabric_device_role: "BORDER_NODE"
        device_identifier:
          - ip_address_range: "204.1.2.1-204.1.2.3"
        requested_info:
          - fabric_info
          - handoff_info
        output_file_info:
          file_path: "tmp/fabric_devices/border_handoffs"
          file_format: "json"
```
+ Playbook return:
```yaml
  msg:
  - 'No managed devices found for the following identifiers: IP(s) not found: 204.1.2.2. Device(s) may be unreachable, unmanaged, or not present in Catalyst Center inventory.'
  - 'The fabric devices filtered from the network devices are: [''204.1.2.3'']'
  - - fabric_info:
      - device_ip: 204.1.2.3
        fabric_details:
        - borderDeviceSettings:
            ...
  - - fabric_devices_layer3_handoffs_sda_info:
      - device_ip: 204.1.2.3
        handoff_layer3_sda_transit_info:
        - transitName: TRANSITSDA
          ...
  - - fabric_devices_layer3_handoffs_ip_info:
      - device_ip: 204.1.2.3
        handoff_layer3_ip_transit_info:
        - externalConnectivityIpPoolName: BorderHandOff_sub
          ...
          interfaceName: TenGigabitEthernet1/1/1
          localIpAddress: 204.1.16.61/30
          localIpv6Address: 2004:1:16::1:0:3d/126
          remoteIpAddress: 204.1.16.62/30
          remoteIpv6Address: 2004:1:16::1:0:3e/126
          tcpMssAdjustment: 0
          transitName: iptransit
          virtualNetworkName: WiredVNStatic
          vlanId: 3115
        ...
  - - fabric_devices_layer2_handoffs_info:
      - device_ip: 204.1.2.3
        handoff_layer2_info: []
```

**What this does**: Scans all border nodes in the IP range 204.1.2.1 to 204.1.2.3 at the SAN JOSE site, retrieves only fabric configuration and Layer 2/3 handoff details, and exports the results to a JSON file for integration with external tools (`border_handoffs.json`).

### Example 4: Retrieve Health and Issues by Hostname

This example monitors the operational status of specific by hostname. It retrieves only health metrics and active issues, making it ideal for troubleshooting or routine health checks.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
        device_identifier:
          - hostname:
              - "SJ-IM-1-9300.cisco.local"
        requested_info:
          - device_health_info
          - device_issues_info
```
+ Playbook return:
```yaml
    response:
    - 'The fabric devices filtered from the network devices are: [''204.1.2.69'']'
    - - device_issues_info:
        - device_ip: 204.1.2.69
          issue_details: []
    - - device_health_info:
        - device_ip: 204.1.2.69
          health_details:
            airQualityHealth: {}
            avgTemperature: 4733.333333333333
            band: {}
            clientCount: {}
            cpuHealth: 10
            cpuUlitilization: 2.0
            cpuUtilization: 2.0
            deviceFamily: SWITCHES_AND_HUBS
            deviceType: Cisco Catalyst 9300 Switch
            freeMemoryBufferHealth: -1
            freeTimerScore: -1
            interDeviceLinkAvailFabric: 10
            interDeviceLinkAvailHealth: 100
            interfaceLinkErrHealth: -1
            interferenceHealth: {}
            ipAddress: 204.1.2.69
            issueCount: 0
            location: Global/USA/SAN JOSE/SJ_BLD23
            macAddress: 8C:94:1F:67:39:00
            maxTemperature: 6000.0
            memoryUtilization: 48
            memoryUtilizationHealth: 10.0
            model: Cisco Catalyst 9300 Switch
            name: SJ-IM-1-9300.cisco.local
            noiseHealth: {}
            osVersion: 17.12.5
            overallHealth: 1
            packetPoolHealth: -1
            reachabilityHealth: REACHABLE
            utilizationHealth: {}
            uuid: 004e1986-c2f8-4e2d-a411-55b3355c226f
            wanLinkUtilization: -1.0
            wqePoolsHealth: -1
    status: success
```

**What this does**: Queries the edge node "SJ-IM-1-9300.cisco.local" at the SAN JOSE site for health metrics (CPU, memory, temperature) and active issues/alerts. This focused approach reduces API calls and provides quick health assessment without file output.

### Example 5: Retrieve Fabric Devices at a Site with Wait Time

This example retrieves information for specific fabric devices in a site, implementing a wait time for the fabric device to join during fabric deployments.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
        device_identifier:
          - ip_address: 
              - 10.4.213.2
        requested_info:
          - fabric_info
        timeout: 150
        retries: 12
        interval: 10
```
+ For example, wait for the fabric device to join the fabric with time wait (timeout: 1, retries: 1, interval: 1) (`very little wait time`)
```yaml
  response:
  - 'No managed devices found for the following identifiers: IP(s) not found: 10.4.213.2. Device(s) may be unreachable, unmanaged, or not present in Catalyst Center inventory.'
  - No managed devices found matching all specified identifiers (['ip_address', 'ip_address_range', 'serial_number', 'hostname']).
  - No managed devices found matching all specified identifiers (['ip_address', 'ip_address_range', 'serial_number', 'hostname']).
  - No fabric devices found for the given filters.
  status: success
...
total ----------------------------------------------------------------- 12.11s
Playbook run took 0 days, 0 hours, 0 minutes, 12 seconds
```

+ For example, wait for the fabric device to join the fabric with time wait (timeout: 100, retries: 1, interval: 1)
```yaml
  response:
  - 'No managed devices found for the following identifiers: IP(s) not found: 10.4.213.2. Device(s) may be unreachable, unmanaged, or not present in Catalyst Center inventory.'
  - No managed devices found matching all specified identifiers (['ip_address', 'ip_address_range', 'serial_number', 'hostname']).
  - No managed devices found matching all specified identifiers (['ip_address', 'ip_address_range', 'serial_number', 'hostname']).
  - No fabric devices found for the given filters.
  status: success
...
total ----------------------------------------------------------------- 211.46s
Playbook run took 0 days, 0 hours, 3 minutes, 31 seconds
```

**What this does**: Performs a complete inventory of all fabric devices (control plane, border, edge, extended, and wireless controller nodes) at the SAN JOSE office site. The extended timeout (more 150 seconds) and retry mechanism ensure reliable data collection even in environments with many devices or network latency.

### Example 6: Wireless Controller SSID Details

This example retrieves onboarding information for wireless controllers, including SSID configurations, WLAN profiles, and radio policies. This is particularly useful for wireless fabric deployments.

```yaml
fabric_device_info_details:
  - fabric_devices:
      - fabric_site_hierarchy: "Global/USA/SAN JOSE"
        fabric_device_role: "WIRELESS_CONTROLLER_NODE"
        device_identifier:
          - serial_number:
              - "FOX2639PAYD"
        requested_info:
          - onboarding_info
```
+ Playbook return:
```yaml
  response:
  - 'The fabric devices filtered from the network devices are: [''204.192.4.200'']'
  - - port_assignment_info:
      - device_ip: 204.192.4.200
        port_assignment_details: []
  - - port_channel_info:
      - device_ip: 204.192.4.200
        port_channel_details: []
  - - ssid_info:
      - device_ip: 204.192.4.200
        ssid_details:
        - adminStatus: true
          l2Security: open
          l3Security: open
          managed: true
          radioPolicy: 2.4GHz + 5GHz
          ssidName: a1
          wlanId: 17
          wlanProfileName: a1_profile
        - adminStatus: true
          l2Security: open
          l3Security: open
          managed: true
          radioPolicy: 2.4GHz + 5GHz
          ssidName: abc
          wlanId: 18
          wlanProfileName: abc_profile
  - - provision_status_info:
      - device_ip: 204.192.4.200
        provision_status:
          description: Wired Provisioned device detail retrieved successfully.
          deviceManagementIpAddress: 204.192.4.200
          siteNameHierarchy: Global/USA/SAN JOSE/SJ_BLD23
          status: success
  status: success
```

**What this does**: Targets a specific wireless controller by serial number at the SAN JOSE campus and retrieves detailed onboarding information including SSID configurations, port channel assignments, and wireless-specific fabric settings. Serial number identification ensures accuracy when IP addresses may change.



## References

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [cisco.dnac Collection](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/)
- [Module Documentation](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/fabric_devices_info_workflow_manager/)

*Note: The environment used for the references in the above instructions is as follows:*

```yaml
python: 3.12.0
dnac_version: 3.1.5
ansible: 9.9.0
dnacentersdk: 2.10.4
cisco.dnac: 6.42.0
```