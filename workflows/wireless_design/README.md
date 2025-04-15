# Cisco Catalyst Center Wireless Design Playbook

This playbook provides functionality to manage wireless network design in Cisco Catalyst Center, including SSIDs, interfaces, power profiles, AP profiles, RF profiles, and anchor groups. It simplifies the configuration of wireless networks by automating repetitive tasks and ensuring consistency across deployments.

## Requirements

- **Python**: 3.6 or higher
- **Ansible**: 2.9 or higher
- **Cisco Catalyst Center**: 2.3.7.9 or higher
- **Cisco DNA Ansible Collection**: Installed via `ansible-galaxy collection install cisco.dnac`
- **Python SDK**: Install `dnacentersdk` via `pip install dnacentersdk`



## Installation
### 1. Prepare your Ansible Environment

- Install Ansible if you haven't already.
- Ensure you have network connectivity to your Catalyst Center instance.
-  Clone the project and playbooks:
  ```bash
  git clone git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git


### 2. Configure Host Inventory

Update the host_inventory_dnac1/hosts.yml file with your Catalyst Center details (IP address, credentials, etc.) and ensure the dnac_version in this file matches your actual Catalyst Center version as below:

```bash
---
catalyst_center_hosts:
    hosts:
        catalyst_center220:
            #(Mandatory) CatC Ip address
            catalyst_center_host:  <CatC IP Address>
            #(Mandatory) CatC UI admin Password
            catalyst_center_password: <CatC UI admin Password>
            catalyst_center_port: 443
            catalyst_center_timeout: 60
            #(Mandatory) CatC UI admin username
            catalyst_center_username: <CatC UI admin username> 
            catalyst_center_verify: false
            #(Mandatory) CatC Release version
            catalyst_center_version: <CatC Release version>
            catalyst_center_debug: true
            catalyst_center_log_level: INFO
            catalyst_center_log: true
```
## Usage
The Wireless Design module allows you to configure and manage various aspects of your wireless network through Cisco Catalyst Center. The configuration is structured into several key components:
![Wireless Design UI Page](./images/wireless_design.png)

Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/docs/ 

### SSIDs

SSIDs are the foundation of wireless networks, enabling devices to connect to the network with specific configurations. In Cisco Catalyst Center, SSIDs can be configured for enterprise or guest use cases with detailed security, QoS, and radio settings.


##### Create an Enterprise SSID

This example demonstrates how to configure an enterprise SSID with advanced security and performance settings.

```yaml
wireless_design_details:
  - ssids:
    - ssid_name: "iac_ssid"
      ssid_type: "Enterprise"
      wlan_profile_name: "iac_profile"
      radio_policy:
        radio_bands: [2.4, 5, 6]
        2_dot_4_ghz_band_policy: "802.11-bg"
        band_select: true
        6_ghz_client_steering: true
      fast_lane: false
      quality_of_service:
        egress: SILVER
        ingress: BRONZE-UP
      ssid_state:
        admin_status: true
        broadcast_ssid: true
      l2_security:
        l2_auth_type: "WPA2_WPA3_ENTERPRISE"
        ap_beacon_protection: true
      fast_transition: "ENABLE"
      fast_transition_over_the_ds: true
      wpa_encryption: ["CCMP128", "GCMP128", "CCMP256", "GCMP256"]
      auth_key_management: ["802.1X-SHA2", "FT+802.1x", "SUITE-B-1X", "SUITE-B-192X"]
      cckm_timestamp_tolerance: 2000
      aaa:
        auth_servers_ip_address_list: ["10.195.247.251"]
        accounting_servers_ip_address_list: ["172.23.241.229"]
        aaa_override: true
        mac_filtering: true
        deny_rcm_clients: true
      mfp_client_protection: "OPTIONAL"
      protected_management_frame: "REQUIRED"
      11k_neighbor_list: true
      coverage_hole_detection: true
      wlan_timeouts:
        enable_session_timeout: true
        session_timeout: 3600
        enable_client_execlusion_timeout: true
        client_execlusion_timeout: 1800
      bss_transition_support:
        bss_max_idle_service: true
        bss_idle_client_timeout: 3000
        directed_multicast_service: true
      nas_id: ["AP ETH Mac Address"]
      client_rate_limit: 90000
```

##### Edit Enerprise SSID

To modify an existing enterprise SSID, you can update specific fields such as security, radio policy, or QoS settings. The following example demonstrates how to edit an enterprise SSID:

```yaml
wireless_design_details:
  - ssids:
    - ssid_name: "iac_ssid"
      ssid_type: "Enterprise"
      l2_security:
        l2_auth_type: "OPEN"
      wlan_profile_name: "iac_profile"
      radio_policy:
        radio_bands: [2.4, 5]
        2_dot_4_ghz_band_policy: "802.11-g"
        band_select: true
        6_ghz_client_steering: false
      fast_lane: false
      quality_of_service:
        egress: SILVER
        ingress: BRONZE-UP
      ssid_state:
        admin_status: true
        broadcast_ssid: true
```

##### Configure Guest SSID

Guest SSIDs are designed to provide temporary or restricted access to external users, ensuring secure and controlled connectivity. In Cisco Catalyst Center, guest SSIDs can be configured with specific security, authentication, and access policies to meet organizational requirements.

The following example demonstrates how to configure a guest SSID with WPA2 Enterprise security and web authentication. This configuration ensures secure access for guest users while leveraging centralized authentication and accounting.

```yaml
wireless_design_details:
  - ssids:
    - ssid_name: "iac_guest_ssid"
      ssid_type: "Guest"
      wlan_profile_name: "iac_guest_profile"
      radio_policy:
        radio_bands: [2.4]
        2_dot_4_ghz_band_policy: "802.11-g"
      fast_lane: true
      ssid_state:
        admin_status: true
        broadcast_ssid: true
      l2_security:
        l2_auth_type: "WPA2_ENTERPRISE"
      fast_transition: "ENABLE"
      fast_transition_over_the_ds: true
      wpa_encryption: ["CCMP128"]
      auth_key_management: ["CCKM", "802.1X-SHA1", "802.1X-SHA2", "FT+802.1x"]
      cckm_timestamp_tolerance: 2000
      l3_security:
        l3_auth_type: WEB_AUTH
        auth_server: central_web_authentication
      aaa:
        auth_servers_ip_address_list: ["10.195.247.251"]
        accounting_servers_ip_address_list: ["172.23.241.229"]

```

##### Edit Guest SSID

To modify an existing guest SSID, you can update specific fields such as security or authentication type. The following example demonstrates how to edit a guest SSID to use open authentication for both Layer 2 and Layer 3 security.

```yaml
wireless_design_details:
  - ssids:
    - ssid_name: "iac_guest_ssid"
      ssid_type: "Guest"
      l2_security:
        l2_auth_type: "OPEN"
      l3_security:
        l3_auth_type: "OPEN"
```

##### Delete SSID

To delete an SSID, specify the ssid_name in the playbook in the *deleted* state. This ensures the SSID is removed from the wireless network configuration.

```yaml
wireless_design_details:
  - ssids:
    - ssid_name: "iac_guest_ssid"
    - ssid_name: "iac_ssid"
    - ssid_name: "temporary_employee_ssid"
```

### Interfaces

##### Create interfaces
Interfaces and VLAN groups in Cisco Catalyst Center allow you to define and manage the network segmentation for wireless traffic. By associating interfaces with specific VLANs, you can ensure proper traffic isolation and routing for different types of network users, such as employees, guests, and IoT devices.

The following example demonstrates how to create wireless interfaces and associate them with VLANs. Each interface is mapped to a specific VLAN ID to segment traffic effectively.

```yaml
wireless_design_details:
  - interfaces:
    - interface_name: "data"
      vlan_id: 10
    - interface_name: "voice"
      vlan_id: 11
    - interface_name: "guest_access"
      vlan_id: 12
    - interface_name: "emp_access"
      vlan_id: 13
```

##### Update Wireless Interfaces and VLANs
To modify existing wireless interfaces or update their associated VLANs, specify the updated *interface_name* and *vlan_id* in the playbook. The following example demonstrates how to update the VLAN IDs for the *data* and *voice* interfaces.

```yaml
wireless_design_details:
  - interfaces:
    - interface_name: "data"
      vlan_id: 7
    - interface_name: "voice"
      vlan_id: 8
```

##### Delete Wireless Interfaces

To delete wireless interfaces, specify the interface_name in the playbook in the *deleted* state. This ensures the interface is removed from the wireless network configuration.

```yaml
wireless_design_details:
  - interfaces:
    - interface_name: "data"
    - interface_name: "voice"
    - interface_name: "guest_access"
    - interface_name: "iot_network"
```

### Power Profile

Power profiles in Cisco Catalyst Center allow you to optimize access point (AP) power consumption and performance by configuring specific power settings for different interfaces. These profiles help manage energy efficiency while maintaining network performance.

##### Create Power Profile

The following example demonstrates how to create a power profile named *iac_radio_state*. This profile disables specific radio interfaces (e.g., 6GHz, 5GHz, and Secondary 5GHz) to optimize power usage.

```yaml
wireless_design_details:
  - power_profiles:
      - power_profile_name: "iac_radio_state"
        power_profile_description: "Profile for radio state settings."
        rules:
          - interface_type: "RADIO"
            interface_id: "6GHZ"
            parameter_type: "STATE"
            parameter_value: "DISABLE"
          - interface_type: "RADIO"
            interface_id: "5GHZ"
            parameter_type: "STATE"
            parameter_value: "DISABLE"
          - interface_type: "RADIO"
            interface_id: "SECONDARY_5GHZ"
            parameter_type: "STATE"
            parameter_value: "DISABLE"

```
##### Update Power Profile

To update an existing power profile, modify the desired settings in the playbook. The following example demonstrates how to update the *iac_radio_state* profile to disable the 2.4GHz radio interface.

```yaml
wireless_design_details:
  - power_profiles:
      - power_profile_name: "iac_radio_state"
        power_profile_description: "Updated profile for radio state settings."
        rules:
          - interface_type: "RADIO"
            interface_id: "2_4GHZ"
            parameter_type: "STATE"
            parameter_value: "DISABLE"
```

##### Delete Power Profile

To delete a power profile, specify the profile name in the playbook in the *deleted* state:

```yaml
wireless_design_details:
  - power_profiles:
      - power_profile_name: "iac_radio_state"
      - power_profile_name: "Ethernet State"
        
```

### Access Point (AP) Profile

##### Create access point profile

Configure access point profiles with management, security, and mesh settings.
To create an access point profile, you need to provide at least the profile name.
In the followng example, we create three access point profiles, each with its own set of settings. For instance, in the first example we are simply creating a basic AP profile with EAP-FAST authentication and a username and password for authentication. In the second example we are creating a profile with EAP-FAST authentication, a username and password for authentication, and a mesh configuration. In the third example we are creating a profile with EAP-PEAP authentication, a username and password for authentication, and a mesh configuration as well as power management settings.

```yaml
wireless_design_details:
  - access_point_profiles:
    - access_point_profile_name: "ap_profile_eap_fast"
      management_settings:
        access_point_authentication: "EAP-FAST"
        dot1x_username: "xxxx"
        dot1x_password: "xxxxxxx"

    - access_point_profile_name: "Office AP Profile"
      remote_teleworker: true
      management_settings:
        access_point_authentication: "NO-AUTH"
        ssh_enabled: true
        telnet_enabled: false
        management_username: "xxxx"
        management_password: "xxxxxxx"
        management_enable_password: "xxxxxxx"

    - access_point_profile_name: "Staging-AP"
      access_point_profile_description: "Main office AP profile"
      management_settings:
        access_point_authentication: "EAP-PEAP"
        dot1x_username: "xxxx"
        dot1x_password: "xxxxxxx"
        ssh_enabled: false
        telnet_enabled: false
      security_settings:
        awips: true
        awips_forensic: false
        rogue_detection: true
        minimum_rssi: -71
        transient_interval: 300
        report_interval: 60
        pmf_denial: false
      mesh_enabled: false
      mesh_settings:
        range: 1000
        backhaul_client_access: true
        rap_downlink_backhaul: "2.4 GHz"
        ghz_2_4_backhaul_data_rates: "802.11n"
        bridge_group_name: "Bridge1"
      power_settings:
        ap_power_profile_name: "iac_radio_state"
        calendar_power_profiles:
          - ap_power_profile_name: "Schedule-Mode"
            scheduler_type: "MONTHLY"
            scheduler_dates_list: ["2", "9", "28"]
            scheduler_start_time: "08:00 AM"
            scheduler_end_time: "6:00 PM"
      time_zone: "DELTA FROM CONTROLLER"
      time_zone_offset_hour: -11
      time_zone_offset_minutes: 30
      maximum_client_limit: 900
        
```
##### Update access point profile

We can modify the access point profiles by providing the specific settings we want to update. In the following example, we update the access point power settings to include a calendar-based power profile for a specific period or time range:

```yaml
wireless_design_details:
- access_point_profiles:
  - access_point_profile_name: "Office AP Profile"
    power_settings:
      calendar_power_profiles:
        - ap_power_profile_name: "Low-Power-Mode"
          scheduler_type: "DAILY"
          scheduler_start_time: "1:00 AM"
          scheduler_end_time: "5:00 AM"

```

##### Delete access point profile
To delete an access point profile, you can specify the profile name in the playbook in the *deleted* state.

```yaml
wireless_design_details:
- access_point_profiles:
  - access_point_profile_name: "Office AP Profile"
  - access_point_profile_name: "Staging-AP"
  - access_point_profile_name: "ap_profile_eap_fast"

```

### RF Profile
Optimize radio frequency settings for different bands (2.4GHz, 5GHz, 6GHz).

##### Create RF Profile
The provided RF profile examples demonstrate how to optimize radio frequency settings for different wireless bands (2.4GHz, 5GHz, and 6GHz) in Cisco Catalyst Center. We have provided three examples on how to create these profiles:
The first profile configures the 2.4GHz band with limited channels (1, 6, 11) to reduce interference, inheriting settings from a "HIGH" parent profile. 
The second profile is a mixed configuration for 5GHz and 6GHz bands, with client limits on 5GHz. 
The third profile is an advanced configuration for the 6GHz band, including detailed settings for power levels, data rates, spatial reuse, and multi-BSSID support.

```yaml
wireless_design_details:
  - radio_frequency_profiles:
    - radio_frequency_profile_name: "iac_rf_profile_2_4ghz"
      default_rf_profile: false
      radio_bands: [2.4]

      radio_bands_2_4ghz_settings:
        parent_profile: "HIGH"
        dca_channels_list: [1, 6, 11]

    - radio_frequency_profile_name: "iac_rf_profile_5_6ghz_mixed"
      default_rf_profile: false
      radio_bands: [5, 6]

      radio_bands_5ghz_settings:
        parent_profile: "LOW"
        preamble_puncturing: false
        client_limit: 100

      radio_bands_6ghz_settings:
        parent_profile: "CUSTOM"
        psc_enforcing_enabled: true
        maximum_dbs_channel_width: 160
        discovery_frames_6ghz: "None"

    - radio_frequency_profile_name: "iac_rf_profile_6_ghz"
      default_rf_profile: false
      radio_bands: [6]

      radio_bands_6ghz_settings:
        minimum_dbs_channel_width: 80
        maximum_dbs_channel_width: 160
        preamble_puncturing: true
        psc_enforcing_enabled: true
        dca_channels_list: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129, 133, 137, 141, 145, 149, 153, 157, 161, 165, 169, 173, 177, 181, 185, 189, 193, 197, 201, 205, 209, 213, 217, 221, 225, 229, 233]
        supported_data_rates_list: [12, 18, 24, 36, 48, 54]
        mandatory_data_rates_list: [12, 54]
        minimum_power_level: 10
        maximum_power_level: 30
        rx_sop_threshold: "CUSTOM"
        custom_rx_sop_threshold: -80
        tpc_power_threshold: -60
        coverage_hole_detection:
          minimum_client_level: 5
          data_rssi_threshold: -72
          voice_rssi_threshold: -68
          exception_level: 6
        client_limit: 150
        flexible_radio_assigment:
          client_reset_count: 10
          client_utilization_threshold: 10
        discovery_frames_6ghz: "None"
        broadcast_probe_response_interval: 10
        standard_power_service: false
        multi_bssid:
          dot_11ax_parameters:
            ofdma_downlink: true
            ofdma_uplink: true
            mu_mimo_downlink: true
            mu_mimo_uplink: true
          dot_11be_parameters:
            ofdma_downlink: true
            ofdma_uplink: true
            mu_mimo_downlink: true
            mu_mimo_uplink: true
            ofdma_multi_ru: true
          target_waketime: true
          twt_broadcast_support: true
        spatial_reuse:
          non_srg_obss_pd: true
          non_srg_obss_pd_max_threshold: -63
          srg_obss_pd: true
          srg_obss_pd_min_threshold: -63
          srg_obss_pd_max_threshold: -62

```

##### Update RF Profile
We can update the RF Profile by modifying any of the configurations in the RF Profile section of the playbook. In the following examples, we are updating the RF Profile "iac_rf_profile_2_4ghz" by changing the parent profile and adjusting the power levels.
In the second example, we are updating the RF Profile "iac_rf_profile_5_6ghz_mixed" by modifying the channel width, supported data rates, and mandatory data rates.

```yaml
wireless_design_details:
  - radio_frequency_profiles:
    - radio_frequency_profile_name: "iac_rf_profile_2_4ghz"
      default_rf_profile: false
      radio_bands: [2.4]
      radio_bands_2_4ghz_settings:
        parent_profile: "LOW"
        minimum_power_level: 3
        maximum_power_level: 15

    - radio_frequency_profile_name: "iac_rf_profile_5_6ghz_mixed"
      default_rf_profile: false
      radio_bands: [5]
      radio_bands_5ghz_settings:
        parent_profile: "TYPICAL"
        channel_width: "160"
        dca_channels_list: [36, 40, 44, 48, 52, 56, 60, 64]
        supported_data_rates_list: [12, 24, 36, 48, 6, 18, 9, 54]
        mandatory_data_rates_list: [24]
```

##### Delete RF Profile

To delete any RF profile, you can specify the profile name in the playbook in the *deleted* state.

```yaml
wireless_design_details:
  - radio_frequency_profiles:
    - radio_frequency_profile_name: "iac_rf_profile_2_4ghz"
    - radio_frequency_profile_name: "iac_rf_profile_5_6ghz_mixed"

```

### Anchor Groups
Anchor groups in Cisco Catalyst Center allow you to define mobility anchors for seamless roaming across wireless networks. Mobility anchors are controllers that handle traffic for specific SSIDs, enabling secure and efficient client mobility between different network segments or sites.

##### Add Anchor Group and Mobility Anchor
The following example demonstrates how to add an anchor group and its associated mobility anchors. We can specify the anchor group name and the details of each mobility anchor in the playbook. In this example, we are adding an anchor group named *Enterprise_Anchor_Group* with two mobility anchors.

```yaml
wireless_design_details:
  - anchor_groups:
    - anchor_group_name: "Enterprise_Anchor_Group"
      mobility_anchors:
        - device_name: "WLC_Enterprise_1"
          device_ip_address: "192.168.0.10"
          device_mac_address: '00:1A:2B:3C:4D:5E'
          device_type: "IOS-XE"
          device_priority: 1
          device_nat_ip_address: "10.0.0.10"
          mobility_group_name: Enterprise_Mobility_Group
          managed_device: false
        - device_name: "WLC_Enterprise_2"
          device_ip_address: "192.168.0.11"
          device_mac_address: '00:1A:2B:3C:4D:5F'
          device_type: "AIREOS"
          device_priority: 2
          device_nat_ip_address: "10.0.0.11"
          mobility_group_name: "Enterprise_Mobility_Group"
          managed_device: false
```

##### Update Anchor Group

To update an existing anchor group, modify the mobility anchors associated with the group. You can add new mobility anchors, update existing ones, or change their configurations. The following example demonstrates how to update the "Enterprise_Anchor_Group" by updating existing anchors, adding new mobility anchors and modifying their details.

```yaml
wireless_design_details:
  - anchor_groups:
    - anchor_group_name: "Enterprise_Anchor_Group"
      mobility_anchors:
        - device_name: "WLC_Enterprise_1"
          device_ip_address: "192.168.0.11"
          device_mac_address: '00:1A:2B:3C:4D:5F'
          device_type: "AIREOS"
          device_priority: 2
          device_nat_ip_address: "10.0.0.11"
          mobility_group_name: "Enterprise_Mobility_Group"
          managed_device: false
        - device_name: "WLC_Enterprise_10"
          device_ip_address: "192.168.0.110"
          device_mac_address: "AA:1A:2B:3C:4D:5E"
          device_type: "IOS-XE"
          device_priority: 1
          device_nat_ip_address: "10.0.0.10"
          mobility_group_name: "Enterprise_Mobility_Group"
          managed_device: false
        - device_name: "WLC_Enterprise_20"
          device_ip_address: "192.168.0.111"
          device_mac_address: "AA:1A:2B:3C:4D:5E"
          device_type: "AIREOS"
          device_priority: 2
          mobility_group_name: "Enterprise_Mobility_Group"
          managed_device: false

```

##### Delete Anchor Group

To delete any anchor groups, you can specify the anchor groups to be deleted in the playbook in the *deleted* state. If you want to delete the "Enterprise_Anchor_Group", you can specify it in the playbook as follows: 

```yaml
wireless_design_details:
  - anchor_groups:
    - anchor_group_name: "Enterprise_Anchor_Group"

```


#### Using the Jinja Template for Bulk Operations

The Jinja template in the wireless design playbook is designed to dynamically generate bulk configurations for SSIDs, interfaces, power profiles, RF profiles, and anchor groups, enabling automation of large-scale deployments or testing scenarios. By leveraging Jinja loops and conditionals, it simplifies the creation of multiple configurations with consistent settings, such as alternating SSID types (Enterprise and Guest), VLAN assignments for interfaces, radio frequency optimizations, and mobility anchor setups. This approach ensures scalability, flexibility, and efficiency in managing wireless network designs.

#### Example Jinja Template

Below is an example of how the Jinja template is structured to generate bulk configurations for wireless design:

```bash
wireless_design_details:
  # Example SSIDs
  - ssids:
    {% for i in range(1, 4) %}
    - ssid_name: "example_ssid_{{ i }}"
      ssid_type: "{{ 'Enterprise' if i % 2 == 0 else 'Guest' }}"
      wlan_profile_name: "example_profile_{{ i }}"
      radio_policy:
        radio_bands: [2.4, 5, 6]
        2_dot_4_ghz_band_policy: "802.11-bg"
        band_select: true
        6_ghz_client_steering: {{ 'true' if i % 2 == 0 else 'false' }}
      fast_lane: {{ 'true' if i % 2 == 0 else 'false' }}
      ssid_state:
        admin_status: true
        broadcast_ssid: true
      l2_security:
        l2_auth_type: "{{ 'WPA2_ENTERPRISE' if i % 2 == 0 else 'OPEN' }}"
      l3_security:
        l3_auth_type: "{{ 'WEB_AUTH' if i % 2 == 0 else 'OPEN' }}"
      fast_transition: "ENABLE"
    {% endfor %}

  # Example Interfaces
  - interfaces:
    {% for i in range(1, 4) %}
    - interface_name: "example_interface_{{ i }}"
      vlan_id: {{ 10 + i }}
    {% endfor %}

  # Example Power Profiles
  - power_profiles:
    {% for i in range(1, 3) %}
    - power_profile_name: "example_power_profile_{{ i }}"
      power_profile_description: "Power profile example {{ i }}"
      rules:
        - interface_type: "RADIO"
          interface_id: "{{ '6GHZ' if i == 1 else '5GHZ' }}"
          parameter_type: "STATE"
          parameter_value: "DISABLE"
        - interface_type: "RADIO"
          interface_id: "2_4GHZ"
          parameter_type: "STATE"
          parameter_value: "ENABLE"
    {% endfor %}

  # Example Access Point Profiles
  - access_point_profiles:
    {% for i in range(1, 4) %}
    - access_point_profile_name: "example_ap_profile_{{ i }}"
      {% if i == 2 %}
      access_point_profile_description: "Description for AP profile {{ i }}"
      remote_teleworker: true
      {% endif %}
      {% if i == 3 %}
      management_settings:
        access_point_authentication: "EAP-TLS"
        ssh_enabled: true
        telnet_enabled: false
        management_username: "admin"
        management_password: "securePass"
        management_enable_password: "enablePass"
      {% endif %}
    {% endfor %}

  # Example RF Profiles
  - radio_frequency_profiles:
    {% for i in range(1, 3) %}
    - radio_frequency_profile_name: "example_rf_profile_{{ i }}"
      default_rf_profile: {{ 'true' if i == 1 else 'false' }}
      radio_bands: [2.4, 5, 6]
      {% if i == 1 %}
      radio_bands_2_4ghz_settings:
        parent_profile: "HIGH"
        dca_channels_list: [1, 6, 11]
      {% else %}
      radio_bands_5ghz_settings:
        parent_profile: "TYPICAL"
        channel_width: "80"
        dca_channels_list: [36, 40, 44, 48]
      {% endif %}
    {% endfor %}

  # Example Anchor Groups
  - anchor_groups:
    {% for i in range(1, 3) %}
    - anchor_group_name: "example_anchor_group_{{ i }}"
      mobility_anchors:
        - device_name: "WLC_Example_{{ i }}"
          device_ip_address: "192.168.0.{{ 10 + i }}"
          device_mac_address: "00:1A:2B:3C:4D:{{ 5 + i }}"
          device_type: "{{ 'IOS-XE' if i == 1 else 'AIREOS' }}"
          device_priority: {{ i }}
          device_nat_ip_address: "10.0.0.{{ 10 + i }}"
          mobility_group_name: "Example_Mobility_Group"
          managed_device: false
    {% endfor %}
```

The Jinja template example for dynamically generating bulk configurations for wireless design can be found in the *jinja_template* folder under the *wireless_design directory*. You can refer to this template as a starting point and modify it to suit your specific network configurations and requirements.

### 3. Validate the playbook

To ensure a successful execution of the playbooks with your specified inputs, follow these steps:

Input Validation:
Before executing the playbook, it is essential to validate the input schema. This step ensures that all required parameters are included and correctly formatted. Run the following command *./tools/validate.sh -s* to perform the validation providing the schema path -d and the input path.

```bash

     ./tools/validate.sh -s /Users/majlona/Desktop/dnac_ansible_workflows_vs_copilot/workflows/wireless_design/schema/wireless_design_schema.yml -d /Users/majlona/Desktop/dnac_ansible_workflows_vs_copilot/workflows/wireless_design/vars/wireless_design_inputs.yml
```

### 4. Running the Playbook

Once the input validation is complete and no errors are found, you can run the playbook. Provide your input file path using the --e variable as VARS_FILE_PATH:

```bash

     ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/wireless_design/playbook/wireless_design_playbook.yml --e VARS_FILE_PATH=/Users/majlona/Desktop/dnac_ansible_workflows_vs_copilot/workflows/wireless_design/vars/wireless_design_inputs.yml -vvv
```

If there is an error in the input or an issue with the API call during execution, the playbook will halt and display the relevant error details.

##### Using the Jinja Template for Bulk Operations

The Jinja Template allows you to create bulk configurations for wireless design, simplifying the process of generating multiple configurations. To use the Jinja Template, modify and run the playbook with the following command:

```bash
      ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/wireless_design/playbook/wireless_design_playbook.yml --extra-vars VARS_FILE_PATH=/Users/majlona/Desktop/dnac_ansible_workflows_vs_copilot/workflows/wireless_design/vars/jinja_wireless_design_inputs.yml -vvvv
```

Post-Execution Verification:
After executing the playbook, check the Catalyst Center UI to verify wireless design. If *debug_log* is enabled, you can also review the logs for detailed information on operations performed and any updates made.

### 5. References

*Note: The environment used for the references in the above instructions is as follows:*

```yaml
python: 3.12.0
dnac_version: 2.3.7.9
ansible: 9.9.0
dnacentersdk: 2.8.8
```
