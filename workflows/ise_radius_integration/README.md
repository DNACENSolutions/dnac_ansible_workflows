# ISE and AAA Integration Workflow Playbook
Workflow Playbook for Assigning devices to sites network complianceing, Re-network complianceing and Deleteing the devices in Inventory. 
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

network_compliance_details  defines the list of devices and devices details for the devices to be run rough the playbooks


To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/network compliance_workflow_manager/


To run this workflow, you follow the README.md 

#Example run:
## Configure or Update Authentication and Policy Servers
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/ise_radius_integration/playbook/ise_radius_integration_workflow_playbook.yml --e VARS_FILE_PATH=../vars/ise_radius_integration_workflow_input.yml -vvvv

## Delete Authentication and Policy Servers
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/ise_radius_integration/playbook/delete_ise_radius_integration_workflow_playbook.yml --e VARS_FILE_PATH=../vars/ise_radius_integration_workflow_input.yml -vvvv

## Authentication and Policy Server with Jinja Template and passwords from Ansible Vault.
### Jinja Template file: ise_radius_inegration_jinja_template.j2
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
ise_radius_integration_details:
    - authentication_policy_server:
      - server_type: AAA
        server_ip_address: 10.0.0.1
        shared_secret: {{ aaa_shared_secret }}
        protocol: RADIUS_TACACS
        authentication_port: 1812
        accounting_port: 1813
        retries: 3
        timeout: 4
        role: secondary
      - server_type: ISE
        server_ip_address: 10.195.243.31
        shared_secret: {{ ise_shared_secret }}
        protocol: RADIUS_TACACS
        #encryption_scheme: KEYWRAP
        #encryption_key: {{ ise_encryption_key }}"
        #message_authenticator_code_key: {{ ise_message_authenticator_code_key }}
        authentication_port: 1812
        accounting_port: 1813
        retries: 3
        timeout: 4
        role: primary
        use_dnac_cert_for_pxgrid: False
        pxgrid_enabled: True
        cisco_ise_dtos:
        - user_name: admin
          password: {{ ise_admin_password }}
          fqdn: IBSTE-ISE1.cisco.com
          ip_address: 10.195.243.31
          description: Cisco ISE
        trusted_server: True
        ise_integration_wait_time: 20
```
### Jinja file selection


### Eecution of playbook with jinja inputs
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/ise_radius_integration/playbook/ise_radius_integration_workflow_playbook.yml --e VARS_FILE_PATH=../vars/ise_radius_integration_workflow_jinja_input.yml -vvv

### Deletion with Jinja Template
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/ise_radius_integration/playbook/ise_radius_integration_workflow_playbook.yml --e VARS_FILE_PATH=../vars/ise_radius_integration_workflow_jinja_input.yml -vvv



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
User Inputs for Users and roles are stored in  workflows/network compliance/vars/network_compliance_workflow_inputs.yml

##Validate user input before running though ansible
```bash
(pyats) pawansi@PAWANSI-M-81A3 dnac_ansible_workflows % ./tools/validate.sh -s workflows/ise_radius_integration/schema/ise_radius_integration_workflow_schema.yml -d workflows/ise_radius_integration/vars/ise_radius_integration_workflow_input.yml 
workflows/ise_radius_integration/schema/ise_radius_integration_workflow_schema.yml
workflows/ise_radius_integration/vars/ise_radius_integration_workflow_input.yml
yamale   -s workflows/ise_radius_integration/schema/ise_radius_integration_workflow_schema.yml  workflows/ise_radius_integration/vars/ise_radius_integration_workflow_input.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/ise_radius_integration/vars/ise_radius_integration_workflow_input.yml...
Validation success! 👍

```


# Execution Reference Logs
```bash

```
