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
--tags create,assign \
-i inventory/iac2/hosts \
-vvvv


# Discovery
ansible-playbook playbooks/discovery.yml \
--tags multi_range,cdp \
-i inventory/iac2/hosts \
-vvvv


# Templates
ansible-playbook playbooks/templates.yml \
--tags pnp_upstream_sw,pnp_devices_sw,pnp_upstream_ap \
-i inventory/iac2/hosts \
-vvvv


# Network profiles
# AC2. Manual steps.


# Provision
ansible-playbook playbooks/inventory.yml \
--tags associate \
-i inventory/iac2/hosts \
-vvvv


# PnP
ansible-playbook playbooks/pnp.yml \
--tags claim_cat9k_stack,claim_ewlc \
-i inventory/iac2/hosts \
-vvvv


# SWIM
ansible-playbook playbooks/swim.yml \
--tags device_ewlc_ha \
-i inventory/iac2/hosts \
-vvvv
