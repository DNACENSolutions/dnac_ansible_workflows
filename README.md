# DNAC Ansible Workflows

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
- Access to a Cisco DNA Center instance
- Proper network connectivity to interact with the Catalyst Center APIs


## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/DNACENSolutions/dnac_ansible_workflows.git


1. Navigate to the project directory:
    
    cd dnac_ansible_workflows

2. Install the required dependencies:

    pip install -r requirements.txt

3. Install the collection (Galaxy link):

    ansible-galaxy collection install cisco.dnac

4.  Create your inventory
    a. Inventory:
        This folder contains inventory file for your dev, lab, sandbox or production env which will be utilised by swim playbooks.
        
        Create your inventory file in below template format to utilize the swim playbooks.
        
        The template for the inventory file is:
            cat inventory/demo_lab/001-dnac_inventory_template.yml
    b. Hairarchical variable files for inputs

        The seconf folder workflows contains playbook and var files for workflows.
        Example:
            workflows/swim
            playbooks/
                swim.yml
                swim_image_upload_golden_tag.yml
                swim_image_distribution.yml
                swim_image_activation.yml
            vars/
                vars_swim.yml

6. Var files:
            Update var file with your  details and parameter to control playbook
7. Platbook: 
        The playbooks can be directly used without change when inventory and var files created in the above templates.

8. Executing playbook (Sample):

        ansible-playbook -i <inventory_dir> <playbook> --extra-vars VARS_FILES_PATH=<relative var files location> -vvvv
        
	Sample:

        ansible-playbook -i ./inventory_dnaccluster ./workflows/swim/playbook/swim.yml --extra-vars VARS_FILES_PATH=./../vars//input_swim.yml -vvvv

## Examples 
How to Generate your hosts inventory from DNAC using inventory_gen playbook:

For brownfield Catalyst Cennter (Network already discovered in Catalyst Center) with devices are in inventory, then automated inventory generation can be performed through inventory_gen playbook. Following the below Steps:

1. Create a basic inventory file with DNAC Inputs in inventory folder. for example demo_inv.yml
        #Inventory file for demo_lab
        dnachosts:
            hosts:
            dnac1:
            dnac_debug: false
            dnac_host: <DNAC IP Address> #(Mandatory) DNAC Ip address
            dnac_password: <DNAC UI admin Password> #(Mandatory) 
            dnac_port: 443 #(Mandatory) 
            dnac_username: <DNAC UI admin username> #(Mandatory) 
            dnac_verify: false #(Mandatory) 
            dnac_version: <DNAC Release version> #(Mandatory)  Example: 2.3.5.3

2. Run the workflows/inventory_gen/inventory_gen.yml playbook with thisinventory file with your DNAC cluster Inputs. From the code base execute:
        ansible-playbook -i ./inventory/demo_inv.yml ./workflows/inventory_gen/playbook/inventory_gen.yml  -vvvv
        #==============
        #For successful run you will see:
        #==============
        TASK [Yaml dump network device data with formatted output to file  inv_network_devices.yml] *************************************************************************************************************************************************************
        task path: ./workflows/inventory_gen/playbook/inventory_gen.yml:50

        ....
        PLAY RECAP **********************************************************************************************************************************************************************************************************************************************
        dnac1                      : ok=5    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   


3. The network_devices inventory is stored inventory_<clusterhostname>


Here are a few examples of Ansible workflows available in this repository:

Example 1: Swim upgrade, this include uploading the images, golden tagging the image filtered location and device family and distributed and activating images on the networkk devices. The filtering is controlled using var_file: input_swim.yml

    ansible-playbook -i ./inventory_dnaccluster ./workflows/swim/playbook/swim.yml --extra-vars VARS_FILES_PATH=./../vars/input_swim.yml -vvvv

Example 2: Create Sites, buildings floors using playbook : site_hierarchy.yml

    ansible-playbook -i ./inventory_dnaccluster ./workflows/sites/playbook/site_hierarchy.yml --extra-vars VARS_FILES_PATH=./../vars/input_design_sites.yml

Example 3: Create Global IP Pools, using playbooks create_update_global_ippools.yaml

    ansible-playbook -i ./inventory_dnaccluster ./workflows/ip_pools/playbook/create_update_global_ippools.yaml --extra-vars VARS_FILES_PATH=/vars/input_design_global_ip_pools.yml

Feel free to explore the playbooks/ directory for more examples and use cases.


## Update
Getting the latest/nightly collection build

Clone the dnacenter-ansible repository.
    git clone git@github.com:DNACENSolutions/dnac_ansible_workflows.git

Go to the dnacenter-ansible directory
    cd dnac_ansible_workflows

Pull the latest master from the repo
    git pull origin master

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

