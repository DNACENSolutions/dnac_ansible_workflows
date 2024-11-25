
# SDA Fabric Virtual Networks Automation and onboarding anycast gaetways on fabric sites
This Ansible playbooks to automate the configuration of Fabric VLANs, Virtual Networks, and Anycast Gateways within a Cisco SD-Access fabric using the Cisco DNA Center.

# Requirements:
  - Cisco Catalyst Center (DNAC) version: 2.3.7.6 (minimum version)
  - DnacenterSDK 2.9.4 (minimum version)
  - Ansible 2.9.10 (minimum version)
  - Python 3.10.0 (minimum version)

## Playbook: 
sda_virtual_networks_l2_l3_gateways_playbook.yml
This playbook utilizes the cisco.dnac.sda_fabric_virtual_networks_workflow_manager Ansible module to manage various aspects of SD-Access virtual networks 
### including:
Fabric VLANs: Create, update, and delete Layer 2 Fabric VLANs.
Virtual Networks: Create, update, and delete Layer 3 Virtual Networks.
Anycast Gateways: Create, update, and delete Anycast Gateways for providing Layer 3 connectivity within the SD-Access fabric.



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
(pyats) pawansi@PAWANSI-M-81A3 dnac_ansible_workflows % yamale -s workflows/sda_virtual_networks_l2l3_gateways/schema/sda_virtual_networks_l2_l3_gateways_schema.yml workflows/sda_virtual_networks_l2l3_gateways/vars
Finding yaml files...
Found 2 yaml files.
Validating...
Validation success! 👍
```

## Running playbook
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml  workflows/sda_virtual_networks_l2l3_gateways/playbook/sda_virtual_networks_l2_l3_gateways_playbook.yml --e VARS_FILE_PATH=../vars/sda_virtual_networks_l2_l3_gateways_input.yml -vvvv
```