# Network Design Site Hierarchy Playbook

You can create a network hierarchy that represents your network's geographical locations. The hierarchical organization enables you to easily apply design settings or configurations to a specific hierarchical element. For example, you can apply design settings to an entire area or to only a floor.

You can name hierarchical elements to help you identify where to apply design settings later.

The hierarchical elements that you can create have rules that dictate under which elements they can reside and which elements can reside under them. See the following figure and descriptions:

Network Hierarchy
Figure 1: Network Hierarchy table, displaying Global, Area, Site, Building, and Floor.
![Alt text](./images/site_image1.png)

Global: Default element under which all other hierarchical elements reside. Areas or sites are the only elements that can reside directly under Global.

Areas and Sites (Site and area icon in network hierarchy tree): Areas and sites reside under Global or under other areas or sites. They do not have a physical address. As the largest element, they identify a geographic region. They provide a way to group areas or sites.

Buildings (represented by the Buildings icon in the network hierarchy tree) reside under areas or sites. When creating a building, you must specify a physical address or latitude and longitude coordinates. Buildings cannot contain areas, but they can contain floors.

Floors (Floor icon in network hierarchy tree): Floors reside under buildings. You can add floors to buildings with or without maps that contain various building components, like walls and windows. If you decide to use floor maps, you can manually create them or import them from files, such as DXF, DWG, JPG, GIF, PNG, or PDF file types. Then you can position your wireless devices on the floor maps to visualize your wireless network coverage.

You can change the site hierarchy for unprovisioned devices while preserving AP locations on floor maps. Note, however, that you can't move an existing floor to a different building.

## RBAC access to create and modify sites
Users with the SUPER-ADMIN-ROLE, NETWORK-ADMIN-ROLE can create,update, delete sites.
Users with a custom role that includes network design access can create, update, and delete sites.

# Procedure
1. ## Prepare your Ansible environment:

Install Ansible if you haven't already.
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

2. ## Configure Host Inventory:

The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
##The Sample host_inventory_dnac1/hosts.yml

```bash
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
3. ## Define Playbook Input:
The workflow/sites/vars/site_hierarchy_design_vars.yaml file stores the sites details you want to configure.
Refer to the full workflow specification for detailed instructions on the available options and their structure: https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/site_workflow_manager/

To create an area named SAN JOSE under the existing area USA, and to define the building BLD23 along with FLOOR1 under Building 23, you can structure the input as follows:

```bash
---
#Select Catalyst Center version, this will overwrite the default version from host file
# Provide the Catalyst Center Version
catalyst_center_version: 2.3.7.6
# Sites Input List 
design_sites:
  - site:
      area:
        name: USA
        parent_name: Global
    type: area
  - site:
      area:
        name: SAN JOSE
        parent_name: Global/USA
    type: area
  - site:
      building:
        name: BLD23
        parent_name: Global/USA/SAN JOSE
        address: McCarthy Blvd, San Jose, California 95131, United States
        latitude: 37.398188
        longitude: -121.912974
        country: United States
    type: building
  - site:
      floor:
        name: FLOOR1
        parent_name: Global/USA/SAN JOSE/BLD23
        rfModel: Cubes And Walled Offices
        width: 100.00
        length: 100.00
        height: 10.00
        floor_number: 1
        units_of_measure: feet
        upload_floor_image_path: /workflows/sites/images/floor_image1.png
    type: floor
```
You can organize all the sites together, for example, grouping all floors under a single building and placing the building within the appropriate hierarchy.

4. Execute: Execute the playbook with your inputs and inventory. Specify your input file using the --e variable VARS_FILE_PATH.
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sites/playbook/site_hierarchy_playbook.yml --e VARS_FILE_PATH=/Users/pawansi/dnac_ansible_workflows/workflows/sites/vars/site_hierarchy_design_vars.yml -vvv
```
## Creating Bulk Site configurations using JINJA template and using the playbook

Below we have provided an example of Jinja template for sites.
This Example creates 3 Areas and in each area it creates 3 buildings and in each building it creates 3 floors. 
This example can be reused and customized to your requirement and increase the requirement scale.

### Creating bulk sites with JINJA template
workflow/sites/jinja_template/site_generation_template.j2 template can be used to customize the template and generate bulk sites.

```bash
---
# Define the Catalyst Center version
catalyst_center_version: 2.3.7.6

# List of floor images to be used for upload
{% set floor_images = ['floor_image1.png', 'floor_image2.jpg', 'floor_image3.jpeg', 'floor_image4.pdf'] %}

design_sites:
  # Define the top-level area
  - site:
      area:
        name: USA
        parent_name: Global
    type: area

  # Loop through areas
  {% for i in range(1, 4) %}
  - site:
      area:
        name: AREA{{i}}
        parent_name: Global/USA
    type: area

    # Loop through buildings in each area
    {% for j in range(1, 4) %}
    - site:
        building:
          name: AREA{{i}} BLD{{j}}
          parent_name: Global/USA/AREA{{i}}
          address: McCarthy Blvd, San Jose, California 95131, United States
          latitude: 37.398188
          longitude: -121.912974
          country: United States
      type: building

      # Loop through floors in each building
      {% for l in range(1, 4) %}
      - site:
          floor:
            name: AREA{{i}} BLD{{j}} FLOOR{{l}}
            parent_name: Global/USA/AREA{{i}}/AREA{{i}} BLD{{j}}
            rfModel: Cubes And Walled Offices
            width: 100.00
            length: 100.00
            height: 10.00
            floor_number: {{ l }}
            units_of_measure: feet
            upload_floor_image_path: workflows/sites/images/{{ floor_images[(l - 1) % floor_images|length] }}
            force_upload_floor_image: True
        type: floor
      {% endfor %}
    {% endfor %}
  {% endfor %}
```

Use the input var file: jinja_template_site_hierarchy_design_vars.yml and specify the name of your Jinja template in the input vars file.

5. Execute with Jinja template:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sites/playbook/site_hierarchy_playbook.yml --e VARS_FILE_PATH=/Users/pawansi/dnac_ansible_workflows/workflows/sites/vars/jinja_template_site_hierarchy_design_vars.yml -vvv
```

### Example of Sites Created Using a Jinja Template
Figure 2: Example of a site design created using a Jinja template.

![Alt text](./images/template_created_sites.png)

Figure 3: Example of a site created using a Jinja template, including floor image design.
![Alt text](./images/template_created_floor_image.png)

Delete all the sites under a specified hierarchy.

You can use the below example to delete all the floors and buildings under the site hierarchy Global/USA/AREA1 and site AREA1.

```bash
---
catalyst_center_version: 2.3.7.6
design_sites:  
  - site:
      area:
        name: AREA1
        parent_name: Global/USA
    type: area
```

## Site Deletion
Playbook can be used to delete sites under a specified hierarchy.
6. Run the delete Playbook:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/sites/playbook/delete_site_hierarchy_playbook.yml --e VARS_FILE_PATH=/Users/pawansi/dnac_ansible_workflows/workflows/sites/vars/delete_site_hierarchy_design_vars.yml -vvv
```
Sites will be deleted from the Catalyst Center.


# Reference

*Note: The environment used for the references in the above instructions is as follows:*

```yaml
python: 3.12.0
dnac_version: 2.3.7.6
ansible: 9.9.0
dnacentersdk: 2.8.6
cisco.dnac: 6.30.2
```