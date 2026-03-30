# Catalyst Center Cisco Validated Playbooks
This repository provides Cisco-validated Ansible playbooks to automate Catalyst Center configurations, accelerating your network automation journey. 

# Table of Contents
- [Prerequisites](#prerequisites)
- [CompatibilityMatrix](#CompatibilityMatrix)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Update](#update)

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


# Installation of Cisco Validated Playbooks, Schema and Sample Inputs Vars

- Install Python 3.9 or later
- Install  cisco.dnac collection including Python requirements.
- Modify ansible.cfg file to support additional jinja2 extensions

## Python
    Python 3.9+ is required to install iac-validate. Don't have Python 3.9 or later? 
    See Python 3 Installation & Setup Guide https://realpython.com/installing-python/
    Create your python virtual environment using commend:
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
For installing or upgrading the cisco.dnac ansible collection follow steps:
    Install Collection from Ansible Galaxy
    These instructions are for regular users to install via Ansible Galaxy. The instructions also include installation of all Python requirements for a given version. 
    The cisco.dnac collection is available on the Ansible Galaxy server and can be automatically installed on your system using following command

### Latest version
Clone the dnacenter-ansible repository.
```bash
ansible-galaxy collection install cisco.dnac --force
```
### Sppecific version
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
Enable Jinja2 extensions: loopcontrols and do
[Jinja2 Extensions Documentation](https://jinja.palletsprojects.com/en/stable/extensions/)

By default, Ansible will issue a warning when a duplicate dict key is encountered in YAML. We recommend to change to error instead and stop playbook execution when a duplicate key is detected.
```bash
jinja2_extensions=jinja2.ext.loopcontrols,jinja2.ext.do
duplicate_dict_key=error
```

# Create your inventory
## Inventory:
This folder contains inventory file for your dev, lab, sandbox or production env which will be utilised by swim playbooks.

Create your inventory file in below template format to utilize the swim playbooks.

The template for the inventory file is:
```bash
cat inventory/demo_lab/001-dnac_inventory_template.yml
```

Setup up your ansible python interpretor following suitable method for your environment : https://docs.ansible.com/ansible/latest/reference_appendices/interpreter_discovery.html
    
### Hairarchical variable files for inputs

The second folder of the workflows contains playbook and var files for workflows.
Example:
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
    dnac_host: <Cisco Catalyst Center IP Address> #(Mandatory) Cisco Catalyst Center Ip address
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



