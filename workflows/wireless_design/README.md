# Cisco Catalyst Center Wireless Design

This Playbooks collection provides functionality to manage wireless network design in Cisco Catalyst Center, including SSIDs, interfaces, power profiles, AP profiles, RF profiles, and anchor groups.

## Requirements

- Python 3.6 or higher
- Ansible 2.9 or higher
- Cisco Catalyst Center 2.3.7.9 or higher

## Installation
### 1. Prepare your Ansible environment.

- install Ansible if you haven't already
- Ensure you have network connectivity to your Catalyst Center instance.
- Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git.

### 2. Configure Host Inventory.
- The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
- Make sure the dnac_version in this file matches your actual Catalyst Center version.
- The Sample host_inventory_dnac1/hosts.yml

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

### SSIDs
Configure enterprise and guest wireless networks with detailed security, QoS, and radio settings.

### Interfaces
Define network interfaces and their associated VLANs.

### Power Profiles
Create custom power profiles to optimize AP power consumption and performance.

### AP Profiles
Configure access point profiles with management, security, and mesh settings.

### RF Profiles
Optimize radio frequency settings for different bands (2.4GHz, 5GHz, 6GHz).

### Anchor Groups
Define anchor groups and their associated mobility anchors for seamless roaming.

## Examples
### Configure Enterprise SSID Input Example

```yaml
#Configure Enterprise SSID Input Example
wireless_design_details:
  - ssids:
    - ssid_name: "Enterprise-SSID"
      ssid_type: "Enterprise"
      radio_policy:
        radio_bands: [2.4, 5]
        band_select: true
      ssid_state:
        admin_status: true
        broadcast_ssid: true
      l2_security:
        l2_auth_type: "WPA2_ENTERPRISE"
        protected_management_frame: "REQUIRED"
        auth_key_management: ["802.1X-SHA2"]
        wpa_encryption: ["CCMP128"]
      aaa:
        auth_servers_ip_address_list: ["10.1.1.1"]
        accounting_servers_ip_address_list: ["10.1.1.2"]
        aaa_override: true
```

### Configure Guest SSID
```yaml
#Configure Guest SSID Input Example
wireless_design_details:
  - ssids:
    - ssid_name: "Guest-SSID"
      ssid_type: "Guest"
      radio_policy:
        radio_bands: [2.4, 5]
      ssid_state:
        admin_status: true
        broadcast_ssid: true
      l2_security:
        l2_auth_type: "OPEN"
      l3_security:
        l3_auth_type: "WEB_AUTH"
        auth_server: "web_authentication_external"
        web_auth_url: "https://guest.example.com"
```
### Configure Interface
```yaml
#Configure Interface Input Example
wireless_design_details:
  - interfaces:
    - interface_name: "Enterprise-VLAN"
        vlan_id: 100
```
### Configure VLAN