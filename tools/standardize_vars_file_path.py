#!/usr/bin/env python3
"""
Standardize VARS_FILE_PATH handling across workflow playbooks.

This update removes unconditional vars_files usage, adds guarded include_vars
loading, and makes task labels safe when VARS_FILE_PATH is omitted and inputs
come from inventory or host variables instead.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path("/Users/pawansi/dnac_ansible_workflows")
WORKFLOWS_DIR = REPO_ROOT / "workflows"

TARGET_PLAYBOOKS = sorted(WORKFLOWS_DIR.glob("*/playbook/*.yml"))

SAFE_INPUT_LABEL = "{{ VARS_FILE_PATH | default('inventory / host variables') }}"

IGNORE_VARS = {
    "VARS_FILE_PATH",
    "SWIM_VARS_FILE_PATH",
    "CSV_FILE_PATH",
    "STATE",
    "absolute_path",
    "all_devices",
    "all_devices_uap",
    "all_devices_ws",
    "ansible_date_time",
    "ansible_env",
    "ansible_host",
    "ansible_network_os",
    "ansible_password",
    "ansible_play_path",
    "ansible_user",
    "ansible_connection",
    "auth_response",
    "authentication",
    "catalyst_center_api_task_timeout",
    "catalyst_center_config_verify",
    "catalyst_center_debug",
    "catalyst_center_host",
    "catalyst_center_log",
    "catalyst_center_log_append",
    "catalyst_center_log_file_path",
    "catalyst_center_log_level",
    "catalyst_center_password",
    "catalyst_center_port",
    "catalyst_center_task_poll_interval",
    "catalyst_center_task_timeout",
    "catalyst_center_username",
    "catalyst_center_verify",
    "catalyst_center_version",
    "catalystcenter_api_task_timeout",
    "catalystcenter_debug",
    "catalystcenter_host",
    "catalystcenter_log",
    "catalystcenter_log_append",
    "catalystcenter_log_file_path",
    "catalystcenter_log_level",
    "catalystcenter_password",
    "catalystcenter_port",
    "catalystcenter_username",
    "catalystcenter_verify",
    "catalystcenter_version",
    "completion_time",
    "config_gen_end",
    "config_gen_start",
    "credentials",
    "dnac_auth_token",
    "dnac_url",
    "generated_config_dir",
    "hostvars",
    "inventory_hostname",
    "item",
    "jinjatemplate",
    "jinjatemplate_file",
    "long_op_duration",
    "long_op_end",
    "long_op_start",
    "maintenance_payload",
    "maintenance_state",
    "merged_data",
    "network_devices_output",
    "now",
    "omit",
    "orig_data_content",
    "passwords_file",
    "playbook_dir",
    "playbook_runtime_seconds",
    "query",
    "range",
    "resolved_vars_file_path",
    "result_fabric_device_info",
    "result_network_devices_info",
    "stage_configured_counts",
    "start_time",
    "state",
    "vars_file_candidates",
    "vars_file_path_resolved",
}

UNDESIRABLE_SUFFIXES = (
    "_append",
    "_content",
    "_count",
    "_counts",
    "_duration",
    "_end",
    "_file",
    "_files",
    "_index",
    "_lines",
    "_output",
    "_outputs",
    "_path",
    "_paths",
    "_payload",
    "_response",
    "_responses",
    "_result",
    "_results",
    "_start",
    "_stats",
    "_summary",
    "_totals",
)

PREFERRED_SUFFIX_SCORES = (
    ("_details", 120),
    ("_config", 115),
    ("_settings", 110),
    ("_input", 105),
    ("_inputs", 105),
    ("_migration", 100),
    ("_policies", 100),
    ("_profiles", 95),
    ("_devices", 92),
    ("_sites", 90),
)

MANUAL_VALIDATIONS = {
    "workflows/ansible_vault_update/playbook/ansible_vault_update_playbook.yml": {
        "mode": "all",
        "vars": ["passwords_details"],
    },
    "workflows/ansible_vault_update/playbook/delete_ansible_vault_update_playbook.yml": {
        "mode": "all",
        "vars": ["passwords_details"],
    },
    "workflows/e2e_lan_automationed_site_bringup/playbook/lan_automation_site_bringup.yml": {
        "mode": "any",
        "vars": [
            "design_sites",
            "device_credentials",
            "network_settings",
            "discovery_details",
            "lan_automation",
            "update_devices_role",
            "provision_devices",
        ],
    },
    "workflows/e2e_network_devices_sw_upgrade/playbook/e2e_network_device_sw_upgrade_playbook.yml": {
        "mode": "all",
        "vars": ["swim_details"],
    },
    "workflows/e2e_nw_design_and_inventory/playbook/e2e_network_inventory_playbook.yml": {
        "mode": "any",
        "vars": [
            "design_sites",
            "device_credentials",
            "discovery_details",
            "inventory_details",
        ],
    },
    "workflows/e2e_sda_onboarding/playbook/e2e_sda_playbook.yml": {
        "mode": "none",
        "vars": [],
    },
    "workflows/inventory/playbook/delete_inventory_playbook.yml": {
        "mode": "all",
        "vars": ["inventory_details"],
    },
    "workflows/inventory/playbook/inventory_playbook.yml": {
        "mode": "all",
        "vars": ["inventory_details"],
    },
    "workflows/ise_radius_integration/playbook/delete_ise_radius_integration_workflow_playbook.yml": {
        "mode": "all",
        "vars": ["ise_radius_integration_details"],
    },
    "workflows/ise_radius_integration/playbook/ise_radius_integration_workflow_playbook.yml": {
        "mode": "all",
        "vars": ["ise_radius_integration_details"],
    },
    "workflows/provision/playbook/delete_provision_workflow_playbook.yml": {
        "mode": "all",
        "vars": ["provision_details"],
    },
    "workflows/provision/playbook/provision_workflow_playbook.yml": {
        "mode": "all",
        "vars": ["provision_details"],
    },
    "workflows/reports/playbook/delete_reports_playbook.yml": {
        "mode": "all",
        "vars": ["reports_details"],
    },
    "workflows/reports/playbook/reports_playbook.yml": {
        "mode": "all",
        "vars": ["reports_details"],
    },
}


FORCE_PROCESS = {
    "workflows/ansible_vault_update/playbook/ansible_vault_update_playbook.yml",
    "workflows/reports/playbook/reports_playbook.yml",
}


def should_process(rel_path: str, text: str) -> bool:
    return (
        rel_path in FORCE_PROCESS
        or
        "vars_files:" in text
        or "SWIM_VARS_FILE_PATH" in text
        or "Construct absolute paths for the variabe file" in text
    )


def normalize_legacy_var_name(text: str) -> str:
    return text.replace("SWIM_VARS_FILE_PATH", "VARS_FILE_PATH")


def remove_vars_files_block(text: str) -> str:
    return re.sub(
        r"(?m)^  vars_files:\n(?:\s{2,4}- [^\n]*\n)+",
        "",
        text,
        count=1,
    )


TASK_BLOCK_RE = re.compile(
    r"(?ms)^    - name:.*?(?=^    - name:|^  post_tasks:|^  handlers:|\Z)"
)


def is_input_handling_block(block: str) -> bool:
    if "file: \"{{ VARS_FILE_PATH }}\"" in block and "include_vars" in block:
        return True
    if "Input file selected" in block and "debug:" in block:
        return True
    if "Print input source" in block and "Input source:" in block:
        return True
    if "Provide it via VARS_FILE_PATH or as an inventory/host variable." in block:
        return True
    if "Validate that at least one workflow input variable is defined" in block:
        return True
    if "Construct absolute paths for the variabe file" in block:
        return True
    if "absolute_path:" in block and "VARS_FILE_PATH" in block:
        return True
    return False


def strip_input_comments(chunk: str) -> str:
    return re.sub(
        r"(?ms)(?:^\s{4}#.*VARS_FILE_PATH.*\n|^\s{4}# =+\n|^\s{4}# Input loading:.*\n)+$",
        "",
        chunk,
    )


def remove_existing_input_handling(text: str) -> str:
    if "  tasks:\n" not in text:
        return text

    prefix, rest = text.split("  tasks:\n", 1)
    rebuilt = []
    last = 0
    removed_any = False

    for match in TASK_BLOCK_RE.finditer(rest):
        between = rest[last:match.start()]
        block = match.group(0)
        if is_input_handling_block(block):
            rebuilt.append(strip_input_comments(between))
            removed_any = True
        else:
            rebuilt.append(between)
            rebuilt.append(block)
        last = match.end()

    rebuilt.append(rest[last:])
    rest = "".join(rebuilt)

    if removed_any:
        rest = re.sub(r"(?m)^\s{4}#.*VARS_FILE_PATH.*\n", "", rest)

    return prefix + "  tasks:\n" + rest


def extract_candidates(text: str) -> list[str]:
    candidates: list[str] = []

    for pattern in (
        r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"when:\s+([A-Za-z_][A-Za-z0-9_]*)\s+is\s+defined",
        r"loop:\s+\"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"with_list:\s+\"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)",
    ):
        for match in re.finditer(pattern, text):
            name = match.group(1)
            if name not in candidates:
                candidates.append(name)

    return candidates


def candidate_score(name: str) -> int:
    if name in IGNORE_VARS:
        return -1000
    if any(name.endswith(suffix) for suffix in UNDESIRABLE_SUFFIXES):
        return -500

    score = 0
    for suffix, value in PREFERRED_SUFFIX_SCORES:
        if name.endswith(suffix):
            score += value
            break

    if name in {
        "design_sites",
        "device_credentials",
        "discovery_details",
        "events_notifications_destination_and_subscription_details",
        "extranet_policies",
        "fabric_multicast_details",
        "fabric_sites_and_zones",
        "fabric_transits",
        "global_ippools",
        "inventory_details",
        "ise_radius_integration_details",
        "lan_automation_details",
        "network_settings_details",
        "pathtrace_details",
        "pnp_details",
        "port_assignment_migration",
        "provision_details",
        "reports_details",
        "rma_devices",
        "roles_users_details",
        "swim_details",
        "tags_details",
        "template_details",
        "wireless_design_details",
    }:
        score += 75

    if "_" in name:
        score += 5

    return score


def detect_validation(rel_path: str, text: str) -> dict[str, list[str] | str]:
    if rel_path in MANUAL_VALIDATIONS:
        return MANUAL_VALIDATIONS[rel_path]

    candidates = extract_candidates(text)
    ranked = sorted(
        ((candidate_score(name), idx, name) for idx, name in enumerate(candidates)),
        reverse=True,
    )

    for score, _, name in ranked:
        if score > 0:
            return {"mode": "all", "vars": [name]}

    return {"mode": "none", "vars": []}


def build_input_block(validation: dict[str, list[str] | str]) -> str:
    block = """    # =========================================================================
    # Input loading: vars file (VARS_FILE_PATH) or inventory variables
    # =========================================================================
    - name: Load input variables from vars file when VARS_FILE_PATH is provided
      ansible.builtin.include_vars:
        file: "{{ VARS_FILE_PATH }}"
      when:
        - VARS_FILE_PATH is defined
        - VARS_FILE_PATH | length > 0

    - name: Print input source
      ansible.builtin.debug:
        msg: >-
          {{
            'Input source: vars file ' ~ VARS_FILE_PATH
            if (VARS_FILE_PATH is defined and VARS_FILE_PATH | length > 0)
            else 'Input source: inventory / host variables (VARS_FILE_PATH not provided)'
          }}
"""

    mode = validation["mode"]
    names = validation["vars"]

    if mode == "all" and names:
        name = names[0]
        block += f"""
    - name: Validate that {name} is defined
      ansible.builtin.fail:
        msg: >-
          Variable '{name}' is not defined.
          Provide it via VARS_FILE_PATH or as an inventory/host variable.
      when: {name} is not defined
"""
    elif mode == "any" and names:
        names_csv = ", ".join(names)
        conditions = "\n".join(f"        - {name} is not defined" for name in names)
        block += f"""
    - name: Validate that at least one workflow input variable is defined
      ansible.builtin.fail:
        msg: >-
          None of the expected workflow input variables are defined ({names_csv}).
          Provide them via VARS_FILE_PATH or as inventory/host variables.
      when:
{conditions}
"""

    return block + "\n"


def insert_input_block(text: str, block: str) -> str:
    if "  tasks:\n" not in text:
        return text

    prefix, rest = text.split("  tasks:\n", 1)
    rest = rest.lstrip("\n")
    return prefix + "  tasks:\n" + block + rest


def make_task_labels_safe(text: str) -> str:
    safe_lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("- name:") or stripped.startswith("msg:"):
            line = line.replace("{{ VARS_FILE_PATH }}", SAFE_INPUT_LABEL)
        safe_lines.append(line)
    return "".join(safe_lines)


def update_playbook(path: Path, dry_run: bool) -> tuple[bool, str]:
    original = path.read_text()
    rel_path = str(path.relative_to(REPO_ROOT))
    if not should_process(rel_path, original):
        return False, "skip"

    text = normalize_legacy_var_name(original)
    text = remove_vars_files_block(text)
    text = remove_existing_input_handling(text)
    validation = detect_validation(rel_path, text)
    text = insert_input_block(text, build_input_block(validation))
    text = make_task_labels_safe(text)

    changed = text != original
    if changed and not dry_run:
        path.write_text(text)

    mode = validation["mode"]
    vars_text = ", ".join(validation["vars"]) if validation["vars"] else "none"
    return changed, f"{mode}:{vars_text}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed_paths: list[str] = []
    skipped_paths: list[str] = []

    for path in TARGET_PLAYBOOKS:
        changed, details = update_playbook(path, dry_run=args.dry_run)
        rel = str(path.relative_to(REPO_ROOT))
        if changed:
            changed_paths.append(f"{rel} [{details}]")
        else:
            skipped_paths.append(rel)

    label = "Would update" if args.dry_run else "Updated"
    print(f"{label}: {len(changed_paths)} playbooks")
    for item in changed_paths:
        print(f" - {item}")
    print(f"Skipped: {len(skipped_paths)} playbooks")


if __name__ == "__main__":
    main()
