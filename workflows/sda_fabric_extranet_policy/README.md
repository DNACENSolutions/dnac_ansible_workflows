# Catalyst Center SDA Fabric Extranet Policies Playbooks

## I. Overview
### 1. Extranet Policy Overview

Configure an extranet policy to allow route leaks between Layer 3 virtual networks (VNs), without using a fusion device. Use an extranet policy to provide the endpoints (hosts or users) with access to shared services like DHCP, DNS, Internet, and so on, through Catalyst Center automation. The shared services connect to a Provider VN. The endpoints that use the shared services reside in a Subscriber VN. An extranet policy establishes communication between the Provider VN and the Subscriber VNs.

You can create an extranet policy, edit an extranet policy, and delete an extranet policy for the following deployments:
    Single site fabric with IP Transit
    Multi-site fabric with SDA Transit

### 2. Important Notes
- Refer to the Catalyst Center documentation for detailed instructions on configuring fabric extranet Policies parameters and using the Ansible playbooks.
- Consider backing up your configuration before running the playbooks, especially the delete playbook.
- If you encounter any issues, review the Ansible playbook output for error messages and consult the Catalyst Center documentation or support resources.


### 3. Detailed Input Spec
Refer to: [https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/sda_extranet_policies_workflow_manager/](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/sda_extranet_policies_workflow_manager/)

### 4. Features
  - Manage SD-Access Extranet Policy operations such as create, update, or delete extranet policies in Cisco Catalyst Center.
  - API to create a new extranet policy.
  - API to update an existing or edit an existing extranet policy.
  - API for deletion of an existing extranet policy using the policy name.

### 5. Prerequisites
Consider the following guidelines before you configure an extranet policy:

- To configure an extranet policy, a device should operate Cisco IOS XE 17.9.1 or a later release.

- Extranet Policy is supported only on the fabric sites that have a LISP Pub/Sub control plane.

- To configure an extranet policy on a multisite fabric with SD-Access transit, ensure that all the sites have the provider VN.

- If you configure multiple VN policies in your network, the same VN cannot be the Provider VN in more than one policy.

- Extranet Policy does not support overlapping IP pools.

- Provider VN in a policy cannot be configured as a Subscriber VN in another VN Policy and conversely.

- Add the Provider VN to all the fabric sites where an extranet policy is applicable.

- Ensure that the Provider VNs do not leak into each other outside the fabric. Else, it might result in route leaks between the Subscriber VNs.

- Extranet policy is not supported on router devices.

- Inter-VN multicast through an extranet policy is not supported. You cannot route multicast between the Layer 3 virtual networks that are interconnected through an extranet policy.


## II. Procedure
### 1. Prepare your Ansible environment:

- install Ansible if you haven't already
- Ensure you have network connectivity to your Catalyst Center instance.
- Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

### 2. Configure Host Inventory:
- The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
- Make sure the dnac_version in this file matches your actual Catalyst Center version.
- The Sample host_inventory_dnac1/hosts.yml

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

### 3. Define input:
The /vars/fabric_extranet_policy_inputs.yml file stores the sites details you want to configure.

```bash
# Description: This file contains the input variables for the fabric extranet policy workflow.
    - extranet_policy_name: ex_policy_infra_vn_provider
      provider_virtual_network: INFRA VN
      subscriber_virtual_networks: 
          - DEFAULT_VN
          - VN_1
    - extranet_policy_name: ex_policy_default_vn_provider
      provider_virtual_network: VN_1
      subscriber_virtual_networks: 
          - VN_2
          - VN_3
      fabric_sites: 
          - Global/USA/SAN JOSE
          - Global/USA/SAN-FRANCISCO

```

### 4. How to Validate Input

**Validate Your Input:**

```bash
   yamale -s workflows/fabric_extranet_policy/schema/fabric_extranet_policy_schema.yml workflows/fabric_extranet_policy/vars/fabric_extranet_policy_inputs.yml
```
**Execute the Playbook**

- Playbook: workflows/fabric_extranet_policy/playbook/fabric_extranet_policy_playbook.yml

####  To create or update the fabroc extranet Policy:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_extranet_policy/playbook/fabric_extranet_policy_playbook.yml --e VARS_FILE_PATH=../vars/fabric_extranet_policy_inputs.yml
```
####  To delete existing extranet policy:
```bash
 ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/fabric_extranet_policy/playbook/delete_fabric_extranet_policy_playbook.yml --e VARS_FILE_PATH=../vars/fabric_extranet_policy_inputs.yml
```

## III. Detailed steps to perform

### 1. Create SDA Extranet Policies
#### **Mapping config to UI Actions**
- The config parameter within this task corresponds to the "Provision > Virtural Networks> Create Template" action in the Cisco Catalyst Center UI.
- Select "Provision" -> "Virtual Networks" to access the Virtual Networks page.
![alt text](./images/ext1.png)
-  Click Layer3 Virutal Network
![alt text](./images/ext2.png)
- Click "Extranet Policies" -> "Create Extranet Policy" to start creating a new policy.
![alt text](./images/ext3.png)
- ext4.png: Enter the Extranet Policy name (eg: "ex_policy_infra_vn_provider") and click "Next".
![alt text](./images/ext4.png)
- Select Provider Virtual Network (eg: "INFRA_VN") and click "Next".
![alt text](./images/ext5.png)
- Select Subscriber Virtual Networks (eg: "DEFAULT_VN", "NY_L3_1") and click "Next".
![alt text](./images/ext6.png)
- Select "New York" in Fabric Sites, click "Next" to specify the site for the Extranet policy.
![alt text](./images/ext7.png)
- Check "Summary," click "Next" to confirm the configuration.
![alt text](./images/ext8.png)
- Select "Preview and Deploy," click "Deploy" to deploy the Extranet policy.
![alt text](./images/ext9.png)
- Click "Save Intent," then click "Submit" to save and submit the configuration.
![alt text](./images/ext10.png)
- Confirm "ex_policy_infra_vn_provider" in the Extranet Policies list to test the policy in action.
![alt text](./images/ext11.png)
- Check Extranet Policy created
![alt text](./images/ext12.png)

#### **YAML Structure and Parameter Explanation**

```bash
- name: Create Extranet Policy
  cisco.dnac.sda_extranet_policies_workflow_manager:
    <<: *common_config
    state: merged
    config:
      - "{{ item }}"
  with_list: "{{ extranet_policies }}"
  tags: create_extranet_policies
```

#### **Example Input File**

```bash
    - extranet_policy_name: ex_policy_infra_vn_provider
      provider_virtual_network: INFRA VN
      subscriber_virtual_networks: 
          - DEFAULT_VN
          - NY_L3_1
      fabric_sites: 
          - Global/USA/New York
```

### 2. Update SDA Extranet Policies
#### **Mapping config to UI Actions**
- Select Extrabnet Policy Name to update -> "More Action" -> "Edit Extranet Policy" to update Extranet policy
![alt text](./images/edit_ext1.png)
- In Subscriber Virtual Networks section _> "Edit" to update Subscriber Virtual Networks
![alt text](./images/edit_ext2.png)
Check all Subscriber Virtual Networks that have been added and Subscriber Virtual Networks that you want to add
![alt text](./images/edit_ext3.png)
- Select Subscriber Virtual Networks that you want to add -> "Next" to update Subscriber Virtual Networks
![alt text](./images/edit_ext5.png)
- Select Fabric Sites that you want to Update, if not updated, you can skip this step -> "Next"
![alt text](./images/edit_ext41.png)
- Check the configuration information that has changed -> "Next"
![alt text](./images/edit_ext42.png)
- Deploy Extrabnet Policy that has just been updated
![alt text](./images/edit_ext6.png)
- Enter "Task Name" for the update task -> Submit
![alt text](./images/edit_ext7.png)
- Execute "Save Intent"
![alt text](./images/edit_ext8.png)
- Update notification successful
![alt text](./images/edit_ext9.png)
- Check configuration update 
![alt text](./images/edit_ext10.png)

#### **YAML Structure and Parameter Explanation**

```bash
- name: Update Extranet Policy
  cisco.dnac.sda_extranet_policies_workflow_manager:
    <<: *common_config
    state: merged
    config:
      - "{{ item }}"
  with_list: "{{ extranet_policies }}"
  tags: update_extranet_policies
```

#### **Example Input File**

```bash
    - extranet_policy_name: ex_policy_infra_vn_provider
      provider_virtual_network: INFRA VN
      subscriber_virtual_networks: 
          - DEFAULT_VN
          - NY_L3_1
          - NY_L3_2
      fabric_sites: 
          - Global/USA/New York
```

### 2. Delete SDA Extranet Policies
#### **Mapping config to UI Actions**
- Select Extrabnet Policy Name to update -> "More Action" -> "Delete Extranet Policy" to update Extranet policy
![alt text](./images/delete_1.png)
- Click "Apply" to delete
![alt text](./images/delete_2.png)
- Click "Next" -> to continue deleting Extranet Policy
![alt text](./images/delete_3.png)
- Load the delete Extranet Policy function
![alt text](./images/delete_4.png)
- Check the deleted Extranet Policy
![alt text](./images/delete_5.png)


#### **YAML Structure and Parameter Explanation**

```bash
- name: Delete Extranet Policy
  cisco.dnac.sda_extranet_policies_workflow_manager:
    <<: *common_config
    state: delete
    config:
      - "{{ item }}"
  with_list: "{{ extranet_policies }}"
  tags: delete_extranet_policies
```

#### **Example Input File**

```bash
    - extranet_policy_name: ex_policy_infra_vn_provider
```

## IV. References:

Note: The environment is used for the references in the above instructions.

```
  ansible: 9.9.0
  ansible-core: 2.16.10
  ansible-runner: 2.4.0

  dnacentersdk: 2.8.3
  cisco.dnac: 6.30.0
  ansible.utils: 5.1.2
```
Cisco Catalyst Center Ansible Module Documentation: [sda_extranet_policies_workflow_manager](https://cisco-en-programmability.github.io/dnacenter-ansible/main/plugins/sda_extranet_policies_workflow_manager.html)

GitHub Source Code: [sda_extranet_policies_workflow_manager.py](https://github.com/cisco-en-programmability/dnacenter-ansible/blob/main/plugins/modules/sda_extranet_policies_workflow_manager.py)