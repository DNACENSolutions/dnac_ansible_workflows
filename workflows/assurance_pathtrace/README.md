# Assurance Pathtrace run Playbooks

# About Path Trace
You can perform a path trace between two nodes in your network—a specified source device and a specified destination device. The two nodes can be a combination of wired or wireless hosts or Layer 3 interfaces or both. In addition, you can specify the protocol that the Catalyst Center controller should use to establish the path trace connection, either TCP or UDP.

When you initiate a path trace, the Catalyst Center controller reviews and collects network topology and routing data from the discovered devices. It then uses this data to calculate a path between the two hosts or Layer 3 interfaces, and displays the path in a path trace topology. The topology includes the path direction and the devices along the path, including their IP addresses. The display also shows the protocol of the devices along the path (Switched, STP, ECMP, Routed, Trace Route) or other source type.

# Return
Pathtrace workflow returns the pathtrace results.

# UI Reference


# Sample Input:
```yaml
---
catalyst_center_version: 2.3.7.6
pathtrace_details: 
  - source_ip: "204.101.16.2"  # required field
    dest_ip: "204.101.16.1"  # required field
    source_port: 4020  # optional field
    dest_port: 4021  # optional field
    protocol: "TCP"  # optional field
    include_stats:  # optional field
      - DEVICE_STATS
      - INTERFACE_STATS
      - QOS_STATS
      - PERFORMANCE_STATS
      - ACL_TRACE
    periodic_refresh: false  # optional field
    control_path: false  # optional field
    delete_on_completion: true  # optional field
  - source_ip: "204.101.16.2"  # required field
    dest_ip: "204.192.3.40"  # required field
    get_last_pathtrace_result: true
```


# Path Trace Playbook Execution:
ansible-playbook -i /Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/ansible_inventory/catalystcenter_inventory/hosts.yml /Users/pawansi/workspace/CatC_Configs/catc_ansible_workflows/workflows/assurance_pathtrace/playbook/delete_assurance_pathtrace_playbook.yml --e VARS_FILE_PATH=/Users/pawansi/workspace/CatC_Configs/CatC_SD_Access_campus/catc_configs/sites/california/day_n_assurance_pathtrace.yml -v




# Schema Validation:
(ansible-venv) pawansi@PAWANSI-M-7J1W catc_ansible_workflows % yamale -s workflows/assurance_pathtrace/schema/assurance_pathtrace_schema.yml  workflows/assurance_pathtrace/vars/assurance_pathtrace_inputs.yml 
Validating workflows/assurance_pathtrace/vars/assurance_pathtrace_inputs.yml...
Validation success! 👍



# Pathtrace Limitations

All the below listed Catalyst Center Path trace limitation apply to workflow/playbook also

## Path trace has the following limitations and restrictions.

    Path trace from a third-party device in Catalyst Center is not supported.

    Path trace between a fabric client and a nonfabric client is not supported.

    Path trace between two fabric clients over multi virtual routing and forwarding (VRF) virtual networks (VNs) is not supported.

    Path trace between two fabric clients over multi sites (domains) is not supported.

    Clients connected in the same fabric and same site where either edge switch is not part of the fabric is not supported.

    Path trace from a router's loopback interface is not supported.

    Overlapping IP addresses are not supported with or without fabric.

    For path trace to work on a Locator ID/Separation Protocol (LISP) fabric, make sure that the traffic is running and cache is available on the edge switches.

    Path trace in Cisco Adaptive Security Appliances (ASA) is not supported because Cisco ASA does not support CDP. It is not possible to identify the path through the Cisco ASA appliance.

    Path trace is not supported for the management interface in wireless controllers in untagged mode.

    Path trace for centralized Wireless Mobility Modes Asymmetric Mobility Tunneling is not supported.

    Path trace for Virtual Switching System (VSS), Multi-Link Aggregation Control Protocol (MLACP), or Virtual PortChannel (vPC) is not supported.

    Path trace for Equal-Cost Multi-Path Routing (ECMP) over Switched Virtual Interface (SVI) is not supported.

    Path trace is not supported on devices with NAT or firewall.

    Cisco Performance Routing (PfR) is not supported with DMVPN tunnels.

    Path trace that has VLAN ACLs (VACLs) enabled is not supported.

    For a Non Periodic Refresh (NPR) path scenario, after an upgrade, the controller does not refresh the path. Additionally, statistics collection stops. To continue statistics collection, you must initiate a new path request.

    Path trace from a host in a Hot Standby Router Protocol (HSRP) VLAN to a host in a non-HSRP VLAN that is connected to any of the HSRP routers is not supported.

    Object groups are not supported in an ACL trace.

    Port-channel Port Aggregation Protocol (PAgP) mode is not supported. Only LACP mode is supported.

    Applying a performance monitor configuration using Catalyst Center fails if there is a different performance monitor policy configuration on the interface. Remove the performance monitor configuration on the interface and resubmit the path trace request.

    Path trace for Performance Monitor statistics is not supported for Cisco ASR 1000 Series routers (Cisco IOS XE 16.3.1).

    Path trace for Performance Monitor statistics is not supported for the Cisco Catalyst 3850 Switch (Cisco IOS XE 16.2.x and 16.3.1).

    Path trace for Cisco Mobility Express (ME) wireless controllers is not supported.

    Path trace for wireless clients that use OTT in Cisco SD-Access fabric is not supported.

    Path trace from a Layer 2 switch is not supported.

    Cisco's Industrial Ethernet (IE) Switches are extended nodes as part of the SD-Access solution. Currently, path trace does not recognize extended nodes, so if a topology contains extended nodes, you will get an error message.

    Dual stack that has both IPv4 and IPv6 addresses for devices is not supported. If this occurs, an error message displays stating that the given address is unknown.

    Because Cisco wireless controllers do not send SNMP mobility traps, note the following:

        For a path trace request, Catalyst Center does not have the right egress virtual interface highlighted on any foreign wireless controller.

        The path trace request does not highlight any ACLs applied on the foreign wireless controller.