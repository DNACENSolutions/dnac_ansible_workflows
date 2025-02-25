# Catalyst Center Device Discovery Playbook

## Overview

The Discovery feature is designed to help you identify and manage devices within your network. By scanning your network, it creates an inventory of all discovered devices, making it easier to monitor and configure them. This feature also works alongside the Device Controllability feature to apply necessary network settings to devices that may not have them.

## How to Use the Discovery Feature

### Prerequisites for Discovery

Before running the Discovery feature, ensure you have:
- Configured at least one **SNMP credential** on your devices.
- Set up **SSH credentials** to allow Catalyst Center to manage devices.

* **Network Access:** Ensure Catalyst Center has appropriate network access to reach the devices you want to discover.
* **Device Support:** Verify that your devices support the chosen discovery protocol (CDP or LLDP).
* **Credentials:** If Device Controllability is enabled, ensure Catalyst Center has the correct credentials to access and configure discovered devices.. please refer to Credential module
* **Catalyst Center Configuration:**
    * Regardless of the method used, you must be able to reach the device from Catalyst Center.
    * Configure specific credentials and protocols in Catalyst Center user device_credentials workflow.

### Configure Environment

```bash
catalyst_center_hosts:
    hosts:
        catalyst_center220:
            dnac_host: xx.xx.xx.xx.
            dnac_password: XXXXXXXX
            dnac_port: 443
            dnac_timeout: 60
            dnac_username: admin
            dnac_verify: false
            dnac_version: 2.3.7.6
            dnac_debug: true
            dnac_log_level: INFO
            dnac_log: true
```

### Full Workflow Specification: 
Refer to the official documentation for detailed information on defining workflows: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/discovery_workflow_manager

### Setting Up Discovery Credentials

You will need to configure various types of credentials based on the devices you want to discover:

- **Network Devices**: Use CLI and SNMP credentials.
- **Compute Devices**: Use CLI, SNMP, and HTTP(S) credentials.

You can save commonly used credentials in Catalyst Center for easier access across multiple discovery jobs.

### Performing the Discovery

- When you perform the discovery, ensure:
  - Only ping-reachable devices are included in the list for IP address range discovery.
  - Devices that respond to CDP, CIDR, and LLDP protocols will be included even if they are ping-unreachable.
  - Your SNMP read-only community string is correctly configured, as it is necessary for discovery.

### Tips for Successful Discovery

- Use the device's loopback IP address for management if reachable.
- If you only want to discover new devices, select the option to discover new devices only to avoid updating existing device information.

## Undestanding Discover task

### Task: Discovery single device

This task initiates the discovery of single device IP address using the `cisco.dnac.discovery_workflow_manager` Ansible module. It allows you to specify single device and a Netconf port for device discovery.

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery** action in the Cisco Catalyst Center UI
![Alt text](./images/discovery_2.png)

#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
  single:
    - ip_address_list:
      - 204.101.16.1
      devices_list: []
      discovery_type: SINGLE
      protocol_order: ssh
      discovery_name: Single IP Discovery11
      discovery_specific_credentials:
        cli_credentials_list:
            - username: wlcaccess
              password: Lablab#123
              enable_password: Cisco#123
            - username: cisco
              password: Cisco#123
              enable_password: Cisco#123
        http_read_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        http_write_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        snmp_v2_read_credential:
            description: snmpV2 Sample 1
            community: public
        snmp_v2_write_credential:
            description: snmpV2 Sample 1
            community: public
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
    - ip_address_list:
      - 204.101.16.2
      devices_list: []
      discovery_type: SINGLE
      protocol_order: ssh
      discovery_name: Single IP Discovery11
      discovery_specific_credentials:
        cli_credentials_list:
            - username: wlcaccess
              password: Lablab#123
              enable_password: Cisco#123
            - username: cisco
              password: Cisco#123
              enable_password: Cisco#123
        http_read_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        http_write_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        snmp_v3_credential:
            description: snmpv3Credentials
            username: wlcaccess
            snmp_mode: AUTHPRIV
            auth_password: Lablab#123
            auth_type: SHA
            privacy_type: AES128
            privacy_password: Lablab#123
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
```

### Task: Discovery IP Address Range

This task initiates the discovery of multiple devices of IP address ranges using the `cisco.dnac.discovery_workflow_manager` Ansible module. It allows you to specify single device and a Netconf port for device discovery.

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery** action in the Cisco Catalyst Center UI
![Alt text](./images/discovery_3.png)

#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
  range:
    - ip_address_list:
      - 204.101.16.2-204.101.16.20
      discovery_type: RANGE
      protocol_order: ssh
      discovery_name: Range IP Discovery11
      discovery_specific_credentials:
        cli_credentials_list:
            - username: wlcaccess
              password: Lablab#123
              enable_password: Cisco#123
            - username: cisco
              password: Cisco#123
              enable_password: Cisco#123
        http_read_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        http_write_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        snmp_v3_credential:
            description: snmpV3 Sample 1
            username: wlcaccess
            snmp_mode: AUTHPRIV
            auth_password: Lablab#123
            auth_type: SHA
            privacy_type: AES128
            privacy_password: Lablab#123
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
```

### Task: Discovery Multiple IP Address Ranges

This task initiates the discovery of multiple devices across various IP address ranges using the `cisco.dnac.discovery_workflow_manager` Ansible module. It allows you to specify multiple IP address ranges and a Netconf port for device discovery.

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery > Discovery Type: IP Address Range** action in the Cisco Catalyst Center UI, specifically focusing on the **Multi Range** discovery type.
![Alt text](./images/discovery_4.png)

#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
  multi_range:
    - ip_address_list:
      - 204.101.16.2-204.101.16.3
      - 204.101.16.4-204.101.16.4
      discovery_type: MULTI RANGE
      protocol_order: ssh
      discovery_name: Multi Range Discovery 11
      discovery_specific_credentials:
        cli_credentials_list:
            - username: wlcaccess
              password: Lablab#123
              enable_password: Cisco#123
            - username: cisco
              password: Cisco#123
              enable_password: Cisco#123
        http_read_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        http_write_credential:
            username: wlcaccess
            password: Lablab#123
            port: 443
            secure: true
        snmp_v3_credential:
            description: snmpV3 Sample 1
            username: wlcaccess
            snmp_mode: AUTHPRIV
            auth_password: Lablab#123
            auth_type: SHA
            privacy_type: AES128
            privacy_password: Lablab#123
      timeout: 30
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2

```

### Task: Discovery Devices from a CDP Seed

This task leverages the Cisco Discovery Protocol (CDP) to discover neighboring devices connected to a specified seed device. It utilizes the `cisco.dnac.discovery_workflow_manager` Ansible module to automate this process within Cisco Catalyst Center.

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery > Discovery Type: CDP** action in the Cisco Catalyst Center UI.
![Alt text](./images/discovery_5.png)
#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
    - ip_address_list:
      - 204.101.16.1
      devices_list: []
      discovery_type: CDP
      protocol_order: ssh
      discovery_name: CDP Based Discovery1
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
```

### Task: Discovery Devices from LLDP

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery** action in the Cisco Catalyst Center UI.
![Alt text](./images/discovery_6.png)
#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
    - ip_address_list:
      - 204.101.16.1
      discovery_type: LLDP
      protocol_order: ssh
      discovery_name: LLDP Discovery
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
```

### Task: Discovery Devices from CIDR

#### Mapping Config to UI Actions

The `config` parameter within this task corresponds to the **Tools > Discovery** action in the Cisco Catalyst Center UI.
![Alt text](./images/discovery_7.png)
#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
discovery_details:
    - ip_address_list:
      - 204.101.16.1/24
      discovery_type: CIDR
      protocol_order: ssh
      discovery_name: CIDR Discovery
      discovery_specific_credentials:
        net_conf_port: "830"
      retry: 2
```


### Task: Delete Discovery by Name

This task facilitates the removal of a specific discovery task from Cisco Catalyst Center based on its name. It utilizes the `cisco.dnac.discovery_workflow_manager` Ansible module with the state parameter set to 'deleted'.

#### Mapping to UI Action

The action performed by this task corresponds to selecting a specific discovery task in the Cisco Catalyst Center UI under **"Discovery"** and then choosing the **"Delete"** option.
![Alt text](./images/delete_discovery.png)


#### YAML Structure and Parameter Explanation

```yaml
catalyst_center_version: 2.3.7.6
delete_discovery:
  by_name:
    - discovery_name: "Multi Range Discovery"
```
### Task: Delete All Discovery

This task enables the removal of all existing discovery tasks within Cisco Catalyst Center. It leverages the `cisco.dnac.discovery_workflow_manager` Ansible module, setting the state to 'deleted' and utilizing the `delete_all` parameter.

#### Mapping to UI Action

While there's no direct equivalent in the UI to delete all discoveries at once, this task essentially automates the process of selecting each discovery task individually and deleting them.

#### YAML Structure and Parameter Explanation

```yaml
delete_discovery:
  all:
    - delete_all: True
```

## Running the Playbook

1. **Validate Your Input:**

```bash
   yamale -s workflows/device_discovery/schema/device_discovery_schema.yml workflows/device_discovery/vars/device_discovery_vars.yml
```
2. **Execute the Playbook**

###  To initiate device discovery:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_discovery/playbook/device_discovery_playbook.yml --e VARS_FILE_PATH=../vars/device_discovery_vars.yml
```
###  To delete existing discoveries:
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_discovery/playbook/delete_device_discovery.yml --e VARS_FILE_PATH=../vars/device_discovery_vars.yml
```

## Referances

```yaml
  ansible: 9.9.0
  ansible-core: 2.16.10
  ansible-runner: 2.4.0

  dnacentersdk: 2.8.3
  cisco.dnac: 6.29.0
  ansible.utils: 5.1.2
```

## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring discovery parameters and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.

