[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/DNACENSolutions/dnac_ansible_workflows)
[![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/codeexchange/devenv/DNACENSolutions/dnac_ansible_workflows/)
# dnac_ansible_workflows
Sample workflows to automate Cisco Catalyst Center configurations through cisco.dnac ansible workflow modules. This include Playbooks, Sample inputs and Sample Inventory files.

![DNAC Ansible Workflows](https://github.com/DNACENSolutions/dnac_ansible_workflows)

This repository contains a collection of Ansible workflows for automating Catalyst Center workflows. These workflows help streamline network provisioning, configuration, and management by leveraging the power of Ansible automation.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Update](#update)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before using these Ansible workflows, ensure that you have the following prerequisites:

- Ansible installed on your machine
- Access to a Cisco Catalyst Center instance
- Proper network connectivity to interact with the Catalyst Center APIs


## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/DNACENSolutions/dnac_ansible_workflows.git
   ```


1. Navigate to the project directory:
    
    ```bash
    cd dnac_ansible_workflows
    ```
2. Install the required dependencies:
   ```bash
    pip install -r requirements.txt
    ```
3. Install the collection (Galaxy link):
    ```bash
    ansible-galaxy collection install cisco.dnac:6.11.0 --force
    ```
4.  Create your inventory
    a. Inventory:
     This folder contains inventory file for your dev, lab, sandbox or production env which will be utilised by swim playbooks.
     
     Create your inventory file in below template format to utilize the swim playbooks.
     
     The template for the inventory file is:
     ```bash
         cat inventory/demo_lab/001-dnac_inventory_template.yml
     ```
    b. Hairarchical variable files for inputs

        The second folder of the workflows contains playbook and var files for workflows.
        Example:
            workflows/swim
            playbooks/
                swim_workflow_playbook.yml
            vars/
                vars_swim.yml

6. Var files:
            Update var file with your  details and parameter to control playbook
7. Playbook: 
        The playbooks can be directly used without any change when inventory and var files created in the above templates.

8. Executing playbook (Sample):

How to Generate your hosts inventory from Cisco Catalyst Center using inventory_gen playbook:

For brownfield Catalyst Cennter (Network already discovered in Catalyst Center) with devices are in inventory, then automated inventory generation can be performed through inventory_gen playbook. Following the below Steps:

i. Create a basic inventory file with Cisco Catalyst Center Inputs in inventory folder. for example demo_inv.yml
  ---
    ```bash
        #Inventory file for demo_lab
        catalyst_cennter_hosts:
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


Here are a few examples of Ansible workflows available in this repository:

Example 1: Swim upgrade, this include uploading the images, golden tagging the image filtered location and device family and distributed and activating images on the networkk devices.
    
```bash
 ansible-playbook -i ./inventory_dnaccluster ./workflows/swim/playbook/swim_workflow_playbook.yml --extra-vars VARS_FILE_PATH=< Vars File PATH (Full Path or relative path from playbook)> -vvvv
```
    
Example 2: Create Sites, buildings floors using playbook : workflows/sites/playbook/site_hierarchy_playbook.yml
    
```bash
 ansible-playbook -i ./inventory_dnaccluster ./workflows/sites/playbook/site_hierarchy_playbook.yml --extra-vars VARS_FILES_PATH=./../vars/site_hierarchy_design_vars_.yml
```
    
Feel free to explore the playbooks/ directory for more examples and use cases.


## Update
Getting the latest/nightly collection build

Clone the dnacenter-ansible repository.
```bash
 git clone git@github.com:DNACENSolutions/dnac_ansible_workflows.git
```
    
Go to the dnacenter-ansible directory
```bash
 cd dnac_ansible_workflows
```
    
Pull the latest master from the repo
```bash
    git pull origin master
```
    
## Contributing
Contributions are welcome! To contribute to this project, follow these steps:

    Fork the repository.
    Create a new branch for your feature or bug fix.
    Make your changes and commit them with descriptive commit messages.
    Push your changes to your fork.
    Submit a pull request to the main branch of this repository.

Code of Conduct

This collection follows the Ansible project's Code of Conduct. Please read and familiarize yourself with this document.

Releasing, Versioning and Deprecation:
 Version (Beta) : More enhancement might follow based on usage feedback

