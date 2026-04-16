# Run All Config Generators Script

Batch execution script for running all `*_config_generator` workflows with their corresponding var files.

## Features

- ✅ **Automatic Discovery**: Finds all config_generator workflows in the repository
- ✅ **Correct Exit Status**: Uses `PIPESTATUS` to capture actual ansible-playbook exit codes
- ✅ **Detailed Logging**: Creates individual log files for each playbook run
- ✅ **Summary Report**: Generates a summary log with success/failure counts
- ✅ **Continue on Error**: Optional flag to continue running even if a playbook fails
- ✅ **Color-Coded Output**: Visual feedback with colored status messages
- ✅ **Flexible Inventory**: Supports custom inventory files

## Usage

```bash
./tools/run_all_config_generators.sh [inventory_file] [--continue-on-error]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `inventory_file` | Path to inventory file | No (default: `inventory/demo_lab/hosts.yaml`) |
| `--continue-on-error` | Continue running even if a playbook fails | No (default: stop on first failure) |
| `--help` or `-h` | Show help message | No |

## Examples

### Run with default inventory (stops on first failure)
```bash
./tools/run_all_config_generators.sh
```

### Run with custom inventory
```bash
./tools/run_all_config_generators.sh inventory/mylab/hosts.yaml
```

### Run with custom inventory and continue on error
```bash
./tools/run_all_config_generators.sh inventory/mylab/hosts.yaml --continue-on-error
```

### Run with relative path
```bash
cd /path/to/dnac_ansible_workflows
./tools/run_all_config_generators.sh inventory/mylab/hosts.yaml
```

## Output

### Console Output

The script provides color-coded output:
- 🟢 **Green** ✓ - Successful execution
- 🔴 **Red** ✗ - Failed execution
- 🟡 **Yellow** ⚠ - Skipped (missing playbook or vars file)
- 🔵 **Blue** ℹ - Informational messages

### Log Files

All logs are stored in `logs/config_generators/`:

```
logs/config_generators/
├── summary_20260414_205500.log          # Summary of all runs
├── site_config_generator_20260414_205500.log
├── network_settings_config_generator_20260414_205500.log
├── discovery_config_generator_20260414_205500.log
└── ...
```

### Summary Report

At the end of execution, you'll see:

```
========================================
Execution Summary
========================================

Total workflows: 28
Successful: 25
Failed: 2
Skipped: 1

Successful workflows:
  ✓ site_config_generator
  ✓ network_settings_config_generator
  ✓ discovery_config_generator
  ...

Failed workflows:
  ✗ sda_fabric_sites_zones_config_generator (exit code: 2)
  ✗ provision_config_generator (exit code: 1)

Skipped workflows:
  ⚠ custom_workflow (no vars file)

Summary log: logs/config_generators/summary_20260414_205500.log
Detailed logs: logs/config_generators
```

## How It Works

1. **Discovery**: Scans `workflows/` directory for all `*_config_generator` folders
2. **Validation**: For each workflow, checks for:
   - Playbook file in `playbook/` subdirectory
   - Vars file in `vars/` subdirectory
   - Inventory file existence
3. **Execution**: Runs `ansible-playbook` with:
   - Specified inventory
   - Discovered playbook
   - `--extra-vars VARS_FILE_PATH=<vars_file>`
4. **Status Capture**: Uses `PIPESTATUS[0]` to get the actual exit code from ansible-playbook (not from `tee`)
5. **Logging**: Saves output to individual log files and summary log
6. **Reporting**: Displays color-coded summary with counts and lists

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | All playbooks succeeded |
| `1` | One or more playbooks failed |

## Troubleshooting

### Issue: All playbooks show as successful even when they fail

**Solution**: This is now fixed! The script uses `PIPESTATUS[0]` to capture the actual ansible-playbook exit code instead of the `tee` command's exit code.

### Issue: Script stops after first failure

**Solution**: Use the `--continue-on-error` flag to continue running all playbooks even if some fail.

### Issue: Inventory file not found

**Solution**: Ensure the inventory file path is correct. You can use:
- Absolute path: `/Users/pawansi/dnac_ansible_workflows/inventory/mylab/hosts.yaml`
- Relative path from repo root: `inventory/mylab/hosts.yaml`

### Issue: Playbook or vars file not found

**Solution**: The script expects:
- Playbook in: `workflows/<workflow_name>/playbook/<workflow_name>.yml`
- Vars in: `workflows/<workflow_name>/vars/<workflow_name>_input.yml` or `<workflow_name>_inputs.yml`

If your files have different names, the script will try to find the first `.yml` file in those directories.

## Workflow Naming Patterns

The script looks for playbooks and vars files using these patterns:

**Playbook patterns** (in order of preference):
1. `playbook/<workflow_name>.yml`
2. `playbook/<workflow_name>_playbook.yml`
3. First `.yml` file in `playbook/` directory

**Vars file patterns** (in order of preference):
1. `vars/<workflow_name>_input.yml`
2. `vars/<workflow_name>_inputs.yml`
3. First file matching `*input*.yml` in `vars/` directory

## Integration with Ansible Runner UI

This script can be integrated with the Ansible Workflow Runner UI tool for batch execution through the web interface.

## License

Part of the `dnac_ansible_workflows` repository.
