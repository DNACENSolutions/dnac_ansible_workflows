import os

def create_directory_structure(root_dir):
    """
    Creates the directory and file structure based on the provided example,
    and populates playbook and README.md files with basic templates.
    If some files or directories already exist, they are ignored and only missing ones are created.
    """

    # Ensure we are in the 'workflows' directory
    cwd = os.getcwd()
    if os.path.basename(cwd) != "workflows":
        # Try to move to 'workflows' directory if it exists in the current path
        workflows_path = os.path.join(cwd, "workflows")
        if os.path.isdir(workflows_path):
            os.chdir(workflows_path)
            print(f"Changed working directory to: {workflows_path}")
        else:
            raise FileNotFoundError("The 'workflows' directory does not exist in the current path.")

    # Create the root directory if it doesn't exist
    os.makedirs(root_dir, exist_ok=True)

    # Define subdirectories
    subdirectories = ["images", "jinja_template", "playbook", "schema", "vars"]
    for subdir in subdirectories:
        os.makedirs(os.path.join(root_dir, subdir), exist_ok=True)

    # Define files to create in each directory
    files = {
        "images": [f"{root_dir}.png"],
        "playbook": [f"{root_dir}_playbook.yml", f"delete_{root_dir}_playbook.yml"],
        "schema": [f"{root_dir}_schema.yml"],
        "vars": [f"{root_dir}_inputs.yml", f"jinja_{root_dir}_inputs.yml"],
        ".": ["description.json", "README.md"]  # Files in the root directory
    }

    # Templates
    playbook_template = lambda name: f"""---
- name: {name.replace('_', ' ').capitalize()}
  hosts: all
  gather_facts: false
  tasks:
    - name: Example task
      debug:
        msg: "This is a placeholder for the {name} playbook."
"""
    readme_template = f"""# {root_dir.replace('_', ' ').title()}

This module was generated using the workflow generator.

## Structure

- **images/**: Image assets
- **jinja_template/**: Jinja templates
- **playbook/**: Ansible playbooks
- **schema/**: Schema definitions
- **vars/**: Variable files

## Usage

Edit the playbooks in `playbook/` and fill in the required tasks for your workflow.

## Generated Files

- `playbook/{root_dir}_playbook.yml`
- `playbook/delete_{root_dir}_playbook.yml`
- `README.md`
"""

    for subdir, file_list in files.items():
        for filename in file_list:
            filepath = os.path.join(root_dir, subdir, filename) if subdir != "." else os.path.join(root_dir, filename)
            # Only create the file if it does not exist
            if not os.path.exists(filepath):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    # Write templates for specific files
                    if subdir == "playbook" and filename.endswith("_playbook.yml"):
                        f.write(playbook_template(filename.replace(".yml", "")))
                    elif filename == "README.md":
                        f.write(readme_template)
                    else:
                        # Create empty files for others
                        pass
                print(f"Created file: {filepath}")

if __name__ == "__main__":
    while True:
        directory_name = input("Enter the directory name to create (e.g., lan_automation) or Enter to exit: ")
        if directory_name:
            create_directory_structure(directory_name)
            print(f"Directory structure for '{directory_name}' created successfully.")
        else:
            print("Directory name cannot be empty. Please try again.")
            break
# End of script