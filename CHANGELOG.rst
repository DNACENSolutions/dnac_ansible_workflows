=============================================
Cisco Catalyst Center Ansible IaC Changelog
=============================================

.. towncrier release notes start

v1.0.0 (2026-06-22)
====================

Release Summary
---------------

Initial GA release of the Cisco Catalyst Center Ansible Infrastructure as Code (IaC) collection.
This release provides Cisco-validated Ansible playbooks to automate Catalyst Center configurations
across Day 0, Day 1, Day 2, and Day N operations.

New Workflows
-------------

**Day 0 – Access and Integrations**

- Users and Roles Management (``workflows/users_and_roles``)
- ISE and AAA Servers Integration (``workflows/ise_radius_integration``)

**Day 1 – Design and Discovery**

- Site Hierarchy and Floor Maps (``workflows/site_hierarchy``)
- Device Credentials (``workflows/device_credentials``)
- Network Settings – Servers, Banners, TZ, SNMP, Logging, Telemetry (``workflows/network_settings``)
- Global and Site IP Address Pools (``workflows/network_settings``)
- Wireless Design (``workflows/wireless_design``)
- Wireless Network Profile (``workflows/network_profile_wireless``)
- Network Profile Switching (``workflows/network_profile_switching``)
- Device Discovery (``workflows/device_discovery``)
- Device Inventory and Management (``workflows/inventory``)
- Plug and Play Onboarding (``workflows/plug_and_play``)
- Device Provisioning and Re-Provisioning (``workflows/provision``)
- Device Templates (``workflows/device_templates``)
- Tags Management (``workflows/tags_manager``)

**Day 2 – Underlay Automation and SD-Access Fabric**

- LAN Automation (``workflows/lan_automation``)
- SDA Fabric Sites and Zones (``workflows/sda_fabric_sites_zones``)
- SDA Fabric Transits (``workflows/sda_fabric_transits``)
- Virtual Networks and L3/L2 Gateways (``workflows/sda_virtual_networks_l2l3_gateways``)
- SDA Fabric Device Roles (``workflows/sda_fabric_device_roles``)
- SDA Host Onboarding (``workflows/sda_hostonboarding``)
- SDA Extranet Policies (``workflows/sda_fabric_extranet_policy``)
- SDA Fabric Multicast (``workflows/sda_fabric_multicast``)
- Application Policy (``workflows/application_policy``)

**Day N – Operations**

- Software Image Management / SWIM (``workflows/swim``)
- Network Compliance and Remediation (``workflows/network_compliance``)
- Events and Notifications (``workflows/events_and_notifications``)
- Device Replacement / RMA (``workflows/device_replacement_rma``)
- Access Point Provisioning and Configuration (``workflows/accesspoints_configuration_provisioning``)
- Device Configuration Backup (``workflows/device_config_backup``)
- Assurance Health Score Settings (``workflows/assurance_health_score_settings``)
- Assurance Path Trace (``workflows/assurance_pathtrace``)
- Assurance Issues Management (``workflows/assurance_issues_management``)
- Assurance ICAP (``workflows/assurance_intelligent_capture``)
- Fabric Devices Info (``workflows/fabric_devices_info``)
- Network Devices Info (``workflows/network_devices_info``)
- Configuration Backup and Restore (``workflows/backup_and_restore``)
- Reports Management (``workflows/reports``)

**Configuration Generators**

- Config generators added for all major workflow categories.

**Compatibility**

- Supports Cisco Catalyst Center versions 2.3.7.6, 2.3.7.7, 2.3.7.9, 2.3.7.10, and 3.1.6.x
- Requires ``cisco.catalystcenter`` Ansible Galaxy collection (latest)
- Requires ``catalystcentersdk`` Python SDK (latest)
- Requires ansible-core >= 2.16.0 and Python >= 3.12
