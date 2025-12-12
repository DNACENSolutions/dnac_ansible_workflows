# Cisco Catalyst Center SDA Fabric Transits Workflow Playbooks

**Overview**

This module provides a comprehensive toolkit for managing SDA (Software-Defined Access) fabric transits in *Cisco Catalyst Center*. It supports creating, updating, and deleting transit networks with flexible configurations, enabling efficient management of network connectivity between fabric sites and external networks. Key features include:

- **Fabric Transit Management**:  
  - **Create** IP-based transits, SD-Access LISP Pub/Sub transits, and LISP BGP transits.  
  - **Update** transit configurations including control plane devices and multicast settings.  
  - **Delete** single or multiple transit networks.  
  - **Support** for site hierarchy-based transit deployment.

- **Transit Types**:  
  - **IP-Based Transit**: Traditional IP routing (VRF-LITE, MPLS) for connecting fabric sites or external networks.  
  - **SDA LISP Pub/Sub Transit**: LISP/VxLAN encapsulation for end-to-end policy plane with SGT tags.  
  - **SDA LISP BGP Transit**: Integration of LISP with BGP for optimized inter-site routing.

- **Control Plane Configuration**:  
  - **Assign** control plane network devices for SDA transits.  
  - **Support** for multiple control plane nodes (up to 2 for BGP, 4 for Pub/Sub).  
  - **Enable/disable** multicast over transit for Pub/Sub configurations.

- **Site Hierarchy Support**:  
  - **Associate** transits with specific site hierarchies (Global/Area/Building/Floor).  
  - **Enable** site-aware transit management and location-based segmentation.  
  - **Support** from Catalyst Center version 3.1.3.0 onwards.

- **BGP Configuration**:  
  - **Configure** Autonomous System Numbers (ASN) for IP-based transits.  
  - **Support** for ASN range 1 to 4294967295.

**Version Added**: `6.18.0`  
*Note*: This version refers to the Cisco Catalyst Center Ansible collection.

---

## Workflow Steps

Follow these steps to configure and deploy SDA fabric transits in *Cisco Catalyst Center* using Ansible playbooks.

### Step 1: Install and Generate Inventory

**Prepare your environment** by installing Ansible and the required *Cisco Catalyst Center* collection, then generate an inventory file.

1. **Install Ansible**:  
   Refer to the [official Ansible documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for installation instructions.

2. **Install Cisco Catalyst Center Collection**:  
   ```bash
   ansible-galaxy collection install cisco.dnac
   ```

3. **Generate Inventory**:  
   Create an Ansible inventory file (e.g., `inventory/demo_lab/hosts.yaml`) with your *Cisco Catalyst Center* appliance details. Define variables such as `catalyst_center_host`, `catalyst_center_username`, and `catalyst_center_password`.  
   > **Note**: For security, consider using *Ansible Vault* to encrypt sensitive data like passwords.  
   ```yaml
   catalyst_center_hosts:
       hosts:
           catalyst_center220:
               catalyst_center_host: xx.xx.xx.xx
               catalyst_center_password: XXXXXXXX
               catalyst_center_port: 443
               catalyst_center_timeout: 60
               catalyst_center_username: admin
               catalyst_center_verify: false  # Enable for production with valid certificates
               catalyst_center_version: 3.1.3.0  # Specify the version
               catalyst_center_debug: true
               catalyst_center_log_level: debug
               catalyst_center_log: true
               ansible_python_interpreter: /auto/cat-sol/pyats-ws/pyats-apoorv/bin/python
   ```

---

### Step 2: Define Inputs and Validate

Define input variables and validate your configuration to ensure successful fabric transit management.

#### Define Input Variables
Create a variable file (e.g., `workflows/sda_fabric_transits/vars/sda_fabric_transits_workflow_inputs.yml`) to specify the desired state of your fabric transits for creation, update, or deletion.

#### Schema for SDA Fabric Transits
The following schema outlines the structure for configuring SDA fabric transits in *Cisco Catalyst Center*. Parameters are listed with their requirements and descriptions.

| **Parameter**                | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|------------------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `fabric_transits` | List       | Yes          | `N/A`             | List of fabric transit configurations to create or manage.                           |

##### Fabric Transit Configuration (`sda_fabric_transits`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `name`        | String     | Yes          | `N/A`             | Name of the SDA fabric transit. Must be unique.                                           |
| `transit_site_hierarchy`          | String       | No         | `Global`             | Site hierarchy for transit (e.g., Global/USA/SAN JOSE). Supported from version 3.1.3.0+.                          |
| `transit_type`        | String       | No         | `IP_BASED_TRANSIT`             | Type of transit: IP_BASED_TRANSIT, SDA_LISP_PUB_SUB_TRANSIT, or SDA_LISP_BGP_TRANSIT.                  |
| `ip_transit_settings`            | Dict       | No*         | `N/A`             | Configuration for IP-based transit. *Required if transit_type is IP_BASED_TRANSIT.                   |
| `sda_transit_settings`| Dict       | No*         | `N/A`             | Configuration for SDA transits. *Required if transit_type is SDA_LISP_*.                       |

##### IP Transit Settings (`ip_transit_settings`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `routing_protocol_name`               | String     | No          | `BGP`             | Routing protocol name. Currently only BGP is supported.                                                              |
| `autonomous_system_number`| String     | Yes         | `N/A`             | ASN for BGP routing. Range: 1-4294967295. Must be unique per IP transit.                        |

##### SDA Transit Settings (`sda_transit_settings`)

| **Parameter**         | **Type**   | **Required** | **Default Value** | **Description**                                                                 |
|-----------------------|------------|--------------|-------------------|---------------------------------------------------------------------------------|
| `is_multicast_over_transit_enabled`       | Boolean    | No         | `false`           | Enable multicast over transit. Available only for SDA_LISP_PUB_SUB_TRANSIT.                                                   |
| `control_plane_network_device_ips`     | List       | Yes         | `N/A`             | IP addresses of control plane devices. Required for SDA transits. Max 2 for BGP, 4 for Pub/Sub.                                      |

---

#### Example Input Files

**Prerequisites**  
Before creating fabric transits, ensure the following are configured in *Cisco Catalyst Center*:  
- **Site Hierarchy**: Define the organizational site structure.  
- **Fabric Sites/Zones**: Create fabric sites where control plane devices reside.  
- **Network Devices**: Provision and assign devices to fabric sites.  
- **Device Requirements**: 
  - SDA_LISP_PUB_SUB_TRANSIT requires devices with IOS XE 17.6 or later.
  - Control plane devices must exist in a fabric site or zone.

##### 1. **Create IP-Based Transit**  
*Example*: Configure a new IP-based transit with BGP routing.
![Alt text](images/image.png)
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: IP_Transit_AS200
        transit_type: IP_BASED_TRANSIT
        transit_site_hierarchy: Global/USA/SAN JOSE  # Optional, defaults to Global
        ip_transit_settings:
          routing_protocol_name: BGP
          autonomous_system_number: "200"
```

##### 2. **Create SDA LISP Pub/Sub Transit**  
*Example*: Configure an SDA transit with multicast enabled.
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: SDA_Transit_PubSub
        transit_type: SDA_LISP_PUB_SUB_TRANSIT
        transit_site_hierarchy: Global/USA/RTP
        sda_transit_settings:
          is_multicast_over_transit_enabled: true
          control_plane_network_device_ips:
            - 10.1.1.1
            - 10.1.1.2
            - 10.1.1.3
```

##### 3. **Create SDA LISP BGP Transit**  
*Example*: Configure an SDA BGP transit with control plane devices.
![Alt text](images/image-1.png)
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: SDA_Transit_BGP
        transit_type: SDA_LISP_BGP_TRANSIT
        sda_transit_settings:
          control_plane_network_device_ips:
            - 192.168.1.10
            - 192.168.1.11
```

##### 4. **Create Multiple Transits**  
*Example*: Deploy multiple transit types in a single playbook run.
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: IP_Transit_AS100
        transit_type: IP_BASED_TRANSIT
        ip_transit_settings:
          autonomous_system_number: "100"
      - name: SDA_Transit_1
        transit_type: SDA_LISP_PUB_SUB_TRANSIT
        transit_site_hierarchy: Global/Corporate/HQ
        sda_transit_settings:
          is_multicast_over_transit_enabled: false
          control_plane_network_device_ips:
            - 204.1.2.5
            - 204.1.2.6
      - name: BGP_Transit_1
        transit_type: SDA_LISP_BGP_TRANSIT
        sda_transit_settings:
          control_plane_network_device_ips:
            - 172.16.1.1
            - 172.16.1.2
```

##### 5. **Update Transit Configuration**  
*Example*: Update control plane devices for an existing transit.
![Alt text](./images/image-3.png)
> **Note**: IP-based transits cannot change ASN after creation. Only control plane devices and multicast settings can be updated for SDA transits.
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: SDA_Transit_1
        transit_type: SDA_LISP_PUB_SUB_TRANSIT
        sda_transit_settings:
          is_multicast_over_transit_enabled: true  # Changed from false
          control_plane_network_device_ips:
            - 204.1.2.5
            - 204.1.2.6
            - 204.1.2.7  # Added new control plane device
```

##### 6. **Update Site Hierarchy**  
*Example*: Change the site association of an existing transit (3.1.3.0+).
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: IP_Transit_AS100
        transit_type: IP_BASED_TRANSIT
        transit_site_hierarchy: Global/USA/NewYork  # Updated site hierarchy
        ip_transit_settings:
          autonomous_system_number: "100"
```

##### 7. **Delete Fabric Transits**  
*Example*: Delete one or more fabric transits by name.
![Alt text](images/image-2.png)
> **Warning**: Deleting transits may impact network connectivity. Verify dependencies before proceeding.
```yaml
catalyst_center_version: 3.1.3.0
catalyst_center_verify: false

fabric_transits:
  - sda_fabric_transits:
      - name: IP_Transit_AS200
      - name: SDA_Transit_1
      - name: BGP_Transit_1
```

---

#### Validate Configuration
> **Important**: Validate your input schema before executing the playbook to ensure all parameters are correctly formatted.  
Run the following command to validate your input file against the schema:  
```bash
yamale -s workflows/sda_fabric_transits/schema/sda_fabric_transits_workflow_schema.yml workflows/sda_fabric_transits/vars/sda_fabric_transits_workflow_inputs.yml
```

---

### Step 3: Deploy and Verify

**Deploy** your configuration to *Cisco Catalyst Center* and **verify** the changes.

1. **Deploy Configuration (Create/Update)**:  
   Run the playbook to apply the fabric transit configuration. Ensure the input file is validated before execution. Specify the input file path using the `--e` variable (`VARS_FILE_PATH`).  
   ```bash
   ansible-playbook -i inventory/demo_lab/hosts.yaml workflows/sda_fabric_transits/playbook/sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml > logs/transits.log -vvvvvv
   ```
   > **Note**: If an error occurs (e.g., invalid input, device not found, or API failure), the playbook will halt and display details. Check the `logs/transits.log` for troubleshooting.

2. **Deploy Configuration (Delete)**:  
   To delete fabric transits, use the delete playbook:
   ```bash
   ansible-playbook -i inventory/demo_lab/hosts.yaml workflows/sda_fabric_transits/playbook/delete_sda_fabric_transits_workflow_playbook.yml --e VARS_FILE_PATH=../vars/sda_fabric_transits_workflow_inputs.yml > logs/transits_delete.log -vvvvvv
   ```

3. **Verify Deployment**:  
   After execution, verify the configuration in the *Cisco Catalyst Center* UI under **Design > Network Settings > SDA Fabric Transits**. If `catalyst_center_debug` is enabled, review the logs for detailed operation information.  

   ![Fabric transit configuration in Cisco Catalyst Center UI](./images/image-1.png)  
   **Figure 1**: *Fabric Transit Configuration in Cisco Catalyst Center*

---

## Important Notes

### Transit Type Constraints
1. **IP-Based Transit**:
   - Cannot be updated after creation (ASN is immutable)
   - Requires unique ASN for each IP transit
   - Only BGP routing protocol is supported

2. **SDA LISP Pub/Sub Transit**:
   - Cannot be added to fabric sites using LISP/BGP control plane
   - Supports devices with IOS XE 17.6 or later
   - Supports up to 4 control plane devices
   - Multicast over transit can be enabled/disabled

3. **SDA LISP BGP Transit**:
   - Cannot be added to fabric sites using LISP Pub/Sub control plane
   - Supports up to 2 control plane devices
   - No multicast over transit option

### Site Hierarchy Support
- **Available**: Catalyst Center version 3.1.3.0 and later
- **Default**: If not specified, transit is assigned to "Global" (accessible across all sites)
- **Format**: Must follow existing site hierarchy (e.g., Global/Area/Building/Floor)
- **Validation**: Site must exist in Catalyst Center before transit creation

### Prerequisites
- Network devices must be provisioned and assigned to fabric sites
- Control plane devices must exist in fabric site or zone
- Ensure network connectivity between control plane devices
- Verify device compatibility (IOS XE versions for Pub/Sub transits)

### Best Practices
- Back up your configuration before running delete playbooks
- Validate input files using the schema validator before deployment
- Use `catalyst_center_debug: true` for troubleshooting
- Monitor task execution in Catalyst Center UI (Design > Tasks)
- Test configurations in non-production environment first

---

## References

**Environment Details**  
The following environment was used for testing:  

| **Component**         | **Version** |
|-----------------------|-------------|
| Python                | `3.10.10`    |
| Cisco Catalyst Center | `3.1.3.0`   |
| Ansible               | `9.9.0`     |
| cisco.dnac Collection | `6.29.0`    |
| dnacentersdk          | `2.9.2`     |

For detailed documentation, refer to:  
- [Ansible Galaxy: Cisco Catalyst Center Collection](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/sda_fabric_transits_workflow_manager)  
- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)

