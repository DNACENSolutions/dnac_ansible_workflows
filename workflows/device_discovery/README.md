# Catalyst Center Device Discovery Playbook

## Discovery Overview

The Discovery feature in Catalyst Center scans your network to identify devices and add them to the inventory. It can also work with the Device Controllability feature to configure necessary network settings on discovered devices.

## Discovery Methods

You have four options for discovering devices:

* **Cisco Discovery Protocol (CDP):** Provide a seed IP address and Catalyst Center will use CDP to discover neighboring devices.
* **IP Address Range:** Specify a range of IP addresses to scan. (Maximum range: 4096 devices)
* **Link Layer Discovery Protocol (LLDP):** Similar to CDP, provide a seed IP address for LLDP-based discovery.
* **Classless Inter-Domain Routing (CIDR):** Provide a seed IP address and a CIDR notation to define the network range to scan.

## Optimizing Discovery Time

Consider these settings to speed up the discovery process:

* **CDP/LLDP Level:** When using CDP or LLDP, set the level to limit the number of hops from the seed device. Lower levels reduce discovery time on large networks.
* **Prefix Length (CIDR):** When using CIDR, adjust the prefix length (between 20 and 30) to control the size of the scanned network.
* **Subnet Filters (IP Range):** Exclude specific IP subnets from the scan when using an IP address range.
* **Preferred Management IP:** Choose whether to add all discovered IP addresses or only the loopback address to Catalyst Center.

## Prerequisites

* **Network Access:** Ensure Catalyst Center has appropriate network access to reach the devices you want to discover.
* **Device Support:** Verify that your devices support the chosen discovery protocol (CDP or LLDP).
* **Credentials:** If Device Controllability is enabled, ensure Catalyst Center has the correct credentials to access and configure discovered devices.
* **Catalyst Center Configuration:**
    * Regardless of the method used, you must be able to reach the device from Catalyst Center.
    * Configure specific credentials and protocols in Catalyst Center user device_credentials workflow.

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
## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring discovery parameters and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.

