import os
import sys
import argparse
import json
import re
from typing import Dict, List, Optional
from pathlib import Path

def validate_directory_name(name: str) -> bool:
    """
    Validates directory name follows naming conventions.
    
    Args:
        name: Directory name to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Check for empty or whitespace-only names
    if not name or not name.strip():
        return False
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-z0-9_-]+$', name):
        return False
    
    # Check length (reasonable limit)
    if len(name) > 100:
        return False
    
    return True


def generate_playbook_content(name: str) -> str:
    """
    Generate playbook template content following the standard workflow pattern.
    
    Args:
        name: Playbook name (e.g., 'lan_automation_playbook')
    
    Returns:
        Formatted playbook YAML content
    """
    # Extract workflow name from playbook name (remove _playbook or delete_ prefix)
    workflow_name = name.replace('_playbook', '').replace('delete_', '')
    display_name = workflow_name.replace('_', ' ').replace('-', ' ').title()
    
    # Determine if this is a delete playbook
    is_delete = 'delete_' in name
    state = 'deleted' if is_delete else 'merged'
    action = 'Delete' if is_delete else 'Create or Update'
    
    # Generate config variable name (e.g., lan_automation_details)
    config_var = f"{workflow_name}_details"
    
    return f"""---
- name: {display_name} Playbook
  hosts: catalyst_center_hosts
  connection: local
  gather_facts: no
  vars_files:
    - "{{{{ VARS_FILE_PATH }}}}"
  vars:
    state: {state}
    catalyst_center_login: &catalyst_center_login
      dnac_host: "{{{{ catalyst_center_host | default(dnac_host) }}}}"
      dnac_username: "{{{{ catalyst_center_username | default(dnac_username) }}}}"
      dnac_password: "{{{{ catalyst_center_password | default(dnac_password) }}}}"
      dnac_version: "{{{{ catalyst_center_version  | default(dnac_version) }}}}"
      dnac_port: "{{{{ catalyst_center_port | default(443) }}}}"
      dnac_verify: "{{{{ catalyst_center_verify | default(dnac_verify) }}}}"
      config_verify: "{{{{ catalyst_center_config_verify | default(False) }}}}"
      dnac_debug: "{{{{ catalyst_center_debug | default(False) }}}}"
      dnac_log: "{{{{ catalyst_center_log | default(False) }}}}"
      dnac_log_level: "{{{{ catalyst_center_log_level | default('INFO') }}}}"
      dnac_log_file_path: "{{{{ catalyst_center_log_file_path |  default(omit) }}}}"
      dnac_log_append: "{{{{ catalyst_center_log_append |  default(False) }}}}"
      dnac_api_task_timeout: "{{{{ catalyst_center_api_task_timeout |  default(1200) }}}}"
      
  tasks:
    # Include the variables file {{{{ VARS_FILE_PATH }}}} for the playbook
    - name: {display_name} Playbook start time
      set_fact:
        long_op_start: "{{{{ now() }}}}"

    - name: load password file
      include_vars:
        file: "{{{{ passwords_file }}}}"
      when: jinjatemplate is defined and jinjatemplate is true and passwords_file is defined

    # load template jinja file
    - name: Create Template
      template: 
        src: "{{{{ jinjatemplate_file }}}}"
        dest: ../tmp/template_generated_file.yaml
      when:  jinjatemplate is defined and jinjatemplate is true and jinjatemplate_file is defined
    
    # Include the variables file ../tmp/template_generated_file.yaml for the playbook
    - name: Include the variables file ../tmp/template_generated_file.yaml for the playbook
      include_vars:
        file: ../tmp/template_generated_file.yaml
      when: jinjatemplate is defined

    # {action} {display_name} with provided details in "{{{{ VARS_FILE_PATH }}}}"
    - name: {action} {display_name} with provided details in "{{{{ VARS_FILE_PATH }}}}"
      cisco.dnac.{workflow_name}_workflow_manager:
        <<: *catalyst_center_login
        state: "{{{{ state }}}}"
        config: "{{{{ {config_var} }}}}"
      when: {config_var} is defined and {config_var} | length > 0

    - name: delete the tmp files
      ansible.builtin.command: rm ../tmp/template_generated_file.yaml
      when : jinjatemplate is defined and jinjatemplate is true and jinjatemplate_file is defined

    - name: {display_name} Playbook end time
      set_fact:
        long_op_end: "{{{{ now() }}}}"
    
    - name: Print the run time
      debug:
        msg: "{display_name} Playbook run time: {{{{ long_op_start }}}}, end: {{{{ long_op_end }}}}"
  
  # run command module to find python version
  post_tasks:
    - name: run command module to find python version
      ansible.builtin.command: which python
      register: ansible_play_path
      delegate_to: catalyst_center_hosts
      connection: local
"""


def generate_description_json(name: str) -> Dict:
    """
    Generate description.json structure.
    
    Args:
        name: Workflow name
    
    Returns:
        Description dictionary
    """
    display_name = name.replace('_', ' ').replace('-', ' ').title()
    return {
        "name": display_name,
        "description": f"Workflow for {display_name} operations in Cisco Catalyst Center",
        "version": "1.0.0",
        "author": "Network Automation Team",
        "tags": ["catalyst-center", "dnac", "automation"],
        "category": "network-management",
        "requirements": {
            "ansible": ">=2.9",
            "python": ">=3.8",
            "cisco.dnac": ">=6.0.0"
        },
        "playbooks": {
            "main": f"playbook/{name}_playbook.yml",
            "delete": f"playbook/delete_{name}_playbook.yml"
        },
        "variables": {
            "inputs": f"vars/{name}_inputs.yml",
            "jinja_inputs": f"vars/jinja_{name}_inputs.yml"
        },
        "schema": f"schema/{name}_schema.yml"
    }


def create_directory_structure(root_dir: str, force_overwrite: bool = False, dry_run: bool = False) -> bool:
    """
    Creates the directory and file structure for a workflow.
    Populates playbook, README.md, and description.json files with templates.
    
    Args:
        root_dir: Name of the root directory to create
        force_overwrite: If True, overwrite existing files
        dry_run: If True, only show what would be created without actually creating
    
    Returns:
        True if successful, False otherwise
    """
    # Validate directory name
    if not validate_directory_name(root_dir):
        print(f"Error: Invalid directory name '{root_dir}'.")
        print("Directory name must:")
        print("  - Contain only lowercase letters, numbers, underscores, or hyphens")
        print("  - Not be empty")
        print("  - Be less than 100 characters")
        return False

    try:
        # Ensure we are in the 'workflows' directory
        cwd = Path.cwd()
        if cwd.name != "workflows":
            # Try to move to 'workflows' directory if it exists
            workflows_path = cwd / "workflows"
            if workflows_path.is_dir():
                os.chdir(workflows_path)
                print(f"Changed working directory to: {workflows_path}")
            else:
                print(f"Error: The 'workflows' directory does not exist in {cwd}")
                print("Please run this script from the project root or workflows directory.")
                return False

        # Check if directory already exists
        target_dir = Path(root_dir)
        if target_dir.exists() and not force_overwrite:
            print(f"Warning: Directory '{root_dir}' already exists.")
            print("Use --force to overwrite existing files or choose a different name.")
            return False

        if dry_run:
            print(f"\n[DRY RUN] Would create directory: {target_dir}")
        else:
            # Create the root directory
            target_dir.mkdir(exist_ok=True)
            print(f"Created directory: {target_dir}")

        # Define subdirectories
        subdirectories = ["images", "jinja_template", "playbook", "schema", "vars"]
        for subdir in subdirectories:
            subdir_path = target_dir / subdir
            if dry_run:
                print(f"[DRY RUN] Would create subdirectory: {subdir_path}")
            else:
                subdir_path.mkdir(exist_ok=True)

        # Define files to create in each directory
        files = {
            "images": [f"{root_dir}.png"],
            "playbook": [f"{root_dir}_playbook.yml", f"delete_{root_dir}_playbook.yml"],
            "schema": [f"{root_dir}_schema.yml"],
            "vars": [f"{root_dir}_inputs.yml", f"jinja_{root_dir}_inputs.yml"],
            ".": ["description.json", "README.md"]  # Files in the root directory
        }

        # README template
        display_name = root_dir.replace('_', ' ').replace('-', ' ').title()
        readme_template = f"""# {display_name}

This workflow was generated using the workflow generator.

## Overview

This workflow provides automation for {display_name} operations in Cisco Catalyst Center.

## Directory Structure

- **images/**: Documentation images and diagrams
- **jinja_template/**: Jinja2 templates for dynamic configuration
- **playbook/**: Ansible playbooks for workflow execution
- **schema/**: YAML schema definitions for validation
- **vars/**: Variable files and input examples

## Files

### Playbooks
- `playbook/{root_dir}_playbook.yml` - Main workflow playbook
- `playbook/delete_{root_dir}_playbook.yml` - Deletion/cleanup playbook

### Configuration
- `vars/{root_dir}_inputs.yml` - Input variables
- `vars/jinja_{root_dir}_inputs.yml` - Jinja template inputs
- `schema/{root_dir}_schema.yml` - Validation schema

### Documentation
- `description.json` - Workflow metadata
- `README.md` - This file

## Usage

1. Update the input variables in `vars/{root_dir}_inputs.yml`
2. Run the playbook:
   ```bash
   ansible-playbook playbook/{root_dir}_playbook.yml -e var_file={root_dir}_inputs.yml
   ```

## Requirements

- Ansible >= 2.9
- Python >= 3.8
- cisco.dnac collection >= 6.0.0

## Notes

- Review and customize the playbooks according to your requirements
- Update the schema file for proper input validation
- Add documentation images to the `images/` directory
"""

        # Create files
        created_count = 0
        skipped_count = 0
        
        for subdir, file_list in files.items():
            for filename in file_list:
                if subdir == ".":
                    filepath = target_dir / filename
                else:
                    filepath = target_dir / subdir / filename
                
                # Check if file exists
                if filepath.exists() and not force_overwrite:
                    if dry_run:
                        print(f"[DRY RUN] Would skip existing file: {filepath}")
                    else:
                        print(f"Skipped existing file: {filepath}")
                    skipped_count += 1
                    continue
                
                if dry_run:
                    print(f"[DRY RUN] Would create file: {filepath}")
                    created_count += 1
                else:
                    # Ensure parent directory exists
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write content based on file type
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            if subdir == "playbook" and filename.endswith("_playbook.yml"):
                                # Generate playbook content
                                f.write(generate_playbook_content(filename.replace(".yml", "")))
                            elif filename == "README.md":
                                f.write(readme_template)
                            elif filename == "description.json":
                                # Generate description.json with proper structure
                                json.dump(generate_description_json(root_dir), f, indent=2)
                                f.write('\n')  # Add newline at end
                            else:
                                # Create empty placeholder files
                                if filename.endswith('.yml'):
                                    f.write("---\n# Add your configuration here\n")
                        
                        print(f"Created file: {filepath}")
                        created_count += 1
                    except IOError as e:
                        print(f"Error creating file {filepath}: {e}")
                        return False
        
        # Print summary
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
        print(f"  Created: {created_count} files")
        if skipped_count > 0:
            print(f"  Skipped: {skipped_count} existing files")
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_mode():
    """Run the tool in interactive mode."""
    print("\n=== Workflow Generator - Interactive Mode ===")
    print("Enter workflow names to create directory structures.")
    print("Press Enter with no input to exit.\n")
    
    while True:
        directory_name = input("Enter workflow name (or press Enter to exit): ").strip()
        
        if not directory_name:
            print("\nExiting workflow generator.")
            break
        
        success = create_directory_structure(directory_name)
        if success:
            print(f"\n✓ Workflow structure for '{directory_name}' created successfully.\n")
        else:
            print(f"\n✗ Failed to create workflow structure for '{directory_name}'.\n")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate workflow directory structure for Cisco Catalyst Center automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Interactive mode
  python workflow_gen.py
  
  # Create a workflow
  python workflow_gen.py lan_automation
  
  # Create multiple workflows
  python workflow_gen.py lan_automation device_discovery
  
  # Dry run to see what would be created
  python workflow_gen.py --dry-run lan_automation
  
  # Force overwrite existing files
  python workflow_gen.py --force lan_automation
"""
    )
    
    parser.add_argument(
        'workflows',
        nargs='*',
        help='Name(s) of workflow(s) to create'
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Overwrite existing files'
    )
    
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    args = parser.parse_args()
    
    # If no workflows specified, run in interactive mode
    if not args.workflows:
        interactive_mode()
        return 0
    
    # Process each workflow
    success_count = 0
    failed_count = 0
    
    for workflow_name in args.workflows:
        print(f"\n{'='*60}")
        print(f"Processing: {workflow_name}")
        print('='*60)
        
        success = create_directory_structure(
            workflow_name,
            force_overwrite=args.force,
            dry_run=args.dry_run
        )
        
        if success:
            success_count += 1
            status = "✓ SUCCESS" if not args.dry_run else "✓ DRY RUN COMPLETE"
            print(f"\n{status}: Workflow '{workflow_name}'")
        else:
            failed_count += 1
            print(f"\n✗ FAILED: Workflow '{workflow_name}'")
    
    # Print overall summary
    if len(args.workflows) > 1:
        print(f"\n{'='*60}")
        print("Overall Summary:")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {failed_count}")
        print('='*60)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())