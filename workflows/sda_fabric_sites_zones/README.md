# Catalyst Center SDA Fabric Sites and Fabric Zones Playbook

## Fabric Sites

A fabric site is an independent area with a unique set of network devices, including control plane, border, edge, wireless controllers, and ISE PSNs. Different levels of redundancy and scale can be designed per site by including local resources such as DHCP, AAA, DNS, and Internet.

A fabric site can cover a single physical location, multiple locations, or only a subset of a location:

- **Single location**: branch, campus, or metro campus
- **Multiple locations**: metro campus + multiple branches
- **Subset of a location**: building or area within a campus

A Software-Defined Access (SDA) fabric network may comprise multiple sites. Each site benefits from scale, resiliency, survivability, and mobility. The overall aggregation of fabric sites accommodates a large number of endpoints and scales modularly or horizontally. Multiple fabric sites are interconnected using a transit.

## Before You Begin

You can create a fabric site only if IP Device Tracking (IPDT) is already configured for the site.

### In the Authentication Profile, You Do the Following:

1. **Choose an authentication template for the fabric site**:
    - **Closed Authentication**: Any traffic before authentication is dropped, including DHCP, DNS, and ARP.
    - **Open Authentication**: A host is allowed network access without having to go through 802.1X authentication.
    - **Low Impact**: Security is added by applying an ACL to the switch port, allowing very limited network access before authentication. After a host has been successfully authenticated, additional network access is granted.
    - **None**

2. (Optional) If you choose **Closed Authentication**, **Open Authentication**, or **Low Impact**, you can customize the authentication settings:
    - **First Authentication Method**: Choose 802.1x or MAC Authentication Bypass (MAB).
    - **802.1x Timeout (in seconds)**: Use the slider to specify the 802.1x timeout, in seconds.
    - **Wake on LAN**: Choose Yes or No.
    - **Number of Hosts**: Choose Unlimited or Single.
    - **BPDU Guard**: Use this checkbox to enable or disable the Bridge Protocol Data Unit (BPDU) guard on all the Closed Authentication ports.

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
Refer to the official documentation for detailed information on defining workflows: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/sda_fabric_sites_zones_workflow_manager


## Create an Fabric sites and fabric zones: Running the Playbook
Figure 1: Creating Fabric Sites and Fabric Zones
![Alt text](./images/Fabric_sites.png)

Figure 2 Select the Authentication profile for the fabric site
![Alt text](./images/Fabric_site_auth_profile.png)

Figure 3 Select the fabric zones
![Alt text](./images/Fabric_zones.png)

Figure 4 Configuratin Summary
![Alt text](./images/Fabric_site_zone_summary.png)

Achieveing the same through Playbook provide the following inputs:
fabric_sites_and_zones:
```bash
    - fabric_sites:
        - fabric_type: fabric_site
          site_name: Global/USA/AREA1/AREA1 BLD1
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
        - fabric_type: fabric_zone
          site_name: Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR1
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
        - fabric_type: fabric_zone
          site_name: Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR2
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
```

1. **Validate Your Input:**

```bash
   yamale -s workflows/sda_fabric_sites_zones/schema/sda_fabric_sites_zones_schema.yml workflows/sda_fabric_sites_zones/vars/sda_fabric_sites_zones_inputs.yml
```
2. **Execute the Playbook**
User inputs: ./workflows/sda_fabric_sites_zones/vars/sda_fabric_sites_zones_inputs.yml
Playbook: workflows/sda_fabric_sites_zones/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=<your input file>

#===========================
    TASK [Print the fabric site(s)/zone(s) output] *************************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": {
        "ansible_facts": {
            "discovered_interpreter_python": "/Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11"
        },
        "changed": true,
        "diff": [],
        "failed": false,
        "response": "Fabric site(s) '['Global/USA/AREA1/AREA1 BLD1']' created successfully in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR1', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR2']' created successfully in Cisco Catalyst Center.",
        "warnings": [
            "Platform darwin on host catalyst_center220 is using the discovered Python interpreter at /Users/pawansi/workspace/dnac_auto/pyats/bin/python3.11, but future installation of another Python interpreter could change the meaning of that path. See https://docs.ansible.com/ansible-core/2.15/reference_appendices/interpreter_discovery.html for more information."
        ]
    }
}
TASK [run command module to find python version] ***********************************************************************************************************************************************************************************************************
changed: [catalyst_center220 -> catalyst_center_hosts]

PLAY RECAP *************************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=6    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

```
Figure 6 Post Creation UI View
![Alt text](./images/Fabric_site_and_zones.png)


###  To create or update the fabric sites and zones example
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_sites_zones_inputs.yml
```
###  To delete existing discoveries:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/delete_sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_sites_zones_inputs.yml
```
## Creating Bulk Site Configurations using JINJA Template and Using the Playbook

Create a Jinja template for your desired input. An example Jinja template for sites is shown below.
This Example create 3 Areas and in Each Areas create 3 buildings and in each building it creates 3 floors. 
This example can be reused and customized to meet your requirements and scale as needed.

### Creating bulk sites with jinja template
workflow/sites/jinja_template/site_generation_template.j2 template can be used to customize the template and generate bulk sites.

```bash
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
fabric_sites_and_zones:
{% for i in range(1, 4) %}
    - fabric_sites:
        - fabric_type: fabric_site
          site_name: Global/USA/AREA{{i}}/AREA{{i}} BLD{{i}}
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
{% for j in range(1, 4) %}
        - fabric_type: fabric_zone
          site_name: Global/USA/AREA{{i}}/AREA{{i}} BLD{{i}}/AREA{{i}} BLD{{i}} FLOOR{{j}}
          authentication_profile: No Authentication
          is_pub_sub_enabled: true
{% endfor %}
{% endfor %}
```

Use the input var file: jinja_template_site_hierarchy_design_vars.yml and specify the name of your Jinja template in the input vars file.

5. Execute with Jinja template:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/sda_j2_template_fabric_sites_input.yml

TASK [Print the fabric site(s)/zone(s) output] *************************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": {
        "changed": true,
        "diff": [],
        "failed": false,
        "response": "Fabric site(s) '['Global/USA/AREA2/AREA2 BLD2', 'Global/USA/AREA3/AREA3 BLD3']' created successfully in Cisco Catalyst Center. Fabric site(s) '['Global/USA/AREA1/AREA1 BLD1']' need no update in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR1', 'Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR2', 'Global/USA/AREA2/AREA2 BLD2/AREA2 BLD2 FLOOR3', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR1', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR2', 'Global/USA/AREA3/AREA3 BLD3/AREA3 BLD3 FLOOR3']' created successfully in Cisco Catalyst Center. Fabric zone(s) '['Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR1', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR2', 'Global/USA/AREA1/AREA1 BLD1/AREA1 BLD1 FLOOR3']' need no update in Cisco Catalyst Center."
    }
}
#=========run logs================================
TASK [Delete the template file] ****************************************************************************************************************************************************************************************************************************
changed: [catalyst_center220]

TASK [Fabric site(s)/zone(s) playbook end time] ************************************************************************************************************************************************************************************************************
ok: [catalyst_center220]

TASK [Print fabric site(s)/zone(s) playbook execution time] ************************************************************************************************************************************************************************************************
ok: [catalyst_center220] => {
    "msg": "Fabric site(s)/zone(s) playbook run time: 2024-10-17 17:07:33.629001, end: 2024-10-17 17:08:46.419055"
}

TASK [run command module to find python version] ***********************************************************************************************************************************************************************************************************
changed: [catalyst_center220 -> catalyst_center_hosts]

PLAY RECAP *************************************************************************************************************************************************************************************************************************************************
catalyst_center220         : ok=9    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```
Figure 5 Jinja created fabric sites
![Alt text](./images/fabric_sites_with_jinja.png)


## References

```yaml
  ansible: 9.9.0
  ansible-core: 2.16.10
  ansible-runner: 2.4.0

  dnacentersdk: 2.8.3
  cisco.dnac: 6.29.0
  ansible.utils: 5.1.2
```


## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring fabric sites and fabric zones and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.
