# Assurance Health Score Settings Playbook
## Module Reference

Playbook for workflow Module: `assurance_device_health_score_settings_workflow_manager`

## Overview

This module provides resource management for assurance Health score settings in Cisco Catalyst Center.


**Description:** 
This module provides capabilities to configure and manage Assurance Health Score settings in Cisco Catalyst Center. It enables fine-tuned health monitoring by adjusting KPI thresholds and device-level scoring logic. Key features include:
  - **Health Score Configuration:**
    - Update and manage health score calculation parameters.
    - Define KPI thresholds and scoring rules specific to network device types.
    - Customize health scoring behavior based on operational priorities.

  - **Device-Specific Customization:**
    - Assign unique health score configurations per device type (e.g., access, core, distribution).
    - Control how individual KPIs influence the overall device health score.

  - **KPI Inclusion/Exclusion:**
    - Exclude specific KPIs from health score calculation to avoid skewing device performance metrics.
    - Ensure that excluded KPIs do not impact score trends or alerting.

  - **Health Score Computation Logic:**
    - Calculates the overall health score using the lowest score among the included KPIs.
    - Reflects worst-case operational scenarios for more conservative monitoring.

  - **Third-Party Device Handling:**
    - Health score configuration is not applicable to third-party devices and is automatically bypassed.

**Version Added:**  
`6.32.0`

---

This README outlines the steps to use the Ansible playbooks for managing assurance Health score settings in Cisco Catalyst Center.

## Workflow Steps

This workflow typically involves the following steps:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary collections for Cisco Catalyst Center.

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

### Step 2: Define Inputs and Validate

This step involves preparing the input data for configuring Assurance Health Score Settings and validating the KPI thresholds per device type.

1.  **Define Input Variables:** Create the variable file at (e.g., `workflows/assurance_health_score_settings/vars/assurance_health_score_settings_inputs.yml`). This file should contain the list of KPI names and threshold values for various device types that you want to configure.

2.  **Review Structure and Options:** Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/assurance_device_health_score_settings_workflow_manager/


## Structure

- **images/**: Image assets
- **jinja_template/**: Jinja templates
- **playbook/**: Ansible playbooks
- **schema/**: Schema definitions
- **vars/**: Variable files

## Usage

### run Schema validation
catc_ansible_workflows %  yamale -s workflows/assurance_health_score_settings/schema/assurance_health_score_settings_schema.yml workflows/assurance_health_score_settings/vars/assurance_health_score_settings_inputs.yml
Validating workflows/assurance_health_score_settings/vars/assurance_health_score_settings_inputs.yml...
Validation success! 👍

## Example Input File
file: assurance_healthscore_settings.yml

1. Health Score Custom Settings for device family Unified Access Point
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 2.4 GHz
      include_for_overall_health: true
      threshold_value: 70
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 5 GHz
      include_for_overall_health: true
      threshold_value: 74
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 6 GHz
      include_for_overall_health: true
      threshold_value: 73
    - device_family: UNIFIED_AP
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 45
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: CPU Utilization
      include_for_overall_health: true
      threshold_value: 46
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 2.4 GHz
      include_for_overall_health: true
      threshold_value: 35
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 5 GHz
      include_for_overall_health: true
      threshold_value: 57
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 6 GHz
      include_for_overall_health: true
      threshold_value: 65
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 85
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 2.4 GHz
      include_for_overall_health: true
      threshold_value: -95
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 5 GHz
      include_for_overall_health: true
      threshold_value: -38
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 6 GHz
      include_for_overall_health: true
      threshold_value: -37
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 2.4 GHz
      include_for_overall_health: true
      threshold_value: 91
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 5 GHz
      include_for_overall_health: true
      threshold_value: 81
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 6 GHz
      include_for_overall_health: true
      threshold_value: 72
      synchronize_to_issue_threshold: false
```
mapping config to UI Actions:
!(./images/unified_AP_custom1.png)
!(./images/unified_AP_custom2.png)

2. Health Score Custom Settings for device family wired client
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: WIRED_CLIENT
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 60
      synchronize_to_issue_threshold: false
```
mapping config to UI Actions:
!(./images/wired_client_custom.png)

3. Health Score Custom Settings for device family wireless client
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
      - device_family: WIRELESS_CLIENT
        kpi_name: Connectivity SNR
        include_for_overall_health: true
        threshold_value: 35
      - device_family: WIRELESS_CLIENT
        kpi_name: Connectivity RSSI
        include_for_overall_health: true
        threshold_value: -70
        synchronize_to_issue_threshold: true
```
mapping config to UI Actions:
!(./images/wireless_client_custom.png)

4. Health Score Custom Settings for device family wireless controler
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: false
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Free Mbuf
      include_for_overall_health: true
      threshold_value: 40
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Free Timer
      include_for_overall_health: true
      threshold_value: 30
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 20
    - device_family: WIRELESS_CONTROLLER
      kpi_name: LISP Session Status
      include_for_overall_health: false
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 10
      synchronize_to_issue_threshold: false
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Packet Pool
      include_for_overall_health: false
    - device_family: WIRELESS_CONTROLLER
      kpi_name: WQE Pool
      include_for_overall_health: false
```
mapping config to UI Actions:
!(./images/wireless_controller_custom.png)

5. Health Score Custom Setting for device family switches and hub
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: SWITCH_AND_HUB
      kpi_name: AAA server reachability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Control Plane (BGP)
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Control Plane (PubSub)
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Peer Node for INFRA VN
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Peer Node
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Transit Control Plane
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session to Spine
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Cisco TrustSec environment data download status
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: CPU Utilization
      include_for_overall_health: true
      threshold_value: 90
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Extended Node Connectivity
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Fabric Multicast RP Reachability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Inter-device Link Availability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Internet Availability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Link Discard
      include_for_overall_health: true
      threshold_value: 30
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 20
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: LISP Session from Border to Transit Site Control Plane
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: LISP Session Status
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 90
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Peer Status
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session from Border to Transit Site Control Plane
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session Status for INFRA VN
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session Status
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Remote Internet Availability
      include_for_overall_health: false
    - device_family: SWITCH_AND_HUB
      kpi_name: VNI Status
      include_for_overall_health: false
```
mapping config to UI Actions:
!(./images/switches_and_hub_custom1.png)
!(./images/switches_and_hub_custom2.png)
!(./images/switches_and_hub_custom3.png)

6. Health Score Custom Setting for device family Router
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: ROUTER
      kpi_name: Link Utilization
      include_for_overall_health: false
      threshold_value: 60
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Control Plane (BGP)
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Control Plane (PubSub)
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Peer Node for INFRA VN
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Peer Node
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Transit Control Plane
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: BGP Session to Spine
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Cisco TrustSec environment data download status
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: CPU Utilization
      include_for_overall_health: false
      threshold_value: 60
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Extended Node Connectivity
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Fabric Multicast RP Reachability
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Inter-device Link Availability
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Internet Availability
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Link Discard
      include_for_overall_health: false
      threshold_value: 60
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Link Error
      include_for_overall_health: false
      threshold_value: 60
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: LISP Session from Border to Transit Site Control Plane
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: LISP Session Status
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Memory Utilization
      include_for_overall_health: false
      threshold_value: 60
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Peer Status
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Pub-Sub Session from Border to Transit Site Control Plane
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Pub-Sub Session Status for INFRA VN
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Pub-Sub Session Status
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: Remote Internet Availability
      include_for_overall_health: false
    - device_family: ROUTER
      kpi_name: VNI Status
      include_for_overall_health: false
```
mapping config to UI Actions:
!(./images/router_custom1.png)
!(./images/router_custom2.png)
!(./images/router_custom3.png)

7. Health Score Default Settings for device family Unified Access Point
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 2.4 GHz
      include_for_overall_health: true
      threshold_value: 60
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 5 GHz
      include_for_overall_health: true
      threshold_value: 75
    - device_family: UNIFIED_AP
      kpi_name: Air Quality 6 GHz
      include_for_overall_health: true
      threshold_value: 75
    - device_family: UNIFIED_AP
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 1
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: CPU Utilization
      include_for_overall_health: true
      threshold_value: 90
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 2.4 GHz
      include_for_overall_health: true
      threshold_value: 50
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 5 GHz
      include_for_overall_health: true
      threshold_value: 20
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Interference 6 GHz
      include_for_overall_health: true
      threshold_value: 20
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 90
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 2.4 GHz
      include_for_overall_health: true
      threshold_value: -81
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 5 GHz
      include_for_overall_health: true
      threshold_value: -83
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: Noise 6 GHz
      include_for_overall_health: true
      threshold_value: -83
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 2.4 GHz
      include_for_overall_health: true
      threshold_value: 70
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 5 GHz
      include_for_overall_health: true
      threshold_value: 70
      synchronize_to_issue_threshold: false
    - device_family: UNIFIED_AP
      kpi_name: RF Utilization 6 GHz
      include_for_overall_health: true
      threshold_value: 70
      synchronize_to_issue_threshold: false
```
mapping config to UI Actions:
!(./images/unified_AP_default1.png)
!(./images/unified_AP_default2.png)

8. Health Score Default Settings for device family wired client
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: WIRED_CLIENT
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 1
      synchronize_to_issue_threshold: false
```
mapping config to UI Actions:
!(./images/wired_client_default.png)

9. Health Score Default Setting for device family wireless client
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
      - device_family: WIRELESS_CLIENT
        kpi_name: Connectivity SNR
        include_for_overall_health: true
        threshold_value: 9
      - device_family: WIRELESS_CLIENT
        kpi_name: Connectivity RSSI
        include_for_overall_health: true
        threshold_value: -72
        synchronize_to_issue_threshold: true
```
mapping config to UI Actions:
!(./images/wireless_client_default.png)

10. Health Score Default Settings for device family wireless controler
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: true
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Free Mbuf
      include_for_overall_health: true
      threshold_value: 20
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Free Timer
      include_for_overall_health: true
      threshold_value: 20
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 1
    - device_family: WIRELESS_CONTROLLER
      kpi_name: LISP Session Status
      include_for_overall_health: true
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 95
      synchronize_to_issue_threshold: true
    - device_family: WIRELESS_CONTROLLER
      kpi_name: Packet Pool
      include_for_overall_health: true
    - device_family: WIRELESS_CONTROLLER
      kpi_name: WQE Pool
      include_for_overall_health: true
```
mapping config to UI Actions:
!(./images/wireless_controller_default.png)

11. Health Score Default Setting for device family Switches and hub
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: SWITCH_AND_HUB
      kpi_name: AAA server reachability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Control Plane (BGP)
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Control Plane (PubSub)
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Peer Node for INFRA VN
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Peer Node
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session from Border to Transit Control Plane
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: BGP Session to Spine
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Cisco TrustSec environment data download status
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: CPU Utilization
      include_for_overall_health: true
      threshold_value: 95
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Extended Node Connectivity
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Fabric Multicast RP Reachability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Inter-device Link Availability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Internet Availability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Link Discard
      include_for_overall_health: true
      threshold_value: 10
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 1
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: LISP Session from Border to Transit Site Control Plane
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: LISP Session Status
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 95
      synchronize_to_issue_threshold: false
    - device_family: SWITCH_AND_HUB
      kpi_name: Peer Status
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session from Border to Transit Site Control Plane
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session Status for INFRA VN
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Pub-Sub Session Status
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: Remote Internet Availability
      include_for_overall_health: true
    - device_family: SWITCH_AND_HUB
      kpi_name: VNI Status
      include_for_overall_health: true
```
mapping config to UI Actions:
!(./images/switches_and_hub_default.png)
!(./images/switches_and_hub_default2.png)
!(./images/switches_and_hub_default3.png)

12. Health Score Default Setting for device family Router
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: ROUTER
      kpi_name: Link Utilization
      include_for_overall_health: true
      threshold_value: 90
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Control Plane (BGP)
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Control Plane (PubSub)
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Peer Node for INFRA VN
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Peer Node
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: BGP Session from Border to Transit Control Plane
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: BGP Session to Spine
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Cisco TrustSec environment data download status
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: CPU Utilization
      include_for_overall_health: true
      threshold_value: 95
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Extended Node Connectivity
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Fabric Control Plane Reachability
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Fabric Multicast RP Reachability
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Inter-device Link Availability
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Internet Availability
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Link Discard
      include_for_overall_health: true
      threshold_value: 10
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 1
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: LISP Session from Border to Transit Site Control Plane
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: LISP Session Status
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Memory Utilization
      include_for_overall_health: true
      threshold_value: 95
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Peer Status
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Pub-Sub Session from Border to Transit Site Control Plane
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Pub-Sub Session Status for INFRA VN
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Pub-Sub Session Status
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: Remote Internet Availability
      include_for_overall_health: true
    - device_family: ROUTER
      kpi_name: VNI Status
      include_for_overall_health: true
```
mapping config to UI Actions:
!(./images/router_default1.png)
!(./images/router_default2.png)
!(./images/router_default3.png)


**Validate Configuration:** 
To ensure a successful execution of the playbooks with your specified inputs, follow these steps:

    **Input Validation**:
    Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command *./tools/validate.sh -s* to perform the validation providing the schema path -d and the input path.

```bash
./tools/validate.sh -s ./workflows/assurance_health_score_settings/schema/assurance_health_score_settings_schema.yml -d ./workflows/assurance_health_score_settings/vars/assurance_health_score_settings_inputs.yml
```

### Deploy and Verify

This is the final step where you deploy the configuration to Cisco Catalyst Center and verify the changes.

**Deploy Configuration:** 

Run the playbook to seamlessly apply the wireless network profile configuration defined in your input variables to Cisco Catalyst Center. 
Before proceeding, ensure that the input validation step has been completed successfully, with no errors detected in the provided variables. Once validated, execute the playbook by specifying the input file path using the --e variable as VARS_FILE_PATH. The VARS_FILE_PATH must be provided as a full path to the input file.
This ensures that the configuration is accurately deployed to Cisco Catalyst Center, automating the setup process and reducing the risk of manual errors.

```bash
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/assurance_health_score_settings/playbook/assurance_health_score_settings_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/assurance_health_score_settings_inputs.yml -vvvvvv    
```

If there is an error in the input or an issue with the API call during execution, the playbook will halt and display the relevant error details.

### Executing playbooks with inputs
```bash
(ansible-venv) pawansi@PAWANSI-M-7J1W CatC_SD_Access_campus % ansible-playbook -i /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible_inventory/catalystcenter_inventory/hosts.yml /Users/pawansi/workspace/CatC_Configs/catc_ansible_workflows/workflows/assurance_health_score_settings/playbook/assurance_health_score_settings_playbook.yml --e VARS_FILE_PATH=/Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/catc_configs/global/assurance_healthscore_settings.yml -vvv

 72570 1746308688.45220: starting run
ansible-playbook [core 2.18.3]
  config file = /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible.cfg
  configured module search path = ['/Users/pawansi/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/pawansi/workspace/CatC_Configs/venv-anisible/lib/python3.11/site-packages/ansible
  ansible collection location = /Users/pawansi/.ansible/collections:/usr/share/ansible/collections
  executable location = /Users/pawansi/workspace/CatC_Configs/venv-anisible/bin/ansible-playbook
  python version = 3.11.10 (main, Sep  7 2024, 01:03:31) [Clang 15.0.0 (clang-1500.3.9.4)] (/Users/pawansi/workspace/CatC_Configs/venv-anisible/bin/python)
  jinja version = 3.1.5
  libyaml = True
Using /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible.cfg as config file
Reading vault password file: /Users/pawansi/.vault_pass.txt
 72570 1746308688.45498: Added group all to inventory
 72570 1746308688.45501: Added group ungrouped to inventory
 72570 1746308688.45503: Group all now contains ungrouped
 72570 1746308688.45507: Examining possible inventory source: /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible_inventory/catalystcenter_inventory/hosts.yml
setting up inventory plugins
Loading collection ansible.builtin from 
...
up=False, tasks child state? (None), rescue child state? (None), always child state? (None), did rescue? False, did start at task? False

PLAY RECAP *********************************************************************************************************************************************************************************
catalyst_center53          : ok=7    changed=0    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   
```