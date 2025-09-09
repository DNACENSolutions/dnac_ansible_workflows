# Schema Validation Tools for DNAC Ansible Workflows

This directory contains comprehensive schema validation tools for validating all workflow inputs against their corresponding schema files.

## Overview

The schema validation system consists of two main components:

1. **`comprehensive_schema_validation.py`** - A Python-based validation tool with detailed reporting
2. **`schemavalidation.sh`** - A shell script wrapper that provides easy command-line access

## Prerequisites

- Python environment with `yamale` installed: `/Users/pawansi/venv/ansible/bin/activate`
- YAML schema files in `workflows/*/schema/` directories
- YAML variable files in `workflows/*/vars/` directories

## Quick Start

### List All Available Workflows
```bash
./tools/schemavalidation.sh --list-workflows
```

### Validate All Workflows
```bash
./tools/schemavalidation.sh
```

### Validate a Specific Workflow
```bash
./tools/schemavalidation.sh --workflow device_discovery
```

### Validate Specific Files
```bash
./tools/schemavalidation.sh -s workflows/device_discovery/schema/device_discovery_schema.yml -v workflows/device_discovery/vars/device_discovery_vars.yml
```

### Use Python Tool with JSON Report
```bash
./tools/schemavalidation.sh --python-tool --output validation_report.json
```

## Tool Details

### Shell Script (`schemavalidation.sh`)

The shell script provides a user-friendly interface with the following options:

```bash
Usage: schemavalidation.sh [OPTIONS]

Options:
  -h, --help              Show help message
  -w, --workflow NAME     Validate only a specific workflow
  -d, --workflows-dir DIR Directory containing workflows (default: workflows)
  -o, --output FILE       Output file for detailed JSON report
  -q, --quiet             Only show summary, suppress detailed output
  -s, --schema FILE       Validate specific schema file
  -v, --vars FILE         Validate specific vars file (requires -s)
  --python-tool           Use Python validation tool instead of yamale directly
  --list-workflows        List all available workflows
```

### Python Tool (`comprehensive_schema_validation.py`)

The Python tool provides advanced features:

- **Automatic Schema-Vars Matching**: Intelligently matches schema files to their corresponding variable files
- **Detailed Error Reporting**: Provides comprehensive error messages and validation details
- **JSON Report Generation**: Creates detailed JSON reports for integration with CI/CD pipelines
- **Flexible Filtering**: Supports validation of specific workflows or file patterns

```bash
python3 comprehensive_schema_validation.py --help
```

## Workflow Structure

Each workflow should have the following structure:
```
workflows/
├── workflow_name/
│   ├── schema/
│   │   ├── workflow_schema.yml
│   │   └── delete_workflow_schema.yml
│   ├── vars/
│   │   ├── workflow_vars.yml
│   │   └── workflow_inputs.yml
│   └── ...
```

## Schema File Format

Schema files use the `yamale` format for YAML validation:

```yaml
# Example schema file
catalyst_center_version: str(required=False)
catalyst_center_verify: bool(required=False)
device_details: list(include('device_type'), min=1, max=100, required=True)
---
device_type:
  hostname: str(required=True)
  ip_address: str(required=True)
  device_type: enum("switch", "router", "ap", required=False)
```

## Variable File Format

Variable files contain the actual configuration data:

```yaml
# Example vars file
catalyst_center_version: "2.3.7.6"
catalyst_center_verify: true
device_details:
  - hostname: "switch-01"
    ip_address: "192.168.1.10"
    device_type: "switch"
  - hostname: "router-01"
    ip_address: "192.168.1.1"
    device_type: "router"
```

## Validation Results

The tools provide three types of validation results:

- **SUCCESS**: Schema validation passed
- **FAILED**: Schema validation failed with specific error details
- **WARNING**: Missing schema or vars files, or other non-critical issues

## Integration with CI/CD

### Basic Validation in CI Pipeline
```bash
# Exit with error code if validation fails
./tools/schemavalidation.sh --quiet
```

### Detailed Reporting for CI
```bash
# Generate JSON report for further processing
./tools/schemavalidation.sh --python-tool --output validation_report.json --quiet
```

## Troubleshooting

### Common Issues

1. **Python Environment Not Found**
   ```
   Error: Python environment not found at /Users/pawansi/venv/ansible/bin/python3
   ```
   Solution: Ensure the Python environment exists and yamale is installed

2. **Yamale Not Found**
   ```
   Error: yamale not found in Python environment
   ```
   Solution: Install yamale in the environment:
   ```bash
   source /Users/pawansi/venv/ansible/bin/activate
   pip install yamale
   ```

3. **Schema Validation Errors**
   - Check that variable files match the expected schema format
   - Verify required fields are present
   - Ensure data types match schema definitions

### Debug Mode

For detailed debugging, run the Python tool directly:
```bash
/Users/pawansi/venv/ansible/bin/python3 tools/comprehensive_schema_validation.py --workflow workflow_name
```

## Examples

### Example 1: Validate Device Discovery Workflow
```bash
./tools/schemavalidation.sh --workflow device_discovery
```

### Example 2: Generate Comprehensive Report
```bash
./tools/schemavalidation.sh --python-tool --output full_validation_report.json
```

### Example 3: Validate Specific Schema-Vars Pair
```bash
./tools/schemavalidation.sh \
  -s workflows/accesspoints_configuration_provisioning/schema/accesspoints_config_schema.yml \
  -v workflows/accesspoints_configuration_provisioning/vars/accesspoints_configuration_vars.yml
```

## Workflow Coverage

The validation tools automatically discover and validate all workflows that contain both `schema/` and `vars/` directories. As of the last update, the following workflows are supported:

- accesspoints_configuration_provisioning
- ansible_vault_update
- application_policy
- assurance_health_score_settings
- assurance_intelligent_capture
- assurance_issues_management
- assurance_pathtrace
- device_config_backup
- device_credentials
- device_discovery
- device_replacement_rma
- device_templates
- e2e_lan_automationed_site_bringup
- e2e_network_devices_sw_upgrade
- e2e_nw_design_and_inventory
- events_and_notifications
- inventory
- ip_pools
- ise_radius_integration
- ise_sg_contracts_policies
- lan_automation
- network_compliance
- network_profile_switching
- network_profile_wireless
- network_settings
- plug_and_play
- provision
- sda_fabric_device_roles
- sda_fabric_extranet_policy
- sda_fabric_multicast
- sda_fabric_sites_zones
- sda_fabric_transits
- sda_hostonboarding
- sda_virtual_networks_l2l3_gateways
- site_hierarchy
- sites
- swim
- tags_manager
- users_and_roles
- wireless_design

## Contributing

When adding new workflows:

1. Ensure both `schema/` and `vars/` directories exist
2. Create appropriate schema files using yamale format
3. Provide example variable files
4. Test validation using the provided tools
5. Update this documentation if needed

## Support

For issues or questions about schema validation:

1. Check the troubleshooting section above
2. Run validation with detailed output to see specific errors
3. Verify schema and variable file formats
4. Ensure the Python environment is properly configured
