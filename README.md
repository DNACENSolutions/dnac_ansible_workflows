# dnac_ansible_workflows
Sample workflows to automate DNAC configurations through cisco.dnac ansible workflow modules. This include Playbooks, Sample inputs and Sample Inventory files.

Version 0.0.1 (Beta)

#Setting env and running playbook
1. Source you python env:
    ```bash
        source <python-virtual-env>/bin/activate
      ```
2. Ansible must be installed
    ```bash
        sudo pip install ansible 
      ```
3. Python DNA Center SDK must be installed
    ```bash
        sudo pip install dnacentersdk 
      ```
4. Install the collection (Galaxy link)
    ```bash
        ansible-galaxy collection install cisco.dnac
    ```
    For more details refer: https://github.com/cisco-en-programmability/dnacenter-ansible

5. Checkout dnac_ansible_workflows project
    ```bash
    git clone git@github.com:DNACENSolutions/dnac_ansible_workflows.git

    cd dnac_ansible_workflows/
    ```

    The project contains 2 folders.
    a. Inventory:
        This folder contains inventory file for your dev, lab, sandbox or production env which will be utilised by swim playbooks.
        
        Create your inventory file in below template format to utilize the swim playbooks.
        
        The template for the inventory file is:
        ```bash
            cat inventory/demo_lab/001-dnac_inventory_template.yml
        ```
    b. The seconf folder workflows/swim contains playbook and var files for swim workflow.
    workflows/swim
    playbooks/
        swim.yml
        swim_image_upload_golden_tag.yml
        swim_image_distribution.yml
        swim_image_activation.yml
    vars/
        vars_swim.yml

6. Var files:
            Update var file with your image details and parameter to control swim upgrade.
7. Platbook: 
        The playbooks can be directly used without change when inventory and var files created in the above templates.

8. Executing playbook (Sample)
    ```bash
        ansible-playbook -i ./inventory/demo_lab/001-dnac_inventory.yml ./workflows/swim/playbook/swim.yml --extra-vars VARS_FILES_PATH=./../vars//input_swim.yml -vvvv
    ```
9. requirments.txt
   all dependent python modules can be installed using requirmennts.txt
    ```bash
        pip3 install -i requirements.txt 
    ```

How to Generate your hosts inventory from DNAC using inventory_gen playbook:
10. If the DNAc is already configured with devices and the devices are in inventory, then automated inventory generation can be done through inventory_gen playbook. Follow the below Steps:
i. Create a basic inventory file with DNAC Inputs in inventory folder. for example demo_inv.yml
  ---
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

ii. Run the workflows/inventory_gen/inventory_gen.yml playbook with thisinventory file with your DNAC cluster Inputs. From the code base execute:
    ```bash
        ansible-playbook -i ./inventory/demo_inv.yml ./workflows/inventory_gen/playbook/inventory_gen.yml  -vvvv
        
        ....
        #==============
        #For successful run you will see:
        #==============
TASK [Yaml dump network device data with formatted output to file  inv_network_devices.yml] *************************************************************************************************************************************************************
task path: ./workflows/inventory_gen/playbook/inventory_gen.yml:50

....
PLAY RECAP **********************************************************************************************************************************************************************************************************************************************
dnac1                      : ok=5    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

    ```
iii. The network_devices inventory is stored inv_network_devices.yml
iV. Copy you inv_network_devices.yml file to you inv directory.


Update
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

Code of Conduct

This collection follows the Ansible project's Code of Conduct. Please read and familiarize yourself with this document.

Releasing, Versioning and Deprecation:
 Version (Beta) : More enhancement might follow based on usage feedback

