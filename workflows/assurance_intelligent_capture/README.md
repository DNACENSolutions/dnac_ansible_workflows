# Cisco Catalyst Center Assurance Intelligent Capture (ICAP) Workflow Playbooks

This resource module enables automated management of Assurance Intelligent Capture (ICAP) settings in Cisco Catalyst Center. It supports creating, deploying, and downloading ICAP packet captures for troubleshooting and assurance workflows. The module is designed for efficient, programmatic control of ICAP settings and packet capture retrieval.

Key features include:

- **ICAP Session Management:**  
  - Create and deploy ICAP (Intelligent Capture) sessions for onboarding, full, OTA, RF statistics, and anomaly captures.
  - Specify capture parameters such as client MAC, AP, WLC, slot, OTA band, channel, and duration.
  - Download PCAP files for offline analysis.

- **Automated Troubleshooting:**  
  - Automate the collection of packet captures for client onboarding and wireless troubleshooting.
  - Integrate with assurance workflows for rapid root cause analysis.

- **Validation and Logging:**  
  - Validate configuration and deployment status.
  - Download and verify PCAP files to a specified directory.

**Version Added:**  `6.31.0`

---

## Workflow Steps

This workflow typically involves the following steps:

### Step 1: Install and Generate Inventory

Before running the playbooks, ensure you have Ansible installed and the necessary Cisco Catalyst Center collection.

1. **Install Ansible:**  
   Follow the official Ansible documentation for installation instructions.

2. **Install Cisco Catalyst Center Collection:**
   ```bash
   ansible-galaxy collection install cisco.dnac
   ```

3. **Generate Inventory:**  
   Create an Ansible inventory file (e.g., `inventory.yml`) that includes your Cisco Catalyst Center appliance details.
   ```yaml
   catalyst_center_hosts:
     hosts:
       your_catalyst_center_instance_name:
         catalyst_center_host: xx.xx.xx.xx
         catalyst_center_username: admin
         catalyst_center_password: XXXXXXXX
         catalyst_center_port: 443
         catalyst_center_verify: false # Set to true for production with valid certificates
         catalyst_center_version: 2.3.7.9
         catalyst_center_log: true
   ```

---

### Step 2: Define Inputs and Validate

Prepare the input data for creating or managing ICAP settings and downloads.

1. **Define Input Variables:**  
   Create variable files (e.g., `vars/assurance_icap_inputs.yml`) that define the desired state of your ICAP settings, including details for creation and download.

#### Schema for Assurance ICAP Workflow

| **Parameter** | **Type** | **Required** | **Description** |
|---------------|----------|--------------|-----------------|
| `config`      | List     | Yes          | List of assurance operations to perform. |
| `state`       | Str      | Yes          | Desired state: `merged` (create/deploy/download). |

##### ICAP Settings (`assurance_icap_settings`)

| **Parameter**         | **Type** | **Required** | **Description** |
|-----------------------|----------|--------------|-----------------|
| `capture_type`        | String   | Yes          | Type of capture: FULL, ONBOARDING, OTA, RFSTATS, ANOMALY. |
| `duration_in_mins`    | Int      | Yes          | Duration of the capture session in minutes. |
| `preview_description` | String   | No           | Description of the capture session. |
| `client_mac`          | String   | Yes          | MAC address of the client device. |
| `wlc_name`            | String   | No           | Name of the Wireless LAN Controller. |
| `ap_name`             | String   | No           | Name of the Access Point. |
| `slot`                | List[Int]| No           | List of slot numbers. |
| `ota_band`            | String   | No           | OTA band: 2.4GHz, 5GHz, 6GHz. |
| `ota_channel`         | Int      | No           | OTA channel number. |
| `ota_channel_width`   | Int      | No           | Channel width in MHz. |

##### ICAP Download (`assurance_icap_download`)

| **Parameter**         | **Type** | **Required** | **Description** |
|-----------------------|----------|--------------|-----------------|
| `capture_type`        | String   | Yes          | Type of capture to download. |
| `client_mac`          | String   | Yes          | MAC address of the client device. |
| `ap_mac`              | String   | No           | MAC address of the AP (required for OTA/ANOMALY). |
| `start_time`          | String   | No           | Start time (YYYY-MM-DD HH:MM:SS). |
| `end_time`            | String   | No           | End time (YYYY-MM-DD HH:MM:SS). |
| `file_path`           | String   | Yes          | Directory to save the downloaded PCAP file. |

---

#### Example Input File

Below are example input files for each `capture_type` supported by the ICAP workflow. You can use these as templates for your own automation.

---

**1. ONBOARDING Capture**

```yaml
  - assurance_icap_settings:
      - capture_type: ONBOARDING
        preview_description: "Onboarding troubleshooting session"
        duration_in_mins: 15
        client_mac: 00:11:22:33:44:55
        wlc_name: WLC-1.cisco.local
state: merged
```

---

**2. FULL Capture**

```yaml
  - assurance_icap_settings:
      - capture_type: FULL
        preview_description: "Full traffic capture for deep analysis"
        duration_in_mins: 20
        client_mac: AA:BB:CC:DD:EE:FF
        wlc_name: WLC-2.cisco.local
state: merged
```

---

**3. OTA (Over-the-Air) Capture**

```yaml
  - assurance_icap_settings:
      - capture_type: OTA
        preview_description: "OTA capture for Wi-Fi troubleshooting"
        duration_in_mins: 10
        client_mac: 12:34:56:78:9A:BC
        ap_name: AP-1.cisco.local
        slot: [1]
        ota_band: 5GHz
        ota_channel: 36
        ota_channel_width: 40
state: merged
```

---

**4. RFSTATS Capture**

```yaml
  - assurance_icap_settings:
      - capture_type: RFSTATS
        preview_description: "RF statistics capture"
        duration_in_mins: 5
        client_mac: 98:76:54:32:10:FE
        ap_name: AP-2.cisco.local
        slot: [0]
        ota_band: 2.4GHz
state: merged
```

---

**5. ANOMALY Capture**

```yaml
  - assurance_icap_settings:
      - capture_type: ANOMALY
        preview_description: "Anomaly detection capture"
        duration_in_mins: 12
        client_mac: 01:23:45:67:89:AB
        ap_name: AP-3.cisco.local
        slot: [1]
        ota_band: 6GHz
        ota_channel: 5
        ota_channel_width: 20
state: merged
```

---

**Download ICAP PCAP File Example**

```yaml
  - assurance_icap_download:
      - capture_type: OTA
        client_mac: 12:34:56:78:9A:BC
        ap_mac: 00:AA:BB:CC:DD:EE
        start_time: "2025-06-01 09:00:00"
        end_time: "2025-06-01 09:10:00"
        file_path: /Users/youruser/Downloads
state: merged
```

> **Note:**  
> - For `OTA` and `ANOMALY` capture types, `ap_name` (for creation) and `ap_mac` (for download) are required.
> - Adjust `duration_in_mins`, MAC addresses, and device names as needed for your environment.

#### Validate Configuration

Important: Validate your input schema before executing the playbook to ensure all parameters are correctly formatted.
Run the following command to validate your input file against the schema:

```bash
./tools/validate.sh -s ./workflows/assurance_intelligent_capture/schema/assurance_intelligent_capture_schema.yml -d ./workflows/assurance_intelligent_capture/vars/assurance_intelligent_capture_inputs.yml
```

---

### Step 3: Deploy and Verify

1. **Deploy Configuration:**  
   Run the playbook to apply the ICAP configuration and/or download packet captures:

   ```bash
   ansible-playbook -i ./inventory/hosts.yml workflows/assurance_intelligent_capture/playbook/assurance_intelligent_capture_playbook.yml --e VARS_FILE_PATH=../vars/assurance_intelligent_capture_inputs.yml -vvvv
   ```

2. **Verify Deployment:**  
   After executing the playbook, check the Catalyst Center UI for ICAP session status. If `catalyst_center_log` is enabled, review the logs for detailed information. For downloads, verify the PCAP file exists in the specified directory.

---


### References

*Note: The environment used for the references in the above instructions is as follows:*

```yaml
python: 3.12.0
dnac_version: 2.3.7.9
ansible: 9.9.0
cisco.dnac: 6.32.0
dnacentersdk: 2.8.8
```

For detailed information on the assurance ICAP workflow, refer to the following documentation:  
https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/assurance_icap_settings_workflow_manager/