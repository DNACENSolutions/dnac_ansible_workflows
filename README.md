# catalyst-center-ansible-iac
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/DNACENSolutions/dnac_ansible_workflows)
[![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/codeexchange/devenv/DNACENSolutions/dnac_ansible_workflows/)
![Catalyst Center Cisco Validated Ansible Playbooks Official](https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git)

# Catalyst Center Cisco Validated Playbooks
This repository provides Cisco-validated Ansible playbooks to automate Catalyst Center configurations, accelerating your network automation journey. It includes:

## Ready-to-use playbooks
Streamline Catalyst Center provisioning with ready-to-use Ansible playbooks. Automate configurations and simplify network management tasks.

## Input validation schemas
Yamale-based input validation schemas ensure user input accuracy for the playbooks by validating user input before execution. This significantly reduces the potential for human error and ensures consistent, reliable results. Prevent costly mistakes and maintain configuration integrity with automated input checks.

## Comprehensive guides
Comprehensive guides provide detailed instructions and practical examples for various Catalyst Center configuration use cases. Learn how to deploy, update, and maintain your network infrastructure with step-by-step guidance and best practices. These resources empower you to effectively manage your network throughout its lifecycle.

## Sample inputs
Jumpstart your automation journey with sample input files that demonstrate proper formatting and supported values. Quickly create your own input configurations by adapting these examples, saving time and reducing errors. Use these pre-populated templates as a foundation for customizing your Catalyst Center deployments.

## Sample Jinja-based templates
Enhance scalability and flexibility with Jinja-based templates support. These templates empower you to dynamically generate input configurations, adapting to various deployments with ease. Simplify complex configurations and streamline repetitive tasks by leveraging the power of Jinja templating within your Ansible playbooks.

### Embrace infrastructure as code and manage your entire Catalyst Center configuration through Git. This repository provides the tools and guidance to make Git your single source of truth, ensuring:

- Complete version control: Track every change and easily revert to previous states.
- Increased collaboration: Simplify teamwork with a centralized and transparent platform.
- Improved reliability: Reduce errors and ensure consistent configurations across your network.
- Simplified deployments: Automate updates and rollbacks with confidence.

# Enterprise Usecases
![Enterprise Usecases](./images/enterpriseUsecases.png)

# Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Update](#update)
- [Contributing](#contributing)
- [License](#license)
- [Cisco Validated Playbooks](#cisco-validated-playbooks)

# Cisco Validated Playbooks

## Day 0 Configurations (Access and Integrations)
- [Catalyst Center Role Based Access Control and Users Management](./workflows/users_and_roles/README.md)
- [Catalyst Center ISE and AAA Servers Integration](./workflows/ise_radius_integration/#readme)

## Day 1 Configurations (Design and Discovery)
- [Catalyst Center Site Hierarchy and Floor Maps design](./workflows/site_hierarchy/#readme)
- [Catalyst Center Device Credentials configurations and assignment](./workflows/device_credentials/#readme)
- [Catalyst Center Network Settings (Servers, Banners, TZ, SNMP, Logging, Telemetry Management](./workflows/network_settings/#readme)
- [Catalyst Center Network Settings Global IP Address Pools and Site IP Address Pools reservation Management](./workflows/network_settings/#readme)
- [Catalyst Center Network Settings Wireless Design Management](./workflows/wireless_design/#readme)
- [Catalyst Center Wireless Network Profile Management](./workflows/network_profile_wireless/#readme) 
- [Catalyst Center Network Profile Switching Management](./workflows/network_profile_switching/#readme)
- [Catalyst Center Devices Discovery](./workflows/device_discovery/#readme)
- [Catalyst Center Device Inventory and device management](./workflows/inventory#readme)
- [Catalyst Center Plug and Play Device Onboarding](./workflows/plug_and_play/README.md)
- [Catalyst Center Device Provisioning and Re-Provisioning Management](./workflows/provision/README.md)
- [Catalyst Center Design and Deploy Device Templates](./workflows/device_templates/README.md)

## Day 2 Configurations (Underlay automation and SD Access fabric)
- [Catalyst Center Underlay Automation (LAN Automation) Management](./workflows/lan_automation/#readme)
- [Catalyst Center SDA Fabric Site and Fabric Zones](./workflows/sda_fabric_sites_zones/README.md)
- [Catalyst Center SDA Fabric Transits (IP transit and SDA Transit) Management](./workflows/sda_fabric_transits/README.md)
- [Catalyst Center Virtual Networks and L3 Anycast Gateways and L2 VLANs Management](./workflows/sda_virtual_networks_l2l3_gateways/README.md)
- [Catalyst Center SDA Fabric Device assignment to fabric sites and zones](./workflows/sda_fabric_device_roles/README.md)
- [Catalyst Center SDA Fabric Devices and Host Onboarding](./workflows/sda_hostonboarding/README.md)
- [Catalyst Center SDA Extranet Policies Management](./workflows/sda_fabric_extranet_policy/README.md)
- [Catalyst Center Application Policy Management](./workflows/application_policy/README.md)

## Day N Operation (Software Upgrade, Compliance, Events, Provisioning, backups and Assurance)
- [Catalyst Center Devices Software image management (SWIM)](./workflows/swim/README.md)
- [Catalyst Center Device compliance and remediation management](./workflows/network_compliance/README.md)
- [Catalyst Center Notification Destination and Events Subscription](./workflows/events_and_notifications/README.md)
- [Catalyst Center Devices Replacement Management](./workflows/device_replacement_rma/README.md)
- [Catalyst Center Access Point Provisioning and Access Point Configuration Management](./workflows/accesspoints_configuration_provisioning/README.md)
- [Device Configuration Customization using Catalyst Center Templates](./workflows/device_templates/README.md)
- [Catalyst Center managed network devices configurations backup management](./workflows/device_config_backup/README.md)
- [Catalyst Center Assurance Health Score KPIs settings and thresholds management](./workflows/assurance_health_score/README.md)
- [Catalyst Center Assurance Path Trace Management](./workflows/assurance_pathtrace/README.md)
- [Catalyst Center Assurance Network Health Management](./workflows/assurance_network_health/README.md)
- [Catalyst Center Assurance issues and events management](./workflows/assurance_issues_management/README.md)
- [Catalyst Center Assurance ICAP Management](./workflows/assurance_intelligent_capture/README.md)

## Demo Videos
[IaC Demo Videos](http://3.136.0.140/index.html)

# CompatibilityMatrix
| Deployed Catalyst Center Version   | Catalyst Center Version in Input   | Ansible Galaxy collection (cisco.dnac)Version    | Python SDK (dnacentersdk) Version    |
| :--------------------------------: | :--------------------------------: | :-----------------------: | :-------------------: |
| 2.3.5.3 | 2.3.5.3   | latest   | latest |
| 2.3.5.5 | 2.3.5.3   | latest   | latest |
| 2.3.5.6 | 2.3.5.3   | latest   | latest |
| 2.3.7.6 | 2.3.7.6   | latest   | latest |
| 2.3.7.7 | 2.3.7.6   | latest   | latest |
| 2.3.7.9 | 2.3.7.9   | latest   | latest |

# Released Versions
v2.3.7.6.1

# Prerequisites
Before using these Ansible workflows, ensure that you have the following prerequisites:

- Ansible installed on your machine
- Access to a Cisco Catalyst Center instance
- Proper network connectivity to interact with the Catalyst Center APIs

# Installation
Follow these steps to install the Cisco Validated Playbooks, Schema, and Sample Input Variables:

- Install Python 3.9 or later
- Install  cisco.dnac collection including Python requirements.
- Modify ansible.cfg file to support additional jinja2 extensions

## Python
    Python 3.9+ is required to install iac-validate. Don't have Python 3.9 or later? 
    See Python 3 Installation & Setup Guide https://realpython.com/installing-python/
    Create your python virtual environment using command below:
```bash
python3 -m venv python3env --prompt "AnsiblePython3 VENV"
source python3env/bin/activate
```

## Ansible Requirements
1. Clone this repository to your local machine:

```bash
git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git
```
Cloning a released version:
```bash
git clone --depth 1 --branch v2.3.7.6.1 https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git
```

## Navigate to the project directory:    
```bash
cd dnac_ansible_workflows
```

## Install the required dependencies:
```bash
pip install -r requirements.txt
```
## Install the collection (Galaxy link):
For installing or upgrading the cisco.dnac Ansible collection, follow these steps: Install Collection from Ansible Galaxy These instructions are for regular users to install via Ansible Galaxy. The instructions also include installation of all Python requirements for a given version. The cisco.dnac collection is available on the Ansible Galaxy server and can be automatically installed on your system using the following command:

### Latest version
Clone the dnacenter-ansible repository.
```bash
ansible-galaxy collection install cisco.dnac --force
```
### Specific version
```bash
ansible-galaxy collection install cisco.dnac:==6.29.0 --force
```

### Install latest devel version from  GitHub abd build
```bash
git clone https://github.com/cisco-en-programmability/dnacenter-ansible.git
```
Go to the dnacenter-ansible directory
```bash
cd dnacenter-ansible
```
Pull the latest master from the repo
```bash
git pull origin master
```
Build and install a collection from source
```bash
ansible-galaxy collection build --force
ansible-galaxy collection install cisco-dnac-* --force
```

## Install or Update the dnacentersdk:
For installing or upgrading the dnacentersdk follow steps:

### Install via pip or pip3
To get the Python Catalyst Center SDK latest in a fresh development environment:

```bash
pip install dnacentersdk
```

### Upgrading to the latest Version
Use --upgrade opton to upgrde to latest version available.
```bash
pip install dnacentersdk --upgrade
```
### Install a specific version
To install a specific version like 2.8.3
```bash
pip install dnacentersdk:2.8.3
```

## Ansible configuration file
Enable Jinja2 extensions: loopcontrols and do Jinja2 Extensions Documentation

By default, Ansible will issue a warning when a duplicate dict key is encountered in YAML. We recommend changing to error instead and stopping playbook execution when a duplicate key is detected.

```bash
jinja2_extensions=jinja2.ext.loopcontrols,jinja2.ext.do
duplicate_dict_key=error
```

# Create your inventory
## Inventory:
This folder contains inventory files for your dev, lab, sandbox, or production environments which will be utilized by SWIM playbooks.

Create your inventory file in the template format below to utilize the SWIM playbooks.

The template for the inventory file is:
```bash
cat inventory/demo_lab/001-dnac_inventory_template.yml
```

Set up your Ansible Python interpreter following a suitable method for your environment: https://docs.ansible.com/ansible/latest/reference_appendices/interpreter_discovery.html


    
### Hairarchical variable files for inputs

The second folder of the workflows contains playbook and var files for workflows. Example:

```bash
workflows/swim
playbooks/
    swim_workflow_playbook.yml
vars/
    vars_swim.yml
```
### Var files:
    Update var file with your  details and parameter to control playbook

### Playbook: 
    The playbooks can be directly used without any change when inventory and var files created in the above templates.

# Executing playbook (Sample):

## Create a basic inventory file with Cisco Catalyst Center Inputs in inventory folder. for example demo_inv.yml
```yaml
---
#Inventory file for demo_lab
catalyst_center_hosts:
    hosts:
    <dnac hostname >:
    dnac_debug: false
    dnac_host: <Cisco Catalyst Center IP Address> #(Mandatory) Cisco Catalyst Center IP Address
    dnac_password: <Cisco Catalyst Center UI admin Password> #(Mandatory) 
    dnac_port: 443 #(Mandatory) 
    dnac_username: <Cisco Catalyst Center UI admin username> #(Mandatory) 
    dnac_verify: false #(Mandatory) 
    dnac_version: <Cisco Catalyst Center Release version> #(Mandatory)  Example: 2.3.5.3
```

Here are a few examples of Cisco Validated Playbooks in the repo. For details documentation of the playbook usage refer the guide inside the corresponding module.

## Example 1: 
Swim upgrade, this include uploading the images, golden tagging the image filtered location and device family and distributed and activating images on the networkk devices.
```bash
ansible-playbook -i ./inventory_dnaccluster ./workflows/swim/playbook/swim_workflow_playbook.yml --extra-vars VARS_FILE_PATH=< Vars File PATH (Full Path or relative path from playbook)> -vvvv
```
    
## Example 2: 
Create Sites, buildings floors using playbook : workflows/sites/playbook/site_hierarchy_playbook.yml
    
```bash
 ansible-playbook -i ./inventory_dnaccluster ./workflows/sites/playbook/site_hierarchy_playbook.yml --extra-vars VARS_FILE_PATH=./../vars/site_hierarchy_design_vars_.yml
```
    
Feel free to explore the playbooks/ directory for more examples and use cases.

# Attention macOS users:

If you're using macOS you may receive this error when running your playbook:
```bash
objc[34120]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called.
objc[34120]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called. We can't safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
ERROR! A worker was found in a dead state
```

If that's the case try setting this environment variable:
```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

# Update
Getting the latest/nightly collection build

Clone the Catalyst Center ansible IaC repository if not already cloned.
```bash
git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git
```
    
Go to the dnacenter-ansible directory
```bash
cd catalyst-center-ansible-iac
```
    
Pull the latest master from the repo
```bash
git pull origin master
```

# Raising an issue or enhancement request
- Visit the Catalyst Center Ansible repository: https://github.com/cisco-en-programmability/catalyst-center-ansible-iac/issues
- Click the "New Issue" button.
- Carefully follow the provided issue template, ensuring you include:
- - A clear and concise description of the problem
- - Steps to reproduce the issue.
- - Relevant code snippets or configurations, playbook, variable files.
- - Expected behavior vs. actual behavior.
- - Catalyst Center and Ansible versions you're using.

# Contributing
Contributions are welcome! To contribute to this project, follow these steps:
    Fork the repository.
    Create a new branch for your feature or bug fix.
    Make your changes and commit them with descriptive commit messages.
    Push your changes to your fork.
    Submit a pull request to the main branch of this repository.

# Code of Conduct
This collection follows the Ansible project's Code of Conduct. Please read and familiarize yourself with this document.

# Releasing, Versioning and Deprecation:
 Version (Beta) : More enhancement might follow based on usage feedback
