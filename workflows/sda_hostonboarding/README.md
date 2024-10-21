# SDA Host Onboarding Workflow Manager
This Ansible workflow playbook manages host onboarding operations within a Cisco SD-Access fabric through the Cisco DNA Center. It provides the ability to add, update, and delete port assignments and port channels for network devices, enabling seamless automation of host onboarding workflows on single or bulk interfaces on a single or a number of access devices.
### Minimum Catalyst Cennter Version Supported : 2.3.7.6

# Playbook Use Cases
This Playbook can be used to automate various host onboarding tasks, including:
1. Adding a group of hosts or different types of host on one or more edge devices.
2. Updating host port assignment: Move a host to a different port or port channel.
3. Deleting host port assignment: Remove a host's port assignment, effectively disconnecting it from the network.
4. Creating and managing port channels: Configure port channels for link aggregation and redundancy.
5. Onboard hosts on link aggregation (port Channels)
6. Delete ALL port assignments and port channels for the fabric device using ip_address
7. Remove provided hosts from interfaces and port channels.

## Playbook parameters spec
https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/sda_host_port_onboarding_workflow_manager/

# Examples:
## Add port interfaces and port channels for a specific fabric device
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
sda_host_onboarding_details:
    - ip_address: "204.1.2.2"
        port_assignment_details:
            - interface_name: "FortyGigabitEthernet1/1/1"
            connected_device_type: "TRUNKING_DEVICE"

            - interface_name: "FortyGigabitEthernet1/1/2"
            connected_device_type: "TRUNKING_DEVICE"
            authentication_template_name: "No Authentication"
            interface_description: "Trunk Port"

            - interface_name: "FortyGigabitEthernet2/1/1"
            connected_device_type: "ACCESS_POINT"
            data_vlan_name: "AG_23"

            - interface_name: "FortyGigabitEthernet2/1/2"
            connected_device_type: "ACCESS_POINT"
            data_vlan_name: "AG_23"
            authentication_template_name: "No Authentication"
            interface_description: "Access Point Port"

            - interface_name: "GigabitEthernet1/1/1"
            connected_device_type: "ACCESS_POINT"
            data_vlan_name: "AG_23"
            authentication_template_name: "Open Authentication"
            interface_description: "Access Point Port"

            - interface_name: "GigabitEthernet1/1/2"
            connected_device_type: "ACCESS_POINT"
            data_vlan_name: "AG_23"
            authentication_template_name: "Closed Authentication"
            interface_description: "Access Point Port"

            - interface_name: "GigabitEthernet1/1/4"
            connected_device_type: "USER_DEVICE"
            data_vlan_name: "AG_VLAN_23"

            - interface_name: "GigabitEthernet2/1/1"
            connected_device_type: "USER_DEVICE"
            voice_vlan_name: "VOICE_VLAN_23"

            - interface_name: "GigabitEthernet2/1/2"
            connected_device_type: "USER_DEVICE"
            data_vlan_name: "AG_23"
            voice_vlan_name: "VOICE_VLAN_23"

            - interface_name: "GigabitEthernet2/1/3"
            connected_device_type: "USER_DEVICE"
            data_vlan_name: "AG_23"
            voice_vlan_name: "VOICE_VLAN_23"
            security_group_name: "Guests"

            - interface_name: "GigabitEthernet2/1/4"
            connected_device_type: "USER_DEVICE"
            data_vlan_name: "AG_23"
            voice_vlan_name: "VOICE_VLAN_23"
            security_group_name: "Guests"
            authentication_template_name: "No Authentication"

            - interface_name: "GigabitEthernet2/1/4"
            connected_device_type: "USER_DEVICE"
            data_vlan_name: "AG_23"
            security_group_name: "Guests"
            authentication_template_name: "Closed Authentication"

            - interface_name: "GigabitEthernet2/1/4"
            connected_device_type: "USER_DEVICE"
            voice_vlan_name: "VOICE_VLAN_23"
            authentication_template_name: "Low Impact"
            interface_description: "User Device"

        port_channel_details:
            - interface_names: ["TenGigabitEthernet1/0/37", "TenGigabitEthernet1/0/38", "TenGigabitEthernet1/0/39"]
            connected_device_type: "TRUNK"

            - interface_names: ["TenGigabitEthernet1/0/43", "TenGigabitEthernet1/0/44"]
            connected_device_type: "TRUNK"
            protocol: "ON"

            - interface_names: ["TenGigabitEthernet1/0/45", "TenGigabitEthernet1/0/46", "TenGigabitEthernet1/0/47", "TenGigabitEthernet1/0/48"]
            connected_device_type: "TRUNK"
            protocol: "LACP"

            - interface_names: ["TenGigabitEthernet1/1/2", "TenGigabitEthernet1/1/3", "TenGigabitEthernet1/1/4"]
            connected_device_type: "TRUNK"
            protocol: "PAGP"
            port_channel_descrption: "Trunk port channel"

            - interface_names: ["TenGigabitEthernet1/1/5", "TenGigabitEthernet1/1/6"]
            connected_device_type: "EXTENDED_NODE"

            - interface_names: ["TenGigabitEthernet1/1/7", "TenGigabitEthernet1/1/8"]
            connected_device_type: "EXTENDED_NODE"
            protocol: "PAGP"
            port_channel_descrption: "extended node port channel"
```

## Update port interfaces and port channels for a specific fabric device
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
sda_host_onboarding_details:
    - hostname: "DC-T-9300.cisco.local"
    port_assignment_details:
        - interface_name: "FortyGigabitEthernet1/1/1"
        connected_device_type: "TRUNKING_DEVICE"
        interface_description: "Trunking device on port 111"

        - interface_name: "GigabitEthernet2/1/4"
        connected_device_type: "USER_DEVICE"
        data_vlan_name: "AG_VLAN_23"
        security_group_name: "Guests"
        authentication_template_name: "Closed Authentication"

        - interface_name: "GigabitEthernet2/1/4"
        connected_device_type: "USER_DEVICE"
        data_vlan_name: "AG_23"
        security_group_name: "Guests"
        authentication_template_name: "Closed Authentication"
        interface_description: "User device at port 214"

    port_channel_details:
        - interface_names: ["TenGigabitEthernet1/1/2", "TenGigabitEthernet1/1/3", "TenGigabitEthernet1/1/4"]
        connected_device_type: "EXTENDED_NODE"
        protocol: 'PAGP'
        port_channel_descrption: "Trunk port channel"
```
## Delete ALL port assignments and port channels for the fabric device using hostname
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
sda_host_onboarding_details:
    - ip_address: "204.1.2.2"
    - hostname: "DC-T-9300.cisco.local"
```

## Delete specific interfaces and port channels using interface names and port channel name
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
sda_host_onboarding_details:
    - ip_address: "204.1.2.2"
    port_assignment_details:
        - interface_name: "FortyGigabitEthernet2/1/2"
        data_vlan_name: "AG_23"

        - interface_name: "GigabitEthernet2/1/3"
        voice_vlan_name: "VOICE_VLAN_23"

    port_channel_details:
        - port_channel_name: "Port-channel2"
        connected_device_type: "TRUNK"

        - port_channel_name: "Port-channel6"
        connected_device_type: "EXTENDED_NODE"
```
# How to execute playbook:

# Procedure
1. ## Prepare your Ansible environment:

Install Ansible if you haven't already
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

2. ## Configure Host Inventory:

The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
##The Sample host_inventory_dnac1/hosts.yml

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
## Validate the playbooks with schema
```bash
    (pyats) pawansi@PAWANSI-M-81A3 sda_hostonboarding % yamale -s schema/sda_host_onboarding_schema.yml vars/                             
    Finding yaml files...
    Found 2 yaml files.
    Validating...
    Validation success! 👍
```

## Running playbook
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml  workflows/sda_hostonboarding/playbook/sda_host_onboarding_playbook.yml --e VARS_FILE_PATH=../vars/sda_host_onboarding_input.yml -vvvv
```


