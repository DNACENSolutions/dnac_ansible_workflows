# Assurance Health Score Settings Playbook
## Module Reference

Playbook for workflow Module: `assurance_device_health_score_settings_workflow_manager`

## Overview

This module provides resource management for assurance Health score settings in Cisco Catalyst Center.

## Description

The Assurance Health Score Settings module:
- Manages assurance Health score settings in Cisco Catalyst Center
- Supports updating configurations for Health score settings functionalities
- Interacts with Cisco Catalyst Center's Assurance settings to configure thresholds, rules, KPIs, and more for health score monitoring
- Allows customization of health scores based on device type
- Calculates network device health score using the lowest score among all included KPIs
- Provides ability to exclude specific KPIs from impacting the overall device health score calculation
- Note: Health score setting is not applicable for Third Party Devices

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

# Sample Input
file: assurance_healthscore_settings.yml
```yaml
catalyst_center_version: 2.3.7.9
catalyst_center_verify: false
assurance_health_score_settings:
  - device_health_score:
    - device_family: SWITCH_AND_HUB  # required field
      kpi_name: CPU Utilization  # required field
      include_for_overall_health: true  # required field
      threshold_value: 91
      synchronize_to_issue_threshold: false
  - device_health_score:
    - device_family: UNIFIED_AP
      kpi_name: Interference 6 GHz
      include_for_overall_health: true
      threshold_value: 30
      synchronize_to_issue_threshold: false
    - device_family: ROUTER
      kpi_name: Link Error
      include_for_overall_health: true
      threshold_value: 80
      synchronize_to_issue_threshold: false
```

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


