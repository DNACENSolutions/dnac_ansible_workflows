# Catalyst Center Device Software Image Management
## Overview

The SWIM protocol provides a standardized way to manage and upgrade software images on Cisco devices. This workflow leverages Ansible's automation capabilities to streamline the upgrade process, reducing manual effort and potential errors.

## Features

* **Automated Image Transfer:** The playbook automatically transfers the desired software image to the target Catalyst switch.
* **Image Activation:**  Activates the new image on the switch.
* **Reload (Optional):**  Optionally reloads the switch to complete the upgrade process.
* **Verification:** Verifies the software version after the upgrade.
* **Error Handling:** Includes error handling mechanisms to gracefully handle potential issues during the upgrade.

## Requirements

* **Ansible:**  A system with Ansible installed.
* **Network Connectivity:**  SSH connectivity to the target Catalyst switch.
* **Credentials:** Valid login credentials for the switch (username/password or SSH key).
* **Software Image:** The desired Cisco IOS XE software image file (.bin).

## Demo Video
[![Device Software Upgrade Demo](./swimdemo.png)](http://3.136.0.140/iac_demos/swim/SWIMDEMO.mp4)
