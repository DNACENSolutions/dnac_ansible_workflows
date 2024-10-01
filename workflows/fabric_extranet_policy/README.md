# Catalyst Center SDA Fabric Extranet Policies Playbooks

## Extranet Policy Overview

Configure an extranet policy to allow route leaks between Layer 3 virtual networks (VNs), without using a fusion device. Use an extranet policy to provide the endpoints (hosts or users) with access to shared services like DHCP, DNS, Internet, and so on, through Catalyst Center automation. The shared services connect to a Provider VN. The endpoints that use the shared services reside in a Subscriber VN. An extranet policy establishes communication between the Provider VN and the Subscriber VNs.

You can create an extranet policy, edit an extranet policy, and delete an extranet policy for the following deployments:
    Single site fabric with IP Transit
    Multi-site fabric with SDA Transit



## Prerequisites
Consider the following guidelines before you configure an extranet policy:

    To configure an extranet policy, a device should operate Cisco IOS XE 17.9.1 or a later release.

    Extranet Policy is supported only on the fabric sites that have a LISP Pub/Sub control plane.

    To configure an extranet policy on a multisite fabric with SD-Access transit, ensure that all the sites have the provider VN.

    If you configure multiple VN policies in your network, the same VN cannot be the Provider VN in more than one policy.

    Extranet Policy does not support overlapping IP pools.

    Provider VN in a policy cannot be configured as a Subscriber VN in another VN Policy and conversely.

    Add the Provider VN to all the fabric sites where an extranet policy is applicable.

    Ensure that the Provider VNs do not leak into each other outside the fabric. Else, it might result in route leaks between the Subscriber VNs.

    Extranet policy is not supported on router devices.

    Inter-VN multicast through an extranet policy is not supported. You cannot route multicast between the Layer 3 virtual networks that are interconnected through an extranet policy.

## Create an Extranet Policy : Running the Playbook

1. **Validate Your Input:**

```bash
   yamale -s workflows/fabric_extranet_policy/schema/fabric_extranet_policy_schema.yml workflows/fabric_extranet_policy/vars/fabric_extranet_policy_inputs.yml
```
2. **Execute the Playbook**
Playbook: workflows/fabric_extranet_policy/playbook/fabric_extranet_policy_playbook.yml
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_extranet_policy/playbook/fabric_extranet_policy_playbook.yml --e VARS_FILE_PATH=<your input file>
```
###  To create or update the fabroc extranet Policy
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_extranet_policy/playbook/fabric_extranet_policy_playbook.yml --e VARS_FILE_PATH=../vars/fabric_extranet_policy_inputs.yml
```
###  To delete existing extranet policy:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_extranet_policy/playbook/delete_fabric_extranet_policy_playbook.yml --e VARS_FILE_PATH=../vars/fabric_extranet_policy_inputs.yml
```
## Important Notes
### Refer to the Catalyst Center documentation for detailed instructions on configuring fabric extranet Policies parameters and using the Ansible playbooks.
### Consider backing up your configuration before running the playbooks, especially the delete playbook.
### If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.

