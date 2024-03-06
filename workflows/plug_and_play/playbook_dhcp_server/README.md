#Ansible Playbook for DHCP server configuration Automation on Cisco IOS required for PnP devices bringup



<h3>Requires</h3>
<ul>
  <li>ansible 2.6.4</li>
</ul>
<h3>Supports</h3>
<ul>
  <li>This script provides support for Cisco IOS</li>
</ul>

<h3>How to use</h3>
<ul>
  <li>Ensure you setup the topology</li>
  <li>Configure Management IP Address or Loopback IP address and make sure it is reachable from execution server and enable SSH in the router</li>
  <li>Ensure you have ansible installed on your computer</li>
  <li>Edit the vars file to meet your topology</li>
  <li>Run the script <i>ansible-playbook -i inventory dhcp_server_config.yml --e VARS_FILE_PATH="Path to the varfile update as per your topology"</i></li>
</ul>
