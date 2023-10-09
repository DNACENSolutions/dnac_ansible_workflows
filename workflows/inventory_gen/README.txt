playbook name:
    inventory_gen/inventory_gen.yaml

This playbook generate your network_devices hosts data from a DNAC. you can take this data and add it to your inventory

How to Execute:

    ansible-playbook -i ./inventory/demo_lab/001-dnac_inventory.yml ./workflows/inventory_gen/playbook/inventory_gen.yml --extra-vars VARS_FILES_PATH=./../vars/
