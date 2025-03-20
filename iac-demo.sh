# Site hierarchy
ansible-playbook playbooks/site.yml \
--tags create \
-i inventory/iac2/hosts \
-vvvv


# Site hierarchy (scale)
ansible-playbook playbooks/site_scale.yml \
--extra-vars '{"COUNT": 100}' \
--extra-vars '{"START": 1}' \
--tags generate,create \
-i inventory/iac2/hosts \
-vvvv

# Credentials
ansible-playbook playbooks/credentials.yml \
--tags create \
-i inventory/iac2/hosts \
-vvvv


# Discovery
ansible-playbook playbooks/discovery.yml \
--tags multi_range \
-i inventory/iac2/hosts \
-vvvv


# Templates
ansible-playbook playbooks/templates.yml \
--tags pnp_upstream_sw,pnp_devices_sw,pnp_upstream_ap \
-i inventory/iac2/hosts \
-vvvv


# Network profiles
# AC2. Manual steps.


# Inventory
ansible-playbook playbooks/inventory.yml \
--tags provision \
-i inventory/iac2/hosts \
-vvvv


# SWIM
ansible-playbook playbooks/swim.yml \
--tags device_e2e \
-i inventory/iac2/hosts \
-vvvv


# PnP
ansible-playbook playbooks/pnp.yml \
--tags claim_cat9k \
-i inventory/iac2/hosts \
-vvvv


# ISE and AAA Integration
ansible-playbook playbooks/ise_aaa_intg.yml \
--tags ise_aaa_intg \
-i inventory/iac2/hosts \
-vvvv


# Provision
ansible-playbook playbooks/provision.yml \
--tags prov_wireless \
-i inventory/iac2/hosts \
-vvvv


# Network Settings
ansible-playbook playbooks/network_settings.yml \
--tags global_settings \
-i inventory/iac2/hosts \
-vvvv


# Compliance
ansible-playbook playbooks/compliance.yml \
--tags check_cat_site_ip \
-i inventory/iac2/hosts \
-vvvv


# LAN Automation
ansible-playbook playbooks/lan_automation.yml \
--tags start_lan_auto \
-i inventory/iac2/hosts \
-vvvv


# IP Pools
ansible-playbook playbooks/ip_pools.yml \
--tags reserve_subpool \
-i inventory/iac2/hosts \
-vvvv
