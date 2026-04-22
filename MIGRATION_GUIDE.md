# Migration Guide: cisco.catalystcenter → cisco.catalystcenter

This guide provides step-by-step instructions for migrating from the `cisco.catalystcenter` Ansible collection to the `cisco.catalystcenter` collection.

## Overview

The `cisco.catalystcenter` collection is the successor to `cisco.catalystcenter`, providing improved functionality and alignment with the Catalyst Center product branding.

### Key Changes

| Component | Old (cisco.catalystcenter) | New (cisco.catalystcenter) |
|-----------|------------------|----------------------------|
| **Collection Name** | `cisco.catalystcenter` | `cisco.catalystcenter` |
| **Python SDK** | `catalystcentersdk` | `catalystcentersdk` |
| **Variable Prefix** | `dnac_*` | `catalystcenter_*` |
| **Module Names** | `cisco.catalystcenter.<module>` | `cisco.catalystcenter.<module>` |

## Migration Steps

### Step 1: Backup Your Repository

```bash
# Create a backup branch
cd /path/to/dnac_ansible_workflows
git checkout -b backup-before-migration
git push origin backup-before-migration

# Return to main branch
git checkout main
```

### Step 2: Run Dry-Run Migration

```bash
# Test the migration without making changes
./tools/migrate_to_catalystcenter.sh --dry-run
```

Review the output to see which files will be modified.

### Step 3: Execute Migration

```bash
# Run the actual migration
./tools/migrate_to_catalystcenter.sh
```

This script will automatically update:
- ✅ Collection references (`cisco.catalystcenter` → `cisco.catalystcenter`)
- ✅ Module names in playbooks
- ✅ Variable names in playbooks and inventory files
- ✅ Python SDK references (`catalystcentersdk` → `catalystcentersdk`)
- ✅ Documentation and README files
- ✅ Requirements files

### Step 4: Update Python Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Uninstall old SDK
pip uninstall catalystcentersdk -y

# Install new SDK
pip install catalystcentersdk

# Update requirements.txt if needed
sed -i '' 's/catalystcentersdk/catalystcentersdk/g' requirements.txt
```

### Step 5: Install New Ansible Collection

```bash
# Uninstall old collection (optional)
ansible-galaxy collection list | grep cisco.catalystcenter

# Install new collection
ansible-galaxy collection install cisco.catalystcenter --force

# Verify installation
ansible-galaxy collection list | grep cisco.catalystcenter
```

### Step 6: Update Inventory Files

Your inventory files will be automatically updated by the migration script. Verify the changes:

**Before:**
```yaml
catalyst_center_hosts:
  hosts:
    catalyst_center_main:
      catalystcenter_host: "10.10.10.10"
      catalystcenter_username: "{{ vault_catalyst_center_username }}"
      catalystcenter_password: "{{ vault_catalyst_center_password }}"
      catalystcenter_port: 443
      catalystcenter_verify: false
      catalystcenter_version: "2.3.7.9"
      catalystcenter_debug: true
      catalystcenter_log: true
      catalystcenter_log_level: INFO
```

**After:**
```yaml
catalyst_center_hosts:
  hosts:
    catalyst_center_main:
      catalystcenter_host: "10.10.10.10"
      catalystcenter_username: "{{ vault_catalyst_center_username }}"
      catalystcenter_password: "{{ vault_catalyst_center_password }}"
      catalystcenter_port: 443
      catalystcenter_verify: false
      catalystcenter_version: "2.3.7.9"
      catalystcenter_debug: true
      catalystcenter_log: true
      catalystcenter_log_level: INFO
```

### Step 7: Review Playbook Changes

Playbooks will be automatically updated. Example changes:

**Before:**
```yaml
- name: Discover devices
  cisco.catalystcenter.discovery_workflow_manager:
    catalystcenter_host: "{{ catalystcenter_host }}"
    catalystcenter_username: "{{ catalystcenter_username }}"
    catalystcenter_password: "{{ catalystcenter_password }}"
    catalystcenter_verify: "{{ catalystcenter_verify }}"
    catalystcenter_port: "{{ catalystcenter_port }}"
    catalystcenter_version: "{{ catalystcenter_version }}"
    catalystcenter_debug: "{{ catalystcenter_debug }}"
    catalystcenter_log: true
    catalystcenter_log_level: "{{ catalystcenter_log_level }}"
    state: merged
    config: ...
```

**After:**
```yaml
- name: Discover devices
  cisco.catalystcenter.discovery_workflow_manager:
    catalystcenter_host: "{{ catalystcenter_host }}"
    catalystcenter_username: "{{ catalystcenter_username }}"
    catalystcenter_password: "{{ catalystcenter_password }}"
    catalystcenter_verify: "{{ catalystcenter_verify }}"
    catalystcenter_port: "{{ catalystcenter_port }}"
    catalystcenter_version: "{{ catalystcenter_version }}"
    catalystcenter_debug: "{{ catalystcenter_debug }}"
    catalystcenter_log: true
    catalystcenter_log_level: "{{ catalystcenter_log_level }}"
    state: merged
    config: ...
```

### Step 8: Test in Lab Environment

```bash
# Test a simple workflow
ansible-playbook \
  -i inventory/mylab/hosts.yaml \
  workflows/site_hierarchy/playbook/site_hierarchy_playbook.yml \
  --extra-vars VARS_FILE_PATH=workflows/site_hierarchy/vars/site_hierarchy_design_vars.yml \
  --vault-password-file .vault_pass \
  --check

# If check mode passes, run without --check
ansible-playbook \
  -i inventory/mylab/hosts.yaml \
  workflows/site_hierarchy/playbook/site_hierarchy_playbook.yml \
  --extra-vars VARS_FILE_PATH=workflows/site_hierarchy/vars/site_hierarchy_design_vars.yml \
  --vault-password-file .vault_pass
```

### Step 9: Review and Commit Changes

```bash
# Review all changes
git status
git diff

# Add all changes
git add -A

# Commit with descriptive message
git commit -m "Migrate from cisco.catalystcenter to cisco.catalystcenter collection

- Updated all playbooks to use cisco.catalystcenter collection
- Migrated variable names from dnac_* to catalystcenter_*
- Updated Python SDK from catalystcentersdk to catalystcentersdk
- Updated documentation and README files
- Updated requirements.txt

Tested in lab environment successfully."

# Push to repository
git push origin main
```

## Manual Migration (Alternative)

If you prefer to migrate manually or need to migrate specific files:

### 1. Update Collection References

```bash
# Find and replace in all YAML files
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i '' 's/cisco\.dnac/cisco.catalystcenter/g' {} +
```

### 2. Update Variable Names

```bash
# Update all dnac_* variables to catalystcenter_*
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i '' 's/catalystcenter_host/catalystcenter_host/g' {} +
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i '' 's/catalystcenter_username/catalystcenter_username/g' {} +
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i '' 's/catalystcenter_password/catalystcenter_password/g' {} +
# ... repeat for all variables
```

### 3. Update Documentation

```bash
# Update README and other markdown files
find . -type f -name "*.md" -exec sed -i '' 's/cisco\.dnac/cisco.catalystcenter/g' {} +
find . -type f -name "*.md" -exec sed -i '' 's/catalystcentersdk/catalystcentersdk/g' {} +
```

## Troubleshooting

### Issue: Module not found after migration

**Solution:**
```bash
# Verify collection is installed
ansible-galaxy collection list | grep cisco.catalystcenter

# Reinstall if needed
ansible-galaxy collection install cisco.catalystcenter --force
```

### Issue: Python SDK import errors

**Solution:**
```bash
# Verify SDK is installed
pip list | grep catalystcentersdk

# Reinstall if needed
pip uninstall catalystcentersdk catalystcentersdk -y
pip install catalystcentersdk
```

### Issue: Variable not defined errors

**Solution:**
Check that all variable references in your inventory and playbooks have been updated from `dnac_*` to `catalystcenter_*`.

```bash
# Search for any remaining dnac_ references
grep -r "catalystcenter_host\|catalystcenter_username\|catalystcenter_password" workflows/ inventory/
```

### Issue: Playbook fails with authentication errors

**Solution:**
Ensure your vault file variables match the new naming convention if you're using Ansible Vault:

```yaml
# vault.yml should still use these names (they're your custom variables)
vault_catalyst_center_username: admin
vault_catalyst_center_password: YourPassword

# But inventory should reference them with catalystcenter_* parameters
catalystcenter_username: "{{ vault_catalyst_center_username }}"
catalystcenter_password: "{{ vault_catalyst_center_password }}"
```

## Compatibility

| Catalyst Center Version | cisco.catalystcenter Collection | catalystcentersdk |
|------------------------|----------------------------------|-------------------|
| 2.3.7.6 | latest | latest |
| 2.3.7.9 | latest | latest |
| 2.3.7.10 | latest | latest |
| 3.1.6.x | latest | latest |

## Additional Resources

- [cisco.catalystcenter Collection Documentation](https://galaxy.ansible.com/ui/repo/published/cisco/catalystcenter/)
- [Catalyst Center SDK Documentation](https://pypi.org/project/catalystcentersdk/)
- [Ansible Collection Migration Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_migrating.html)

## Rollback Procedure

If you need to rollback the migration:

```bash
# Switch to backup branch
git checkout backup-before-migration

# Or reset to previous commit
git log --oneline -10  # Find the commit before migration
git reset --hard <commit-hash>

# Reinstall old dependencies
pip uninstall catalystcentersdk -y
pip install catalystcentersdk
ansible-galaxy collection install cisco.catalystcenter --force
```

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [cisco.catalystcenter collection issues](https://github.com/cisco-en-programmability/catalystcenter-ansible/issues)
3. Open an issue in this repository with details about your migration problem
