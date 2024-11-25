# Catalyst Center SDA Fabric transits (IP/SDA) workflow

## Fabric Transits

### Transits
A transit is a site that interconnects two or more fabric sites or connects the fabric site with external networks (Internet, data center, and so on). There are two types of transit networks:

### IP transit: 
Uses a regular IP network to connect to an external network or to connect two or more fabric sites. It leverages a traditional IP-based (VRF-LITE, MPLS) network, which requires remapping of VRFs and SGTs between sites.

### SD-Access transit: 
Uses LISP/VxLAN encapsulation to connect two fabric sites. The SD-Access transit area may be defined as a portion of the fabric that has its own control plane nodes, but does not have edge or border nodes. However, it can work with a fabric that has an external border. With an SD-Access transit, an end-to-end policy plane is maintained using SGT group tags.

## Before you begin

Few things to know:

### Note:
1. You can’t add an SD-Access (LISP Pub/Sub) transit to a fabric site that uses LISP/BGP control plane. You can’t add SD-Access (LISP/BGP) transit to a fabric site that uses LISP Pub/Sub control plane.

2. To complete the native multicast configuration over multiple sites that are connected to the SD-Access transit, ensure that you enable multicast over SD-Access transit on the border nodes.

3. To create SD-Access Transit atleast one Transit CP device must be provided. 

## Create an Fabric transits: Running the Playbook
Playbook: workflows/sda_fabric_transits/playbook/playbook/sda_fabric_transits_workflow_playbook.yml
Schema: workflows/sda_fabric_transits/schema/sda_fabric_transits_workflow_schema.yml
Input Variables: [Title](vars/sda_fabric_transits_workflow_inputs.yml)
1. **Validate Your Input:**

```bash
   yamale -s workflows/sda_fabric_transits/schema/sda_fabric_transits_workflow_schema.yml workflows/sda_fabric_transits/vars/sda_fabric_transits_workflow_inputs.yml
```
2. **Execute the Playbook**
User inputs: ./workflows/sda_fabric_transits/vars/fabric_sites_zones_inputs.yml
Playbook: workflows/sda_fabric_transits/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=<your input file>
```
###  To create or update the fabroc transits and zones example
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml
```
###  To delete existing fabric transits:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sda_fabric_transits/playbook/delete_sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml
```
## Important Notes
Refer to the Catalyst Center documentation for detailed instructions on configuring fabric sites and fabric transits and using the Ansible playbooks.
Consider backing up your configuration before running the playbooks, especially the delete playbook.
If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.
