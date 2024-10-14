# Catalyst Center Events and Notification Destination and Events Subscriptions Manager workflow

## Events and Notification Overview

Catalyst Center platform supports the ability to send custom notifications when specific events are triggered. This is valuable for third-party systems that take business actions based upon event type. For example, when a device in the network is out of compliance, a custom application may want to receive notifications and execute a software upgrade action.

You can view a list of available events for this release. From the top-left corner, click the menu icon and choose Platform > Manage > Configurations. These events can be customized for IT Service Management (ITSM) incidents.

## This workflow manage the follow:
    Configure various types of destinations to deliver event notifications from Cisco Catalyst Center Platform.
    Configuring/Updating the Webhook destination details in Cisco Catalyst Center.
    Configuring/Updating the Email destination details in Cisco Catalyst Center.
    Configuring/Updating the Syslog destination details in Cisco Catalyst Center.
    Configuring/Updating the SNMP destination details in Cisco Catalyst Center.
    Configuring/Updating the ITSM Integration Settings in Cisco Catalyst Center.
    Create/Update Notification using the above destination in Cisco Catalyst Center.

## How to Validate Input
Playbook: workflows/events_and_notifications/playbook/events_and_notifications_playbook.yml
Inputs: workflows/events_and_notifications/vars/events_and_notifications_destinations_inputs.yml
* Use `yamale`:

```bash
yamale -s workflows/events_and_notifications/schema/events_and_notifications_schema.yml workflows/events_and_notifications/vars/events_and_notifications_destinations_inputs.yml 
```

## How to Run
* Execute the Ansible Playbook to add, update, destination and events subscriptions:
```bash
    ansible-playbook -i host_inventory_dnac1/hosts.yml workflows/events_and_notifications/playbook/events_and_notifications_playbook.yml --e VARS_FILE_PATH=../vars/events_and_notifications_destinations_inputs.yml
```

##  Important Notes
* Always refer to the detailed input specification for comprehensive information on available options and their structure.



