# Device Credential Workflow Manager
Device Credential Workflow Manager in Cisco DNA Center is a tool that helps you organize and manage network device credentials, including creating, applying, and updating credentials for network devices during deployment or maintenance.

You can configure and manage credentials for network devices such as switches, routers, access points, and other devices, ensuring that Cisco DNA Center has access and can manage them automatically.

These workflows help you reduce risk and enhance security while managing your network. Below are the key elements and processes in Device Credential Workflow Manager.

Device Credentials Figure: It consists of two parts: Network Hierarchy and Manage Credentials.
![Alt text](./images/credential.png)

Network Hierarchy: specifies where the credential will be applied on
Manage Credentials:
- CLI: Connect and manage devices via command line (SSH/Telnet).
- SNMPv2c Read: Read device status information via SNMPv2c.
- SNMPv2c Write: Both read and change configuration via SNMPv2c.
- SNMPv3: Secure SNMP version, supporting encryption and authentication.
- HTTP(S) Read: Read device information via HTTP or HTTPS protocol.
- HTTP(S) Write: Change device configuration via HTTP or HTTPS protocol.

## Purpose

### Centralized Credential Management 

- Streamline the process of adding, updating, and deleting device credentials from a single location.

### Improved Security 

- Reduce the risk of unauthorized access by ensuring credentials are securely stored and managed.

### Workflow Automation 

- Simplify credential management tasks with an automated workflow, saving time and minimizing errors.

## Compatibility

### Cisco DNA Center 

- 2.3.3.0 and above

### Ansible 

- Latest stable version recommended

## Procedure

1. ### Prepare your Ansible environment

  - Install Ansible if you haven't already
  - Ensure you have network connectivity to your Catalyst Center instance.
  - Checkout the project and playbooks:
  >git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

2. ### Configure Host Inventory

- Update hosts.yml (or your preferred inventory file) with the connection details for your DNA Center instance.
 - The **host_inventory_dnac1/hosts.yml** file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.

```yaml
---
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
3. ### Workflow Details and Generate your Input
The workflow utilizes the **device_credential_workflow_manager** module to interface with DNA Center's credential management APIs. For a comprehensive guide on the available options and their structure, please refer to the full workflow specification: [full workflow specification](https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/device_credential_workflow_manager). The following operations are supported:

- **Add Device Credential:** 

  **Purpose**:
  - Create new device credentials.
  - Make sure this device credential does not already exist in DNA Center.

  **Input example with creating cli credential**:

  ```yaml
  ---
  catalyst_center_version: 2.3.7.6
  device_credentials:
    credentials_details: #Create multiple credentials for the same protocol
    - global_credential_details: #Create global credentials for the device list
        cli_credential: #Create CLI credentials list
        - description: CLI Sample 1
          username: cli-1
          password: "5!meh"
          enable_password: "q4^t^"
        - description: CLI2
          username: cli-2
          password: "sbs2@"
          enable_password: "8b!rn"
  ```

- **Update Device Credential:**

  **Purpose**:
  - Modify existing credentials (e.g., change passwords).
  - This task ensures that if the credential already exists, the details of that credential will be updated without creating a duplicate.

  **Input example with update cli credential**:

  ```yaml
  ---
  catalyst_center_version: 2.3.7.6
  device_credentials:
    credentials_details: 
    - global_credential_details: 
        cli_credential:
        - description: CLI Sample 1
          username: cli-1
          password: "5!meh"
          enable_password: "q4^t^"
        - description: CLI2
          username: cli-2
          password: "sbs2@"
          enable_password: "8b!rn"
  ```

  **Input example with update device credential name/description using old name and description**:

  ```yaml
  ---
  catalyst_center_version: 2.3.7.6
  device_credentials:
    credentials_details:
    - global_credential_details:
        cli_credential:
        - description: CLISample1
          username: cli1
          password: "5!meh"
          enable_password: "q4^t^"
          old_description: CLI Sample 1
          old_username: cli-1
  ```

- **Delete Device Credential:**
  **Purpose**:
    - Remove credentials from DNA Center.
    - Make sure that the device credentials you delete are not assigned to any site.

  **Input example with delete cli credential**:

  ```yaml
  ---
  catalyst_center_version: 2.3.7.6
  device_credentials:
    credentials_details:
    - global_credential_details:
        cli_credential:
        - description: CLI Sample 1
          username: cli-1
  ```

- **Assign or Update Credentials to Sites:**

  **Purpose**:
    - Assign clredentials to sites.
    - Update new credentials to sites. 

  **Input example for Assign Credentials to sites**:

    ```yaml
    ---
    catalyst_center_version: 2.3.7.6
    device_credentials:
      credentials_site_assignment: #Assign credentials to sites list of all sites mappings
      - assign_credentials_to_site: # Assign device credentials to sites
          cli_credential: #Assign CLI credentials to sites
            description: CLI Sample 1
            username:  cli-1
          site_name: #Sites  to which the credentials are assigned
          - Global/India #Full Site Heirarchy Path from Global to Site
          - Global/India/Bangalore
    ```

- **Apply Credentials:**

  **Purpose**:
    - Make update to creedentials, i.e. reset passsword etc and Apply to applicable sites and all the devices on that site.

  **Input example for Apply Credentials to sites**:

    ```yaml
    ---
    catalyst_center_version: 2.3.7.6
    device_credentials:
      credentials_site_apply:
      - apply_credentials_to_site:
          cli_credential:
            description: CLI Sample 1
            username:  cli-1
          site_name:
          - Global/India #Full Site Heirarchy Path from Global to Site
          - Global/India/Bangalore
    ```

4. ### Validate Input:(recommended)

Validate the input with schema using yamale
- Command to Validate:

```bash
yamale -s workflows/device_credentials/schema/device_credentials_schema.yml workflows/device_credentials/vars/device_credentials_vars.yml
```

- Result:
```bash
Validating /Users/pawansi/dnac_ansible_workflows/workflows/device_credentials/vars/device_credentials_vars.yml...
Validation success! 👍
```

## Example run

- Collect device running configurations through Catalyst Center APIs.

```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_credentials/playbook/device_credentials_playbook.yml --e VARS_FILE_PATH=../vars/device_credentials_vars.yml -vvvv
```

## running through Jinja template with credentials picked up from ansible Vault
You can define your input as  jinja template where you can use the variables from ansible vault and run using the same playbooks

Defining the jinja template example: workflows/device_credentials/jinja_template/device_credentials_template.j2

while defining the template maintain the structure and the variable name: device_credentials: which is a dictionary having two keys: credentials_details and credentials_site_assignment and follow the workflow spec for the rest as below example.

```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
device_credentials:
  credentials_details: #Create multiple credentials for the same protocol
  - global_credential_details: #Create global credentials for the device list
      cli_credential: #Create CLI credentials list
      - description: switchandwlc credentials
        username: wlcaccess
        password: {{ wlcaccess_password }}
        enable_password: {{ wlcaccess_enable_password }}
      snmp_v3: #Create SNMPv3 credentials list
      - description: snmpV3 Sample 1 
        auth_password: {{ snmpV3_Sample_1_auth_password }}
        auth_type: SHA
        snmp_mode: AUTHPRIV
        privacy_password: {{ snmpV3_Sample_1_privacy_password }}
        privacy_type: AES128
        username: admin
      https_read: #Create HTTPS Read credentials list
      - description: httpsRead Sample 1
        username: admin
        password: {{ httpsRead_Sample_1_password }}
        port: 443
      https_write: #Create HTTPS Write credentials list
      - description: httpsWrite Sample 1
        username: admin
        password: {{ httpsWrite_Sample_1_password }}
        port: 443
  credentials_site_assignment: #Assign credentials to sites list of all sites mappings
  - assign_credentials_to_site: # Assign device credentials to sites
      cli_credential: #Assign CLI credentials to sites
        description: switchandwlc credentials
        username:  wlcaccess
      snmp_v3: #Assign SNMPv3 credentials to sites
        description: snmpV3 Sample 1 
        username: admin
      https_read: #Assign HTTPS Read credentials to sites
        username: admin
        description: httpsRead Sample 1
      https_write: #Assign HTTPS Write credentials to sites
        username: admin
        description: httpsWrite Sample 1
      site_name: #Sites  to which the credentials are assigned
        - Global/USA
```
### Create playbook input file which contains path to jinja template
Create file jinja_template_device_credentials_input.yml (example name)
```yaml
---
#Select Catalyst Cennter version, this one overwrite the default version from host file
catalyst_center_version: 2.3.7.6
catalyst_center_verify: false
jinjatemplate: true
#Provide the path to the jinja template file
jinjatemplate_file: ../jinja_template/device_credentials_template.j2
# device_credentials could be empty or have a list of device credentials, if jinjatemplate  is true device_credentials value is taken from jinja template
device_credentials: []
```

The variables used in the template should be already added to ansible vault. 
Refer workflow ansible_vault_update workflow to add the variable to your ansible vault.

## Execute credentials with jinja template:
```bash
ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/device_credentials/playbook/device_credentials_playbook.yml --e VARS_FILE_PATH=../vars/jinja_template_device_credentials_input.yml -vvvv
```


## Important Notes:
- Ensure the Catalyst Center version is compatible.
- Carefully configure inventory and input variables.
- Validate input using yamale to prevent errors.
- Review execution logs for troubleshooting.