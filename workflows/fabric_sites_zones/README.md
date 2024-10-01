# Catalyst Center SDA Fabric sites and fabric Zones Playbooks

## Fabric Sites

A fabric site is an independent fabric area with a unique set of network devices: control plane, border, edge, wireless controller, ISE PSN. Different levels of redundancy and scale can be designed per site by including local resources: DHCP, AAA, DNS, Internet, and so on.

A fabric site can cover a single physical location, multiple locations, or only a subset of a location:

    Single location: branch, campus, or metro campus

    Multiple locations: metro campus + multiple branches

    Subset of a location: building or area within a campus

A Software-Defined Access fabric network may comprise multiple sites. Each site has the benefits of scale, resiliency, survivability, and mobility. The overall aggregation of fabric sites accommodates a large number of endpoints and scales modularly or horizontally. Multiple fabric sites are interconnected using a transit.

## Before you begin

You can create a fabric site only if IP Device Tracking (IPDT) is already configured for the site.

## In the Authentication Profile you do the following:

    Choose an authentication template for the fabric site:

        Closed Authentication: Any traffic before authentication is dropped, including DHCP, DNS, and ARP.

        Open Authentication: A host is allowed network access without having to go through 802.1X authentication.

        Low Impact: Security is added by applying an ACL to the switch port, to allow very limited network access before authentication. After a host has been successfully authenticated, additional network access is granted.

        None

    (Optional) If you choose Closed Authentication, Open Authentication, or Low Impact, you can customize the authentication settings:

        First Authentication Method: Choose 802.1x or MAC Authentication Bypass (MAB)

        802.1x Timeout (in seconds): Use the slider to specify the 802.1x timeout, in seconds.

        Wake on LAN: Choose Yes or No.

        Number of Hosts: Choose Unlimited or Single.

        BPDU Guard: Use this check box to enable or disable the Bridge Protocol Data Unit (BPDU) guard on all the Closed Authentication ports.

## Create an Fabric sites and fabric zones: Running the Playbook

1. **Validate Your Input:**

```bash
   yamale -s workflows/fabric_sites_zones/schema/fabric_sites_zones_schema.yml workflows/fabric_sites_zones/vars/fabric_sites_zones_inputs.yml
```
2. **Execute the Playbook**
[Title](playbook/fabric_sites_zones_playbook.yml)
User inputs: ./workflows/fabric_sites_zones/vars/fabric_sites_zones_inputs.yml
Playbook: workflows/fabric_sites_zones/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_sites_zones/playbook/fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=<your input file>
```
###  To create or update the fabroc sites and zones example
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_sites_zones/playbook/fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/fabric_sites_zones_inputs.yml
```
###  To delete existing discoveries:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_sites_zones/playbook/delete_fabric_sites_zones_playbook.yml --e VARS_FILE_PATH=../vars/fabric_sites_zones_inputs.yml
```
## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring fabric sites and fabric zones and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.
