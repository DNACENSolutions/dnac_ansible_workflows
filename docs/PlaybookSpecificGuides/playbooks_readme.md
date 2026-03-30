# Prevalidated Playbooks Guides
The cisco-en-programmability/catalyst-center-ansible-iac project provides Ansible playbooks to automate Catalyst Center configurations. It streamlines Catalyst Center provisioning, automates network management tasks, and uses input validation schemas to ensure accuracy. The project includes comprehensive guides and sample inputs to help users manage their network infrastructure, and it supports Jinja-based templates for scalability and flexibility. This allows you to manage your entire Catalyst Center configuration through Git, providing version control, collaboration, and improved reliability.

# Table of Contents

## Day0 Configurations (Access and Integrations)
- [Catalyst Center Role Based Access Control and Users Management](./workflows/users_and_roles/README.md)
- [Catalyst Center ISE and AAA Servers Integration](./workflows/ise_radius_integration/#readme)

## Day1 Configurations (Design and Discovery)
- [Catalyst Center Site Hierarchy and Floor Maps design](./workflows/site_hierarchy/#readme)
- [Catalyst Center Device Credentials configurations and assignment](./workflows/device_credentials/#readme)
- [Catalyst Center Network Settings (Servers, Banners, TZ, SNMP, Logging, Telemetry Management](./workflows/network_settings/#readme)
- [Catalyst Center Network Settings Global Ip Pools and Site Pools reservation Management](./workflows/network_settings/#readme)
- [Catalyst Center Devces Discovery](./workflows/device_discovery/#readme)
- [Catalyst Center Device Inventory and device management](./workflows/inventory#readme)
- [Catalyst Center Plug and Play Device Onboarding](./workflows/plug_and_play/README.md)
- [Catalyst Center Device Provisioning and Re-Provisioning Management](./workflows/provision/README.md)
- [Catalyst Center Design and Deploy Device Templates](./workflows/device_templates/README.md)

## Day2 Configurations (Underlay automation and SD Access fabric)
- [Catalyst Cennter Underlay Automation (LAN Automation) Management](./workflows/lan_automation/#readme)
- [Catalyst Center SDA Fabric Site and Fabric Zones](./workflows/sda_fabric_sites_zones/README.md)
- [Catalyst Center SDA Fabric Transits (IP and SDA) Management](./workflows/sda_fabric_transits/README.md)
- [Catalyst Center Virtual Networks and L3 Anycast Gateways and L2 Vlans](./workflows/sda_virtual_networks_l2l3_gateways/README.md)
- [Catalyst Center SDA Fabric Device assignment to fabric sites and zones](./workflows/sda_fabric_device_roles/README.md)
- [Catalyst Center SDA Fabric Devices and Host Onboarding](./workflows/sda_hostonboarding/README.md)
- [Catalyst Center SDA Extranet Policies Management](./workflows/sda_fabric_extranet_policy/README.md)

## DayN Operation (Software Upgrade, Compliance, Events, Provisioning, backups and Assurance)
- [Catalyst Center Devces Software image management (SWIM)](./workflows/swim/README.md)
- [Catalyst Center Device compliance and remidiation](./workflows/network_compliance/README.md)
- [Catalyst Center Notification Destination and Events Subscription](./workflows/events_and_notifications/README.md)
- [Catalyst Center Devices Replacement Management](./workflows/device_replacement_rma/README.md)
- [Catalyst Center Access Point Provisioning and Access Point Configuration Management](./workflows/accesspoints_configuration_provisioning/README.md)
- [Device Configuration Customization using Catalyst Center Templates](./workflows/device_templates/README.md)
- [Catalyst Center managed network devices configurations backup management](./workflows/device_config_backup/README.md)

