# Plug and Play Provisioning Ansible Workflow

**Overview**

This Ansible playbook automates the provisioning and onboarding of new network devices leveraging Cisco's Plug and Play technology. It streamlines the process of configuring devices, minimizing manual efforts and promoting consistency.

**Key Features**

* **Zero-Touch Provisioning:** Remotely configure devices onboarded through PnP
* **Planned Provisioning:** Pre-configure settings and apply them when the device comes online.
* **Unclaimed Provisioning:** Discover and configure new devices that join the network unexpectedly.

**Workflows**

* **Planned Provisioning:**
    * Devices are pre-configured in Catalyst Center.
    * Upon connecting to the network, they automatically receive their configuration.
* **Unclaimed Provisioning:**
    * New devices are detected.
    * An administrator can initiate the provisioning process through this playbook.

**Prerequisites**

* Ansible installed
* `yamale` Python library installed (`pip install yamale`)
* Cisco DNA Center or Plug and Play Connect access configured

**Usage**

1. **Configure Variables**
    * Edit `catalyst_center_pnp_vars.yml` with your specific settings:
        * Catalyst Center credentials
        * Device information
        * Desired configuration templates
2. **Prepare Inventory**
    * Create `host_inventory_dnac1/hosts.yml` listing target devices.

3. **Validate Inputs**
```bash
    yamale -s workflows/plug_and_play/schema/plug_and_play_schema.yml workflows/plug_and_play/vars/catalyst_center_pnp_vars.yml 
```
3. **Execute Playbook**
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/plug_and_play/playbook/catalyst_center_pnp_playbook.yml --e VARS_FILE_PATH=../vars/catalyst_center_pnp_vars.yml
```
**Important Notes**

* Customize the playbook and variables to match your network environment.
* Consult Cisco documentation for in-depth information about Plug and Play.

**Disclaimer**

* This playbook is provided as-is. Use at your own risk.
* Ensure you have proper backups and understand the potential impact before running in a production environment.

---