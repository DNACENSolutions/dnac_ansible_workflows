# Network Compliance Workflow Playbook
Workflow Playbook for Assigning devices to sites network complianceing, Re-network complianceing and Deleteing the devices in Inventory. 
This workflow playbook is supported from Catalyst Center Release version 2.3.7.6

network_compliance_details  defines the list of devices and devices details for the devices to be run rough the playbooks


To define the details you can refer the full workflow specification: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/network compliance_workflow_manager/


To run this workflow, you follow the README.md 

##Example run:

ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml --e VARS_FILE_PATH=../vars/network_compliance_workflow_input.yml -vvvv

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
(pyats) dnac_ansible_workflows % ./tools/validate.sh -s workflows/network_compliance/schema/network_compliance_workflow_schema.yml -d workflows/network_compliance/vars/network_compliance_workflow_input.yml 
workflows/network_compliance/schema/network_compliance_workflow_schema.yml
workflows/network_compliance/vars/network_compliance_workflow_input.yml
yamale   -s workflows/network_compliance/schema/network_compliance_workflow_schema.yml  workflows/network_compliance/vars/network_compliance_workflow_input.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/vars/network_compliance_workflow_input.yml...
Validation success! 👍
```


# Execution Reference Logs
```bash
(pyats) pawansi@PAWANSI-M-81A3 dnac_ansible_workflows % ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml --e VARS_FILE_PATH=../vars/network_compliance_workflow_input.yml -vvvv
ansible-playbook [core 2.15.3]
  config file = None
  configured module search path = ['/Users/pawansi/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/pawansi/workspace/dnac_auto/pyats/lib/python3.11/site-packages/ansible
  ansible collection location = /Users/pawansi/.ansible/collections:/usr/share/ansible/collections
  executable location = /Users/pawansi/workspace/dnac_auto/pyats/bin/ansible-playbook
  python version = 3.11.4 (main, Jul 25 2023, 17:07:07) [Clang 14.0.3 (clang-1403.0.22.14.1)] (/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11)
  jinja version = 3.1.2
  libyaml = True
No config file found; using defaults
setting up inventory plugins
Loading collection ansible.builtin from 
host_list declined parsing /Users/pawansi/dnac_ansible_workflows/host_inventory_dnac1/hosts.yml as it did not pass its verify_file() method
script declined parsing /Users/pawansi/dnac_ansible_workflows/host_inventory_dnac1/hosts.yml as it did not pass its verify_file() method
Parsed /Users/pawansi/dnac_ansible_workflows/host_inventory_dnac1/hosts.yml inventory source with yaml plugin
Loading collection cisco.dnac from /Users/pawansi/.ansible/collections/ansible_collections/cisco/dnac
Loading callback plugin default of type stdout, v2.0 from /Users/pawansi/workspace/dnac_auto/pyats/lib/python3.11/site-packages/ansible/plugins/callback/default.py
Skipping callback 'default', as we already have a stdout callback.
Skipping callback 'minimal', as we already have a stdout callback.
Skipping callback 'oneline', as we already have a stdout callback.

PLAYBOOK: network_compliance_workflow_playbook.yml ******************************************************************************************************************************************************************************************************
Positional arguments: workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml
verbosity: 4
connection: smart
timeout: 10
become_method: sudo
tags: ('all',)
inventory: ('/Users/pawansi/dnac_ansible_workflows/host_inventory_dnac1/hosts.yml',)
extra_vars: ('VARS_FILE_PATH=../vars/network_compliance_workflow_input.yml',)
forks: 5
1 plays in workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'

PLAY [Network Compliance on  Cisco Catalyst Center] *****************************************************************************************************************************************************************************************************
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [Network Compliance devices on Cisco Catalyst Center] **********************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:26
ok: [catalyst_center220] => {
    "ansible_facts": {
        "long_op_start": "2024-09-06 22:22:18.229560"
    },
    "changed": false
}
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [Network Compliance devices on Cisco Catalyst Center] **********************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:29
<catalyst_center220> ESTABLISH LOCAL CONNECTION FOR USER: pawansi
<catalyst_center220> EXEC /bin/sh -c 'echo ~pawansi && sleep 0'
<catalyst_center220> EXEC /bin/sh -c '( umask 77 && mkdir -p "` echo /Users/pawansi/.ansible/tmp `"&& mkdir "` echo /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596 `" && echo ansible-tmp-1725686538.312991-77255-136033103198596="` echo /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596 `" ) && sleep 0'
<catalyst_center220> Attempting python interpreter discovery
<catalyst_center220> EXEC /bin/sh -c 'echo PLATFORM; uname; echo FOUND; command -v '"'"'python3.11'"'"'; command -v '"'"'python3.10'"'"'; command -v '"'"'python3.9'"'"'; command -v '"'"'python3.8'"'"'; command -v '"'"'python3.7'"'"'; command -v '"'"'python3.6'"'"'; command -v '"'"'python3.5'"'"'; command -v '"'"'/usr/bin/python3'"'"'; command -v '"'"'/usr/libexec/platform-python'"'"'; command -v '"'"'python2.7'"'"'; command -v '"'"'/usr/bin/python'"'"'; command -v '"'"'python'"'"'; echo ENDFOUND && sleep 0'
<catalyst_center220> Python interpreter discovery fallback (unsupported platform for extended discovery: darwin)
Using module file /Users/pawansi/.ansible/collections/ansible_collections/cisco/dnac/plugins/modules/network_compliance_workflow_manager.py
<catalyst_center220> PUT /Users/pawansi/.ansible/tmp/ansible-local-77251po1mpkhx/tmpsuycx0i1 TO /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596/AnsiballZ_network_compliance_workflow_manager.py
<catalyst_center220> EXEC /bin/sh -c 'chmod u+x /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596/ /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596/AnsiballZ_network_compliance_workflow_manager.py && sleep 0'
<catalyst_center220> EXEC /bin/sh -c '/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11 /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596/AnsiballZ_network_compliance_workflow_manager.py && sleep 0'
<catalyst_center220> EXEC /bin/sh -c 'rm -f -r /Users/pawansi/.ansible/tmp/ansible-tmp-1725686538.312991-77255-136033103198596/ > /dev/null 2>&1 && sleep 0'
[WARNING]: Platform darwin on host catalyst_center220 is using the discovered Python interpreter at /Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11, but future installation of another Python interpreter could change the meaning of that
path. See https://docs.ansible.com/ansible-core/2.15/reference_appendices/interpreter_discovery.html for more information.
ok: [catalyst_center220] => {
    "ansible_facts": {
        "discovered_interpreter_python": "/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11"
    },
    "changed": false,
    "diff": [],
    "invocation": {
        "module_args": {
            "config": [
                {
                    "ip_address_list": [
                        "204.1.2.2",
                        "204.1.2.1",
                        "204.1.2.4"
                    ],
                    "run_compliance": true,
                    "run_compliance_categories": [
                        "INTENT",
                        "RUNNING_CONFIG",
                        "IMAGE",
                        "PSIRT"
                    ],
                    "site_name": "Global/USA/SAN JOSE/BLD23",
                    "sync_device_config": true
                }
            ],
            "config_verify": false,
            "dnac_api_task_timeout": 1200,
            "dnac_debug": true,
            "dnac_host": "10.195.227.14",
            "dnac_log": true,
            "dnac_log_append": true,
            "dnac_log_file_path": "dnac.log",
            "dnac_log_level": "INFO",
            "dnac_password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "dnac_port": "443",
            "dnac_task_poll_interval": 2,
            "dnac_username": "admin",
            "dnac_verify": false,
            "dnac_version": "2.3.7.6",
            "state": "merged",
            "validate_response_schema": true
        }
    },
    "msg": "Device(s) with IP address(es): 204.192.4.2, 204.1.2.1, 204.1.2.4, 204.1.2.2 are already compliant with the RUNNING_CONFIG compliance type. Therefore, the task 'Sync Device Configuration' is not required.",
    "response": [],
    "status": "ok"
}
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [Print the Network Compliance devices output] ******************************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:35
ok: [catalyst_center220] => {
    "msg": {
        "ansible_facts": {
            "discovered_interpreter_python": "/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11"
        },
        "changed": false,
        "diff": [],
        "failed": false,
        "msg": "Device(s) with IP address(es): 204.192.4.2, 204.1.2.1, 204.1.2.4, 204.1.2.2 are already compliant with the RUNNING_CONFIG compliance type. Therefore, the task 'Sync Device Configuration' is not required.",
        "response": [],
        "status": "ok",
        "warnings": [
            "Platform darwin on host catalyst_center220 is using the discovered Python interpreter at /Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11, but future installation of another Python interpreter could change the meaning of that path. See https://docs.ansible.com/ansible-core/2.15/reference_appendices/interpreter_discovery.html for more information."
        ]
    }
}
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [Network Compliance devices playbook end time] *****************************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:38
ok: [catalyst_center220] => {
    "ansible_facts": {
        "long_op_end": "2024-09-06 22:22:26.036856"
    },
    "changed": false
}
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [Print Network Compliance devices playbook execution time] *****************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:41
ok: [catalyst_center220] => {
    "msg": "Network Compliance devices playbook run time: 2024-09-06 22:22:18.229560, end: 2024-09-06 22:22:26.036856"
}
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'

TASK [run command module to find python version] ********************************************************************************************************************************************************************************************************
task path: /Users/pawansi/dnac_ansible_workflows/workflows/network_compliance/playbook/network_compliance_workflow_playbook.yml:45
Read vars_file '{{ VARS_FILE_PATH }}'
<catalyst_center_hosts> ESTABLISH LOCAL CONNECTION FOR USER: pawansi
<catalyst_center_hosts> EXEC /bin/sh -c 'echo ~pawansi && sleep 0'
<catalyst_center_hosts> EXEC /bin/sh -c '( umask 77 && mkdir -p "` echo /Users/pawansi/.ansible/tmp `"&& mkdir "` echo /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969 `" && echo ansible-tmp-1725686546.153583-77282-13787995213969="` echo /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969 `" ) && sleep 0'
<catalyst_center220> Attempting python interpreter discovery
<catalyst_center_hosts> EXEC /bin/sh -c 'echo PLATFORM; uname; echo FOUND; command -v '"'"'python3.11'"'"'; command -v '"'"'python3.10'"'"'; command -v '"'"'python3.9'"'"'; command -v '"'"'python3.8'"'"'; command -v '"'"'python3.7'"'"'; command -v '"'"'python3.6'"'"'; command -v '"'"'python3.5'"'"'; command -v '"'"'/usr/bin/python3'"'"'; command -v '"'"'/usr/libexec/platform-python'"'"'; command -v '"'"'python2.7'"'"'; command -v '"'"'/usr/bin/python'"'"'; command -v '"'"'python'"'"'; echo ENDFOUND && sleep 0'
<catalyst_center220> Python interpreter discovery fallback (unsupported platform for extended discovery: darwin)
Using module file /Users/pawansi/workspace/dnac_auto/pyats/lib/python3.11/site-packages/ansible/modules/command.py
<catalyst_center_hosts> PUT /Users/pawansi/.ansible/tmp/ansible-local-77251po1mpkhx/tmpsn3ed7wm TO /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969/AnsiballZ_command.py
<catalyst_center_hosts> EXEC /bin/sh -c 'chmod u+x /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969/ /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969/AnsiballZ_command.py && sleep 0'
<catalyst_center_hosts> EXEC /bin/sh -c '/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11 /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969/AnsiballZ_command.py && sleep 0'
<catalyst_center_hosts> EXEC /bin/sh -c 'rm -f -r /Users/pawansi/.ansible/tmp/ansible-tmp-1725686546.153583-77282-13787995213969/ > /dev/null 2>&1 && sleep 0'
changed: [catalyst_center220 -> catalyst_center_hosts] => {
    "changed": true,
    "cmd": [
        "which",
        "python"
    ],
    "delta": "0:00:00.010597",
    "end": "2024-09-06 22:22:26.739389",
    "invocation": {
        "module_args": {
            "_raw_params": "which python",
            "_uses_shell": false,
            "argv": null,
            "chdir": null,
            "creates": null,
            "executable": null,
            "removes": null,
            "stdin": null,
            "stdin_add_newline": true,
            "strip_empty_ends": true
        }
    },
    "msg": "",
    "rc": 0,
    "start": "2024-09-06 22:22:26.728792",
    "stderr": "",
    "stderr_lines": [],
    "stdout": "/Users/pawansi/workspace/dnac_auto/pyats/bin/python",
    "stdout_lines": [
        "/Users/pawansi/workspace/dnac_auto/pyats/bin/python"
    ]
}
Read vars_file '{{ VARS_FILE_PATH }}'
Read vars_file '{{ VARS_FILE_PATH }}'

PLAY RECAP **********************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=6    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

```
