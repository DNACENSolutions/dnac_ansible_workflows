# Backup and Restore Config Generator

## Table of Contents

- [User Flow (3 Steps)](#user-flow-3-steps)
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Workflow Structure](#workflow-structure)
- [Schema Parameters](#schema-parameters)
- [Getting Started](#getting-started)
- [Operations](#operations)
- [Examples](#examples)

## Overview

The Backup and Restore config generator automates the creation of YAML configurations for existing NFS configurations and backup storage configurations deployed in Cisco Catalyst Center. This tool reduces the effort required to manually create Ansible playbooks by programmatically generating configurations from existing infrastructure.

---

## Features

- **Configuration Generation**: Generate YAML configurations compatible with `backup_and_restore_workflow_manager` module.
Extract existing NFS configurations and backup storage configurations from your Cisco Catalyst Center.
Convert them into properly formatted YAML files.
Generate files that are ready to use with Ansible automation.
- **Component Filtering**: Selective generation of NFS configurations or backup storage configurations
- **Flexible Output**: Configurable file paths and naming conventions
- **Brownfield Support**: Extract configurations from existing Catalyst Center deployments
- **API Integration**: Leverages native Catalyst Center APIs for data retrieval

---

## Prerequisites

### Software Requirements

| Component | Version |
|-----------|---------|
| Ansible | 2.13+ |
| cisco.catalystcenter collection | 2.6.0 |
| Python | 3.9+ |
| Cisco Catalyst Center | 3.1.3.0+ |
| catalystcentersdk | 2.9.3+ |

### Required Collections

```bash
ansible-galaxy collection install cisco.catalystcenter  
ansible-galaxy collection install ansible.utils
pip install catalystcentersdk
pip install yamale
```

### Access Requirements

- Catalyst Center admin credentials
- Network connectivity to Catalyst Center API
- Backup and restore infrastructure deployed and configured
- Existing NFS configurations and backup storage configurations

---

## Workflow Structure

```
backup_and_restore_config_generator/
├── playbook/
│   └── backup_and_restore_config_generator.yml          # Main operations
├── vars/
│   ├── backup_and_restore_config_inputs.yml             # Configuration examples
├── schema/
│   └── backup_and_restore_config_schema.yml             # Input validation
└── README.md                                                
```

---

## Schema Parameters

### Top-Level Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file_path | string | No | auto-generated | Output file path for YAML configuration file. Default filename: `backup_and_restore_playbook_config_<YYYY-MM-DD_HH-MM-SS>.yml` |
| file_mode | string | No | overwrite | File write mode — `overwrite` replaces the file, `append` adds to it. Only applicable when `file_path` is provided. |
| config | dict | No | omitted (all components) | Configuration filters dict. When omitted, all NFS and backup storage configurations are retrieved. When provided, `component_specific_filters` is mandatory. |

### Component Specific Filtering (within `config` parameter)

| Parameter      | Type | Required | Default | Description |
|--------------|------|----------|-------------|-----------|
| component_specific_filters | dict | Yes (when `config` provided) | N/A | Required when `config` is provided. Filters to specify which components to include. |
| components_list | list | Conditional | N/A | List of components to include. **Required when no component filter blocks are provided.** Empty list is invalid when no filter blocks exist. |
| nfs_configuration      | list(dict) | No | all NFS configurations | NFS configuration filtering criteria. Both `server_ip` and `source_path` must be provided together for filtering. |
| backup_storage_configuration | list(dict) | No | all backup storage configurations | Backup storage configuration filtering criteria. Only `server_type` filtering is supported. |

**Component Logic Rules:**
- **No `config`**: All components are retrieved (equivalent to both `nfs_configuration` and `backup_storage_configuration`)
- **`config` provided**: `component_specific_filters` is mandatory
- **Component filter blocks provided** (e.g., `nfs_configuration`): Those components are automatically added to `components_list` when missing
- **No component filter blocks**: `components_list` is required and must not be empty

**Valid Component Types:**
- `nfs_configuration`: NFS server configurations
- `backup_storage_configuration`: Backup storage configurations  

### NFS Configuration Filters

| Parameter | Type   | Required |  Description |
|-----------|--------|-------------|----------------|
| server_ip | string | False |  Filter by NFS server IP address | 
| source_path   | string| False | Filter by NFS source path |

### Backup Storage Configuration Filters

| Parameter | Type | Required |  Description |
|-----------|------|-------------|-----------------|
| server_type    | string | False |  Filter by server type ("NFS" or "PHYSICAL_DISK") | 

---

## Getting Started

## Workflow Steps
## User Flow (3 Steps)

```mermaid
flowchart TD
  A[Start] --> B[Step 1: Create virtual env and install dependencies]
  B --> C[Step 2: Provide workflow inputs]
  C --> D{Choose input location}
  D -->|Option A| E[Update inventory hosts.yaml]
  D -->|Option B| F[Update vars input file]
  E --> G[Step 3: Export env vars]
  F --> G
  G --> H[Run ansible-playbook]
  H --> I[Review playbook summary output]
  I --> J[Done]
```

### Installation and Run (Aligned)

1. Create and activate a Python virtual environment, then install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install cisco.catalystcenter --force
```

2. Provide workflow inputs in either inventory (`inventory/demo_lab/hosts.yaml`) or the workflow `vars/` file.

3. Export Catalyst Center environment variables and run the playbook.

```bash
export HOSTIP=<catalyst-center-ip-or-fqdn>
export CATALYST_CENTER_USERNAME=<username>
export CATALYST_CENTER_PASSWORD='<password>'
ansible-playbook -i ./inventory/demo_lab/hosts.yaml ./workflows/backup_and_restore_config_generator/playbook/backup_and_restore_config_generator.yml -vvvv
```


## Operations

### Generate Operations (state: gathered)

Use `backup_and_restore_config_generator.yml` for generating YAML playbook configuration operations.

#### Generate All Configurations

**Description**:  Omit config parameter entirely at module level
                  All existing NFS configurations and backup storage configurations will be extracted.

```yaml
# No config at all - only DNAC connection details
# Expected: defaults to generates all configs
backup_and_restore_config:
  - file_path: "/tmp/complete_backup_restore_config.yml"  

```

#### Component-Specific Generation

**Description**: Generates configuration for specific component types only.

**Extract NFS Configurations Only**

```yaml
#Test NFS configuration filter
 backup_and_restore_config:
   - file_path: "/tmp/backup_restore_components_config1.yml"
     config:
       component_specific_filters:
         components_list: ["nfs_configuration"]

```

**Extract Backup Storage Configurations Only**

```yaml
#Test Backup configuration filter
backup_and_restore_config:
  - file_path: "/tmp/backup_storage_configurations_config3.yml"
    config:
      component_specific_filters:
        components_list: ["backup_storage_configuration"]
```

**Validate and Execute:**

```bash
# Validate
./tools/schemavalidation.sh \
  -s workflows/backup_and_restore_config_generator/schema/backup_and_restore_config_schema.yml \
  -v workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml
```
Return result validate:
```bash

 ./tools/schemavalidation.sh \
>   -s workflows/backup_and_restore_config_generator/schema/backup_and_restore_config_schema.yml \
>   -v workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml
workflows/backup_and_restore_config_generator/schema/backup_and_restore_config_schema.yml
workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml
python -c <yamale validation wrapper>
Validating workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml...
Validation success! 👍

```

```bash
# Execute (run from project root directory)
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/backup_and_restore_config_generator/playbook/backup_and_restore_config_generator.yml \
  --extra-vars VARS_FILE_PATH=${PWD}/workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml
```

Expected Terminal Output:

1. Generate All Configurations

```code
        file_path: /tmp/complete_backup_restore_config.yml
      msg: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
      response:
        components_processed: 1
        components_skipped: 1
        configurations_count: 1
        file_path: /tmp/complete_backup_restore_config.yml
        message: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
        status: success
      status: success
    skipped: false
```

2. Component Specific Generation:

a. NFS Configuration Filter:

```code
        component_specific_filters:
          components_list:
          - nfs_configuration
        file_path: /tmp/nfs_configurations_config.yml
      msg: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
      response:
        components_processed: 1
        components_skipped: 0
        configurations_count: 4
        file_path: /tmp/nfs_configurations_config.yml
        message: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
        status: success
      status: success
    skipped: false

```

b. Backup Storage Configuration Filter:

```code
component_specific_filters:
          components_list:
          - backup_storage_configuration
        file_path: /tmp/backup_storage_configurations_config.yml
      msg: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
      response:
        components_processed: 1
        components_skipped: 0
        configurations_count: 1
        file_path: /tmp/backup_storage_configurations_config.yml
        message: YAML configuration file generated successfully for module 'backup_and_restore_workflow_manager'
        status: success
      status: success
    skipped: false

```
---
## Examples

### Example 1: Generate ALL backup and restore components

```yaml
  backup_and_restore_config:
    - file_path: "/tmp/complete_backup_restore_config.yml"
```
After running the playbook , the followning YAML configuration is generated .

```yaml
---
config:
- nfs_configuration:
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB23
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 10.195.189.95
    source_path: /data/nfsshare/iac
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB30
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB17
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
- backup_storage_configuration:
  - server_type: NFS
    nfs_details:
      server_ip: 172.27.17.90
      source_path: /home/nfsshare/backups/TB23
      nfs_port: 2049
      nfs_version: nfs4
      nfs_portmapper_port: 111
    data_retention_period: 3
```

### Example 2: NFS Configuration Filters only

Extract all NFS configurations.

```yaml
 backup_and_restore_config:
   - file_path: "/tmp/backup_restore_components_config1.yml"
     config:
       component_specific_filters:
         components_list: ["nfs_configuration"]
```

After running the playbook , the followning YAML configuration is generated .

```yaml
---
config:
- nfs_configuration:
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB23
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 10.195.189.95
    source_path: /data/nfsshare/iac
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB30
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
  - server_ip: 172.27.17.90
    source_path: /home/nfsshare/backups/TB17
    nfs_port: 2049
    nfs_version: nfs4
    nfs_portmapper_port: 111
```

### Example 3: Backup Storage Configuration Filters only

Extract all backup storage configurations

```yaml
backup_and_restore_config:
  - file_path: "/tmp/backup_storage_configurations_config3.yml"
    config:
      component_specific_filters:
        components_list: ["backup_storage_configuration"]
```

After running the playbook , the followning YAML configuration is generated .

```yaml
---
config:
- backup_storage_configuration:
  - server_type: NFS
    nfs_details:
      server_ip: 172.27.17.90
      source_path: /home/nfsshare/backups/TB23
      nfs_port: 2049
      nfs_version: nfs4
      nfs_portmapper_port: 111
    data_retention_period: 3
```

### Example 4: Filtered NFS Configurations

```yaml
 backup_and_restore_config:
   - file_path: "/tmp/filtered_nfs_configurations.yml"
     config:
       component_specific_filters:
         components_list: ["nfs_configuration"]
         nfs_configuration:
           - server_ip: "172.27.17.90"
             source_path: "/home/nfsshare/backups/TB23"
           - server_ip: "172.27.17.90"
             source_path: "/home/nfsshare/backups/TB17"
```

### Example 5: Multi-Component configurations

```yaml
 backup_and_restore_config:
   - file_path: "/tmp/nfs_and_backup_storage.yml"
     config:
       component_specific_filters:
         components_list: ["nfs_configuration", "backup_storage_configuration"]
         nfs_configuration:
           - server_ip: "172.27.17.90"
             source_path: "/home/nfsshare/backups/TB23"
         backup_storage_configuration:
           - server_type: "NFS"
```

### Example 6: Backup Storage with multiple server types

```yaml
 backup_and_restore_config:
   - file_path: "/tmp/backup_storage_all_types.yml"
     config:  
       component_specific_filters:
         components_list: ["backup_storage_configuration"]
         backup_storage_configuration:
           - server_type: "NFS"
           - server_type: "PHYSICAL_DISK"
```

---

## Additional Resources

- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [Cisco DNA Center SDK](https://catalystcentersdk.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)

## Inventory / group_vars Example

You can also run this workflow without `VARS_FILE_PATH` by moving the sample workflow data into inventory, `host_vars`, or `group_vars`.

1. Create an inventory vars file such as `inventory/group_vars/all.yml` or `inventory/host_vars/<host>.yml`.
2. Copy the sample workflow data from `workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml` into that inventory vars file.
3. Keep the same top-level variable name in inventory: `backup_and_restore_config`.
4. Run the playbook without `VARS_FILE_PATH`:

```bash
ansible-playbook -i <inventory-file> workflows/backup_and_restore_config_generator/playbook/backup_and_restore_config_generator.yml -vvvv
```
## VARS_FILE_PATH Path Resolution

Ansible resolves `VARS_FILE_PATH` relative to the playbook directory, not the current working directory.

Use either of these forms:

- Relative to the playbook: `../vars/backup_and_restore_config_inputs.yml`
- Fully resolved from the repo root: `${PWD}/workflows/backup_and_restore_config_generator/vars/backup_and_restore_config_inputs.yml`

