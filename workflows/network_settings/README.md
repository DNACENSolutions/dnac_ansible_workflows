# Network Settings and Ip Pools reservation workflow !!
Workflow Playbook for configuring and updatings Network Settings and Ip Pools reservation on sites
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

catalyst_center_version: Define the version of Catalyst Center for which Scripts to run for legacy configs, you could keep it same.
role_details defines the accesss destails for the role.
network_settings_details: Details of Network settings 
To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/network_settings_workflow_manager/

To run this workflow, you follow the README.md 

## Example run: (Create network settings)
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_settings/playbook/network_settings_playbook.yml --e VARS_FILE_PATH=../vars/network_settings_vars.yml -vvv 

## Example run: (Create IP Pools and Reserve IP pools on sites)
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_settings/playbook/network_settings_playbook.yml --e VARS_FILE_PATH=../vars/global_pool_and_reserve_pools_on_sites.yml -vvv 

## Updating servers on sites AAA NTP, DNS, DHCP, TimeZone, SNMP, Logging, Banner etc.
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_settings/playbook/network_settings_playbook.yml --e VARS_FILE_PATH=../vars/server_update_aaa_ntp_dns_dhcp_tz_banner_syslog_snmp_netflow.yml -vvv 

##Example run: Delete Network Settings

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_settings/playbook/delete_network_settings_playbook.yml --e VARS_FILE_PATH=../vars/network_settings_vars.yml -vvv 

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
User Inputs for Users and roles are stored in  workflows/users_and_roles/vars/users_and_roles_workflow_inputs.yml

##Validate user input before running though ansible
```bash
(pyats) pawansi@PAWANSI-M-81A3 dnac_ansible_workflows % ./tools/validate.sh -s workflows/network_settings/schema/nw_settings_schema.yml -d workflows/network_settings/vars/network_settings_vars.yml
workflows/network_settings/schema/nw_settings_schema.yml
workflows/network_settings/vars/network_settings_vars.yml
yamale   -s workflows/network_settings/schema/nw_settings_schema.yml  workflows/network_settings/vars/network_settings_vars.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/network_settings/vars/network_settings_vars.yml...
Validation success! 👍
```

