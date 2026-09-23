# Ansible Workflow Runner

A lightweight web UI for browsing, editing, and executing Ansible playbooks from the `dnac_ansible_workflows` repository.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [User Flows](#user-flows)
  - [Flow 1: Run a Playbook with Default Settings](#flow-1-run-a-playbook-with-default-settings)
  - [Flow 2: Run a Playbook with Custom Vars](#flow-2-run-a-playbook-with-custom-vars)
  - [Flow 3: Build and Execute a Multi-Step Workflow](#flow-3-build-and-execute-a-multi-step-workflow)
  - [Flow 4: Validate and Edit Vars Before Running](#flow-4-validate-and-edit-vars-before-running)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Features

- **🚀 Run Playbook** — Select workflow and playbook, then launch with repo defaults or custom file paths
- **📝 YAML Editor** — Load and edit vars files in-browser with syntax highlighting (CodeMirror)
- **✅ Schema Validation** — Validate repo or custom vars files against their schema before running
- **📂 Custom File Browser** — Browse YAML vars or inventory files from the repo or your home directory
- **📡 Live Output** — Stream ansible-playbook output in real time with ANSI color support
- **🔗 Workflow Builder** — Chain multiple playbook runs into a sequential workflow; reorder steps with up/down controls
- **📊 Job History** — View past executions with status, duration, timestamps, and clickable detailed log links
- **📄 Job Detail Pages** — Open a shareable page for a single job with full Ansible output and raw log access
- **🛑 Cancel Support** — Stop running playbooks or entire workflows mid-execution
- **🔁 SDA port migration guided input** — Enter port migration values in the UI, validate them before execution, and generate the vars YAML without manually editing the file

---

## Prerequisites

Before running the Ansible Workflow Runner, ensure you have:

- **Python 3.10+** installed
- **Ansible** installed and `ansible-playbook` in your PATH, or set `ANSIBLE_PLAYBOOK_BIN` to the full binary path
- **Flask** and **Yamale** Python packages installed from `tools/ansible_runner/requirements.txt`
- **cisco.catalystcenter** Ansible collection and `catalystcentersdk` installed for live workflow runs
- A configured **inventory file** such as `inventory/demo_lab/hosts.yaml`
- Catalyst Center reachability from the machine running the UI
- For SDA port assignment migration, access to the source and destination devices in Catalyst Center and this repository's `workflows/sda_port_assignment_migration` workflow

---

## Quick Start

```bash
# Clone and enter the repository
git clone <repository-url>
cd <repository-directory>

# Create a virtual environment (recommended)
python3 -m venv tools/ansible_runner/.venv

# Install dependencies
tools/ansible_runner/.venv/bin/python -m pip install --upgrade pip
tools/ansible_runner/.venv/bin/python -m pip install -r tools/ansible_runner/requirements.txt
tools/ansible_runner/.venv/bin/python -m pip install catalystcentersdk

# Install the Catalyst Center Ansible collection used by the SDA migration workflow
ansible-galaxy collection install cisco.catalystcenter --collections-path "$PWD/collections" --force

# Optional: override Ansible/runtime paths if they are not already on PATH
export ANSIBLE_PLAYBOOK_BIN="$(command -v ansible-playbook)"
export ANSIBLE_COLLECTIONS_PATH="$PWD/collections:$PWD/.ansible/collections:$PWD:$HOME/.ansible/collections"

# Required for live SDA port migration runs and dropdown lookups; the launcher also prompts when these are not set
export HOSTIP="<catalyst-center-host-or-ip>"
export CATALYST_CENTER_USERNAME="<catalyst-center-username>"
export SWITCH_CLI_USERNAME="<switch-cli-username>"

# Optional when SNMPv3 credentials are needed by the generated inventory configuration
export SNMPV3_USERNAME="<snmpv3-username>"
export SNMPV3_AUTH_PROTOCOL="SHA"
export SNMPV3_PRIV_PROTOCOL="AES128"

# Start the server with Catalyst Center and switch credentials
tools/ansible_runner/start_switch_refresh_runner.sh

# Open in browser
http://127.0.0.1:5006
```

The startup banner prints the exact URL. By default, `start_switch_refresh_runner.sh` binds to `0.0.0.0:5006`, so local users open `http://127.0.0.1:5006`; remote users open `http://<runner-hostname-or-ip>:5006`. Override this with `RUNNER_HOST` and `RUNNER_PORT` before starting the script.

**Alternative Quick Start (using an existing Python environment):**
```bash
cd <repository-directory>
python3 -m pip install -r tools/ansible_runner/requirements.txt
python3 -m pip install catalystcentersdk
ansible-galaxy collection install cisco.catalystcenter --collections-path "$PWD/collections" --force
RUNNER_PORT=5006 python3 tools/ansible_runner/app.py
```

---

## User Flows

### Flow 1: Run a Playbook with Default Settings

**Use Case:** Execute a workflow playbook using the default vars and inventory files from the repository.

```mermaid
flowchart TD
   A[Start: Open Browser] --> B[Navigate to http://127.0.0.1:5006]
    B --> C[Click 'Run Playbook' Tab]
    C --> D[Search/Select Workflow]
    D --> E[Select Playbook from Dropdown]
    E --> F{Use Default Vars?}
    F -->|Yes| G[Keep 'Workflow vars' Selected]
    F -->|No| H[See Flow 2]
    G --> I{Use Default Inventory?}
    I -->|Yes| J[Keep 'Repo inventory' Selected]
    I -->|No| K[See Flow 2]
    J --> L[Optional: Set Verbosity Level]
    L --> M[Optional: Add Extra Args]
    M --> N[Review Selection Summary]
    N --> O[Click 'Launch Playbook']
    O --> P[View Live Output Stream]
    P --> Q{Execution Complete?}
    Q -->|Success| R[✅ View Success Status]
    Q -->|Failed| S[❌ View Error Details]
    Q -->|Running| T[Optional: Click Cancel]
    T --> U[Execution Cancelled]
    R --> V[End]
    S --> V
    U --> V
```

**Step-by-Step Instructions:**

1. **Open the Application**
   - Navigate to `http://127.0.0.1:5006` in your browser
   - You'll see the main dashboard with workflow statistics

2. **Select Workflow**
   - Click the **"Run Playbook"** tab
   - Use the search box to filter workflows (e.g., type "network_settings")
   - Select your desired workflow from the dropdown

3. **Select Playbook**
   - The playbook dropdown auto-populates with available playbooks
   - Select the playbook you want to run

4. **Configure Vars (Default)**
   - Keep **"Workflow vars"** button selected (default)
   - The default vars file from the workflow will be used

5. **Configure Inventory (Default)**
   - Keep **"Repo inventory"** button selected (default)
   - Select an inventory file from the dropdown (e.g., `inventory/demo_lab/hosts.yaml`)

6. **Optional Settings**
   - Set **Verbosity**: Choose from `-v`, `-vv`, `-vvv`, `-vvvv` for more detailed output
   - Add **Extra Arguments**: e.g., `--check --diff` for dry-run mode

7. **Launch**
   - Review the selection summary at the bottom
   - Click **"Launch playbook"**
   - Watch the live output stream with color-coded Ansible output

8. **Monitor Execution**
   - View real-time output in the terminal section
   - Status badge shows: Running → Completed/Failed
   - Click **"Cancel"** if needed to stop execution

---

### Flow 2: Run a Playbook with Custom Vars

**Use Case:** Execute a workflow playbook using a custom vars file from your home directory or a different location.

```mermaid
flowchart TD
    A[Start: From Flow 1 Step 4] --> B[Click 'Browse another file' Button]
    B --> C{Select Browse Root}
    C -->|Repository| D[Browse Repo Files]
    C -->|Home Directory| E[Browse Home Files]
    D --> F[Navigate to Desired Folder]
    E --> F
    F --> G[Click on YAML File]
    G --> H[File Selected and Loaded]
    H --> I{Need to Edit?}
    I -->|Yes| J[Click 'Open in editor' Button]
    I -->|No| K[Continue to Inventory]
    J --> L[Edit YAML in CodeMirror]
    L --> M[Press Cmd+S to Save]
    M --> N{Validate Before Running?}
    N -->|Yes| O[Click Validate Button]
    N -->|No| K
    O --> P{Validation Result}
    P -->|✅ Success| K
    P -->|❌ Failed| Q[Fix Errors in Editor]
    Q --> M
    K --> R[Configure Inventory]
    R --> S[Continue with Flow 1 Step 7]
```

**Step-by-Step Instructions:**

1. **Switch to Custom Vars**
   - After selecting workflow and playbook, click **"Browse another file"** under Vars File Source

2. **Browse for File**
   - Choose browse root: **Repository** or **Home**
   - Navigate through folders by clicking on directory names
   - Use breadcrumbs at the top to go back to parent folders
   - Click on a YAML file to select it

3. **Edit Vars (Optional)**
   - Click **"Open in editor"** button next to the selected file
   - The YAML editor opens with syntax highlighting
   - Make your changes
   - Press `Cmd+S` (Mac) or `Ctrl+S` (Windows/Linux) to save

4. **Validate Vars (Recommended)**
   - Click the **"✓ Validate"** button
   - If validation passes: ✅ Green success message
   - If validation fails: ❌ Red error message with details
   - Fix any errors and save again

5. **Continue with Inventory**
   - Select inventory (default or browse for custom)
   - Proceed to launch as in Flow 1

---

### SDA Port Assignment Migration: Guided Input

Select the `sda_port_assignment_migration` workflow and `sda_port_assignment_migration_playbook.yml`. The guided form accepts the fabric site, source and destination management IPs, generated config directory, cleanup setting, and interface mappings. It validates IPv4 values, required fields, absolute generated config path, and port mapping syntax before enabling YAML generation.

Use **Load ports** after entering the source and destination IPs. The Source Device dropdown is populated from SDA host-port assignments on the source device through `/api/host-port-assignments?ip=<source-ip>`. The Destination Device dropdown is populated from Catalyst Center inventory interfaces through `/api/device-interfaces?ip=<destination-ip>`. If the destination device is not in inventory yet, the UI offers expected `GigabitEthernet1/0/1` through `GigabitEthernet1/0/48` choices so the migration plan can still be generated before the device is onboarded.

Click **Add mapping** for each source-to-destination pair. The UI writes mappings as `source_interface=destination_interface` lines and generates `interface_mappings` in the selected vars file. Click **Generate vars YAML** after entering or changing workflow values. The generated file is saved to the selected workflow vars path, usually `workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml`, and is the file used by the next run.

For a live run from the UI, select the inventory file, usually `inventory/demo_lab/hosts.yaml` or your environment-specific inventory, then click **Launch playbook**. The same run can be submitted with the API:

```bash
curl -X POST http://127.0.0.1:5006/api/run \
   -H 'Content-Type: application/json' \
   --data '{
      "playbook": "workflows/sda_port_assignment_migration/playbook/sda_port_assignment_migration_playbook.yml",
      "inventory": "inventory/demo_lab/hosts.yaml",
      "vars_file": "workflows/sda_port_assignment_migration/vars/sda_port_assignment_migration_input.yml",
      "verbosity": "",
      "extra_args": "",
      "label": "sda_port_assignment_migration"
   }'
```

The Run Options panel shows runner readiness without displaying secret values. Dropdown lookup requires `HOSTIP`, `CATALYST_CENTER_USERNAME`, and `CATALYST_CENTER_PASSWORD`. Live migration runs also use the selected inventory and any workflow-specific credentials it references. If `SNMPV3_USERNAME` is set, the launcher prompts for SNMPv3 auth and privacy passwords; otherwise SNMPv3 password prompts are skipped. Syntax-check jobs remain available for validating generated input without changing devices.

### Flow 3: Build and Execute a Multi-Step Workflow

**Use Case:** Chain multiple playbook executions into a sequential workflow (e.g., configure network settings, then deploy fabric, then verify).

```mermaid
flowchart TD
    A[Start: Open Browser] --> B[Click 'Workflow Builder' Tab]
    B --> C[Click '+ Add Step' Button]
    C --> D[Modal Opens]
    D --> E[Search/Select Workflow]
    E --> F[Select Playbook]
    F --> G[Select Vars Source]
    G --> H[Select Inventory]
    H --> I[Click 'Add Step']
    I --> J[Step Added to List]
    J --> K{Add More Steps?}
    K -->|Yes| C
    K -->|No| L{Reorder Steps?}
    L -->|Yes| M[Use ▲/▼ Buttons]
    M --> L
    L -->|No| N[Review All Steps]
    N --> O[Click 'Run Workflow']
    O --> P[Step 1 Executes]
    P --> Q{Step 1 Success?}
    Q -->|Yes| R[Step 2 Executes]
    Q -->|No| S[❌ Workflow Stops]
    R --> T{Step 2 Success?}
    T -->|Yes| U[Continue Next Steps...]
    T -->|No| S
    U --> V[All Steps Complete]
    V --> W[✅ Workflow Success]
    S --> X[View Failed Step Output]
    W --> Y[End]
    X --> Y
```

**Step-by-Step Instructions:**

1. **Open Workflow Builder**
   - Click the **"Workflow Builder"** tab

2. **Add First Step**
   - Click **"+ Add Step"**
   - In the modal:
     - Search/select workflow
     - Select playbook
     - Choose vars source (workflow default or browse)
     - Select inventory
   - Click **"Add Step"**

3. **Add More Steps**
   - Repeat step 2 for each playbook you want to run
   - Steps will execute in the order they appear

4. **Reorder Steps (Optional)**
   - Use **▲** button to move a step up
   - Use **▼** button to move a step down
   - Use **✕** button to remove a step

5. **Execute Workflow**
   - Review all steps in the list
   - Click **"Run Workflow"**
   - Each step executes sequentially
   - If any step fails, the workflow stops
   - View combined output in the terminal below

6. **Monitor Progress**
   - Each step shows status: ⏳ Pending → 🔄 Running → ✅ Completed / ❌ Failed
   - Click **"Cancel Workflow"** to stop execution
   - Remaining steps will be marked as ⚪ Cancelled

---

### Flow 4: Validate and Edit Vars Before Running

**Use Case:** Review and modify vars file, validate against schema, then execute playbook.

```mermaid
flowchart TD
    A[Start: Select Workflow & Playbook] --> B[Select Vars File]
    B --> C[Click 'Open in editor']
    C --> D[YAML Editor Opens]
    D --> E[Review Current Values]
    E --> F{Need Changes?}
    F -->|Yes| G[Edit YAML Content]
    F -->|No| H[Click 'Validate']
    G --> I[Press Cmd+S to Save]
    I --> J[File Saved Confirmation]
    J --> H
    H --> K[Validation Runs]
    K --> L{Valid?}
    L -->|✅ Yes| M[Green Success Message]
    L -->|❌ No| N[Red Error Message]
    N --> O[Review Error Details]
    O --> P[Fix Issues in Editor]
    P --> I
    M --> Q[Close Editor or Keep Open]
    Q --> R[Select Inventory]
    R --> S[Launch Playbook]
    S --> T[View Output]
```

**Step-by-Step Instructions:**

1. **Load Vars in Editor**
   - After selecting workflow, playbook, and vars file
   - Click **"Open in editor"** button (📝 icon)
   - The CodeMirror editor opens with YAML syntax highlighting

2. **Review and Edit**
   - Review the current configuration
   - Make necessary changes (e.g., update IP addresses, credentials, settings)
   - The editor shows line numbers and auto-indents

3. **Save Changes**
   - Press `Cmd+S` (Mac) or `Ctrl+S` (Windows/Linux)
   - Or click the **"Save"** button in the editor header
   - Toast notification confirms save

4. **Validate Against Schema**
   - Click the **"✓ Validate"** button
   - The system runs Yamale validation against the workflow's schema
   - Results appear below the vars file selector

5. **Handle Validation Results**
   - **✅ Success**: Green message "Validation completed"
   - **❌ Failure**: Red message with specific errors
     - Example: `line 15: 'ip_address' is required`
     - Fix the errors in the editor
     - Save and validate again

6. **Proceed to Launch**
   - Once validation passes, continue with inventory selection
   - Launch the playbook with confidence

---

## Architecture

```
tools/ansible_runner/
├── app.py              # Flask backend — API + process management
├── requirements.txt    # Python dependencies (flask, yamale)
├── README.md           # This file
├── .venv/              # Virtual environment (created by user)
└── templates/
    ├── index.html      # Main runner frontend (Tailwind + CodeMirror)
    └── job.html        # Dedicated job log page
```

### Backend (`app.py`)
- **Workflow Discovery**: Scans `workflows/` directory for playbooks, vars, schemas
- **File Browser**: Serves YAML files from repo and home directory with path validation
- **File Operations**: Read/write YAML files with security checks
- **Schema Validation**: Uses Yamale to validate vars against workflow schemas
- **Process Management**: Runs `ansible-playbook` via subprocess with live streaming
- **Job Tracking**: Manages job lifecycle (queued → running → completed/failed/cancelled)
- **SSE Streaming**: Server-Sent Events for real-time output with ANSI color preservation

### Frontend (`index.html`)
- **Single HTML File**: No build step required, runs directly in browser
- **Tailwind CSS**: Modern UI styling via CDN
- **CodeMirror 5**: YAML editor with syntax highlighting via CDN
- **Vanilla JavaScript**: All interactivity without frameworks
- **Three Main Tabs**:
  1. **Run Playbook**: Single playbook execution with guided form
  2. **Workflow Builder**: Multi-step workflow creation and execution
  3. **Job History**: View past executions with status, timing, and direct log links

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the main HTML interface |
| `GET` | `/jobs/<id>` | Serve the dedicated job detail page |
| `GET` | `/api/workflows` | List all workflow directories with their playbooks, vars, and schemas |
| `GET` | `/api/inventories` | List all inventory YAML files from `inventory/` directory |
| `GET` | `/api/fs?root=<repo\|home>&path=<path>` | Browse YAML files under the repo or home directory |
| `GET` | `/api/file?path=<rel>` | Read a file's content (repo or home directory) |
| `PUT` | `/api/file` | Save file content: `{path, content}` |
| `POST` | `/api/validate` | Validate vars against schema: `{schema, data}` |
| `POST` | `/api/run` | Start a playbook run: `{inventory, playbook, vars_file, verbosity, extra_args, label}` |
| `GET` | `/api/run/<id>/stream` | SSE stream of job output (real-time, supports `start=<line>` offset) |
| `POST` | `/api/run/<id>/cancel` | Cancel a running job |
| `GET` | `/api/jobs` | List all jobs with status, duration, and timing |
| `GET` | `/api/jobs/<id>` | Get a single job with metadata and captured log lines |
| `GET` | `/api/jobs/<id>/log` | Open the captured job log as plain text |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+S` / `Ctrl+S` | Save the file currently open in the editor |
| `Escape` | Close modal dialogs |
| `Cmd+1` / `Ctrl+1` | Switch to Run Playbook tab |
| `Cmd+2` / `Ctrl+2` | Switch to Workflow Builder tab |
| `Cmd+3` / `Ctrl+3` | Switch to Job History tab |

---

## Troubleshooting

### Server won't start
- **Issue**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Install dependencies: `pip install -r tools/ansible_runner/requirements.txt`

### Ansible playbook not found
- **Issue**: `ansible-playbook: command not found`
- **Solution**: Install Ansible: `pip install ansible` or `brew install ansible`

### Validation fails
- **Issue**: Schema validation errors
- **Solution**: Review the error message, fix the vars file, and validate again

### Can't access custom files
- **Issue**: "Access denied" when browsing files
- **Solution**: Ensure files are within the repository or your home directory

---

## License

This tool is part of the `dnac_ansible_workflows` repository. Refer to the main repository license.
