#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_ROOT="${SWITCH_REFRESH_ANSIBLE_VENV:-}"
if [[ -z "${VENV_ROOT}" && -x "/ws/shreeheg-sjc/dnac_ansible_workflows-ansible-runner-ui-reliability/.venv312/bin/ansible-playbook" ]]; then
  VENV_ROOT="/ws/shreeheg-sjc/dnac_ansible_workflows-ansible-runner-ui-reliability/.venv312"
fi
if [[ -n "${SWITCH_REFRESH_ANSIBLE_PLAYBOOK:-}" ]]; then
  ANSIBLE_PLAYBOOK="${SWITCH_REFRESH_ANSIBLE_PLAYBOOK}"
elif [[ -n "${VENV_ROOT}" ]]; then
  ANSIBLE_PLAYBOOK="${VENV_ROOT}/bin/ansible-playbook"
else
  ANSIBLE_PLAYBOOK="$(command -v ansible-playbook || true)"
fi
ANSIBLE_PYTHON_INTERPRETER="${SWITCH_REFRESH_ANSIBLE_PYTHON:-}"
if [[ -z "${ANSIBLE_PYTHON_INTERPRETER}" && -n "${VENV_ROOT}" ]]; then
  ANSIBLE_PYTHON_INTERPRETER="${VENV_ROOT}/bin/python"
fi
INVENTORY="${SWITCH_REFRESH_INVENTORY:-${REPO_ROOT}/inventory/demo_lab/hosts.yaml}"
LOG_DIR="${REPO_ROOT}/logs/switch_refresh_regression"

usage() {
  cat <<'USAGE'
Usage: tools/switch_refresh_regression_runner.sh <flow>

Full flows:
  full-lan                 LAN Automation ENL1 -> ENL2 full refresh
  full-discovery           Discovery EN1 -> EN2 full refresh

Cut flows:
  recover-lan-seed-ports  Reset LAN Automation seed ports and resync seed
  resync-lan-seed          Resync LAN Automation seed in Catalyst Center only
  lan-onboard              LAN Automation onboarding only
  lan-onboard-enl1         LAN Automation onboarding for ENL1 reverse refresh
  discovery-onboard        Discovery onboarding only
  discovery-onboard-en1    Discovery onboarding for EN1 reverse refresh
  lan-provision            Provision LAN Automation replacement ENL2
  lan-provision-enl1       Provision LAN Automation ENL1 reverse refresh
  discovery-provision      Provision Discovery replacement EN2
  discovery-provision-en1  Provision Discovery EN1 reverse refresh
  lan-set-access-role      Set LAN Automation replacement ENL2 inventory role to ACCESS and resync
  lan-set-enl1-access-role Set LAN Automation ENL1 inventory role to ACCESS and resync
  discovery-set-access-role Set Discovery replacement EN2 inventory role to ACCESS and resync
  discovery-set-en1-access-role Set Discovery EN1 inventory role to ACCESS and resync
  lan-fabric               Fabric onboarding for ENL2
  lan-fabric-enl1          Fabric onboarding for ENL1 reverse refresh
  discovery-fabric         Fabric onboarding for EN2
  discovery-fabric-en1     Fabric onboarding for EN1 reverse refresh
  discovery-seed-en2-port  Add a test host-port assignment to EN2
  lan-seed-enl2-port       Add a test host-port assignment to ENL2
  lan-migrate              Port assignment migration ENL1 -> ENL2
  lan-migrate-enl2-to-enl1 Port assignment migration ENL2 -> ENL1
  discovery-migrate        Port assignment migration EN1 -> EN2
  discovery-migrate-en2-to-en1 Port assignment migration EN2 -> EN1
  lan-cleanup              Cleanup source ENL1
  lan-cleanup-enl2         Cleanup source ENL2 after reverse LAN refresh
  discovery-cleanup        Cleanup source EN1
  lan-validate             Validate LAN Automation final state
  discovery-validate       Validate Discovery final state
  lan-diagnose-enl2        Read-only ENL2 inventory and fabric membership check
  lan-diagnose-enl1        Read-only ENL1 inventory and LAN Automation session check
  lan-list-enl-interfaces  Read-only ENL1/ENL2 interface inventory check
  discovery-diagnose-en2   Read-only EN2 inventory and fabric membership check
  discovery-list-en2-interfaces Read-only EN2 interface inventory check

Environment defaults can be pre-exported. Missing secrets are prompted silently.
Required: HOSTIP, CATALYST_CENTER_USERNAME, CATALYST_CENTER_PASSWORD,
          SWITCH_USERNAME, SWITCH_PASSWORD, SWITCH_ENABLE_PASSWORD.
Discovery onboarding also uses SWITCH_SNMP_PASSWORD when it differs from SWITCH_PASSWORD.

Optional runtime overrides:
  SWITCH_REFRESH_ANSIBLE_VENV       Path to a Python virtualenv with ansible-playbook
  SWITCH_REFRESH_ANSIBLE_PLAYBOOK   Explicit ansible-playbook executable
  SWITCH_REFRESH_ANSIBLE_PYTHON     Explicit Python interpreter for ansible_python_interpreter
  SWITCH_REFRESH_COLLECTIONS_PATH   Extra Ansible collection paths
USAGE
}

flow="${1:-}"
case "${flow}" in
  recover-lan-seed-ports) playbook="workflows/switch_refresh_regression/playbook/cut_recover_lan_seed_ports.yml" ;;
  resync-lan-seed) playbook="workflows/switch_refresh_regression/playbook/cut_recover_lan_seed_ports.yml" ;;
  full-lan) playbook="workflows/switch_refresh_regression/playbook/full_lan_automation_refresh.yml" ;;
  full-discovery) playbook="workflows/switch_refresh_regression/playbook/full_discovery_refresh.yml" ;;
  lan-onboard) playbook="workflows/switch_refresh_regression/playbook/cut_lan_automation_onboard.yml" ;;
  lan-onboard-enl1) playbook="workflows/switch_refresh_regression/playbook/cut_lan_automation_onboard_enl1.yml" ;;
  discovery-onboard) playbook="workflows/switch_refresh_regression/playbook/cut_discovery_onboard.yml" ;;
  discovery-onboard-en1) playbook="workflows/switch_refresh_regression/playbook/cut_discovery_onboard_en1.yml" ;;
  lan-provision) playbook="workflows/switch_refresh_regression/playbook/cut_provision_lan_automation_replacement.yml" ;;
  lan-provision-enl1) playbook="workflows/switch_refresh_regression/playbook/cut_provision_lan_automation_enl1.yml" ;;
  discovery-provision) playbook="workflows/switch_refresh_regression/playbook/cut_provision_discovery_replacement.yml" ;;
  discovery-provision-en1) playbook="workflows/switch_refresh_regression/playbook/cut_provision_discovery_en1.yml" ;;
  lan-set-access-role) playbook="workflows/switch_refresh_regression/playbook/cut_set_lan_automation_enl2_access_role.yml" ;;
  lan-set-enl1-access-role) playbook="workflows/switch_refresh_regression/playbook/cut_set_lan_automation_enl1_access_role.yml" ;;
  discovery-set-access-role) playbook="workflows/switch_refresh_regression/playbook/cut_set_discovery_en2_access_role.yml" ;;
  discovery-set-en1-access-role) playbook="workflows/switch_refresh_regression/playbook/cut_set_discovery_en1_access_role.yml" ;;
  lan-fabric) playbook="workflows/switch_refresh_regression/playbook/cut_fabric_onboard_lan_automation.yml" ;;
  lan-fabric-enl1) playbook="workflows/switch_refresh_regression/playbook/cut_fabric_onboard_lan_automation_enl1.yml" ;;
  discovery-fabric) playbook="workflows/switch_refresh_regression/playbook/cut_fabric_onboard_discovery.yml" ;;
  discovery-fabric-en1) playbook="workflows/switch_refresh_regression/playbook/cut_fabric_onboard_discovery_en1.yml" ;;
  discovery-seed-en2-port) playbook="workflows/switch_refresh_regression/playbook/cut_seed_discovery_en2_port_assignment.yml" ;;
  lan-seed-enl2-port) playbook="workflows/switch_refresh_regression/playbook/cut_seed_lan_automation_enl2_port_assignment.yml" ;;
  lan-migrate) playbook="workflows/switch_refresh_regression/playbook/cut_port_assignment_migration_lan_automation.yml" ;;
  lan-migrate-enl2-to-enl1) playbook="workflows/switch_refresh_regression/playbook/cut_port_assignment_migration_lan_automation_enl2_to_enl1.yml" ;;
  discovery-migrate) playbook="workflows/switch_refresh_regression/playbook/cut_port_assignment_migration_discovery.yml" ;;
  discovery-migrate-en2-to-en1) playbook="workflows/switch_refresh_regression/playbook/cut_port_assignment_migration_discovery_en2_to_en1.yml" ;;
  lan-cleanup) playbook="workflows/switch_refresh_regression/playbook/cut_cleanup_lan_automation_source.yml" ;;
  lan-cleanup-enl2) playbook="workflows/switch_refresh_regression/playbook/cut_cleanup_lan_automation_enl2.yml" ;;
  discovery-cleanup) playbook="workflows/switch_refresh_regression/playbook/cut_cleanup_discovery_source.yml" ;;
  lan-validate) playbook="workflows/switch_refresh_regression/playbook/cut_validate_lan_automation.yml" ;;
  discovery-validate) playbook="workflows/switch_refresh_regression/playbook/cut_validate_discovery.yml" ;;
  lan-diagnose-enl2) playbook="workflows/switch_refresh_regression/playbook/diagnose_lan_automation_enl2.yml" ;;
  lan-diagnose-enl1) playbook="workflows/switch_refresh_regression/playbook/diagnose_lan_automation_enl1.yml" ;;
  lan-list-enl-interfaces) playbook="workflows/switch_refresh_regression/playbook/diagnose_lan_automation_enl_interfaces.yml" ;;
  discovery-diagnose-en2) playbook="workflows/switch_refresh_regression/playbook/diagnose_discovery_en2.yml" ;;
  discovery-list-en2-interfaces) playbook="workflows/switch_refresh_regression/playbook/diagnose_discovery_en2_interfaces.yml" ;;
  -h|--help|help|"") usage; exit 0 ;;
  *) echo "Unknown flow: ${flow}" >&2; usage >&2; exit 2 ;;
esac

prompt_default() {
  local var_name="$1"
  local prompt="$2"
  local default_value="$3"
  local value="${!var_name:-}"
  if [[ -z "${value}" ]]; then
    read -r -p "${prompt} [${default_value}]: " value
    export "${var_name}=${value:-${default_value}}"
  fi
}

prompt_secret() {
  local var_name="$1"
  local prompt="$2"
  local value="${!var_name:-}"
  if [[ -z "${value}" ]]; then
    read -r -s -p "${prompt}: " value </dev/tty
    echo
    if [[ -z "${value}" ]]; then
      echo "${prompt} cannot be empty." >&2
      exit 1
    fi
    export "${var_name}=${value}"
  fi
}

if [[ -z "${ANSIBLE_PLAYBOOK}" || ! -x "${ANSIBLE_PLAYBOOK}" ]]; then
  echo "ansible-playbook not found or not executable. Set SWITCH_REFRESH_ANSIBLE_VENV or SWITCH_REFRESH_ANSIBLE_PLAYBOOK." >&2
  exit 1
fi

prompt_default HOSTIP "Catalyst Center host" "10.195.243.100"
prompt_default CATALYST_CENTER_USERNAME "Catalyst Center username" "iac4"
prompt_secret CATALYST_CENTER_PASSWORD "Catalyst Center password"

if [[ "${flow}" != "lan-diagnose-enl2" && "${flow}" != "lan-diagnose-enl1" && "${flow}" != "lan-list-enl-interfaces" && "${flow}" != "discovery-diagnose-en2" && "${flow}" != "discovery-list-en2-interfaces" ]]; then
  prompt_default SWITCH_USERNAME "Switch username" "wlcaccess"
  prompt_secret SWITCH_PASSWORD "Switch password"
  prompt_secret SWITCH_ENABLE_PASSWORD "Switch enable password"
  if [[ "${flow}" == "full-discovery" || "${flow}" == "discovery-onboard" || "${flow}" == "discovery-onboard-en1" ]]; then
    prompt_secret SWITCH_SNMP_PASSWORD "Switch SNMP password"
  fi
fi

collections_path_entries=("${REPO_ROOT}/collections")
if [[ -n "${SWITCH_REFRESH_COLLECTIONS_PATH:-}" ]]; then
  collections_path_entries+=("${SWITCH_REFRESH_COLLECTIONS_PATH}")
fi
if [[ -d "/ws/shreeheg-sjc/catalystcenter-ansible-dev-switch-refresh-sda/collections" ]]; then
  collections_path_entries+=("/ws/shreeheg-sjc/catalystcenter-ansible-dev-switch-refresh-sda/collections")
fi
if [[ -d "/ws/shreeheg-sjc/dnac_ansible_workflows-ansible-runner-ui-reliability/collections" ]]; then
  collections_path_entries+=("/ws/shreeheg-sjc/dnac_ansible_workflows-ansible-runner-ui-reliability/collections")
fi
if [[ -n "${ANSIBLE_COLLECTIONS_PATH:-}" ]]; then
  collections_path_entries+=("${ANSIBLE_COLLECTIONS_PATH}")
fi
collections_path_entries+=("${HOME}/.ansible/collections" "/usr/share/ansible/collections")
export ANSIBLE_COLLECTIONS_PATH="$(IFS=:; echo "${collections_path_entries[*]}")"

ansible_extra_args=()
if [[ -n "${ANSIBLE_PYTHON_INTERPRETER}" ]]; then
  ansible_extra_args+=("-e" "ansible_python_interpreter=${ANSIBLE_PYTHON_INTERPRETER}")
fi

mkdir -p "${LOG_DIR}"
timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="${LOG_DIR}/${flow}_${timestamp}.log"

echo "Running ${flow}: ${playbook}"
echo "Log: ${log_file}"
cd "${REPO_ROOT}"

if [[ "${flow}" == "recover-lan-seed-ports" || "${flow}" == "resync-lan-seed" ]]; then
  seed_ip="${SWITCH_REFRESH_LAN_SEED_IP:-204.1.2.4}"
  seed_ports="${SWITCH_REFRESH_LAN_SEED_PORTS:-GigabitEthernet2/0/7 GigabitEthernet2/0/8}"
  {
    if [[ "${flow}" == "recover-lan-seed-ports" ]]; then
      echo "Recovering LAN Automation seed ${seed_ip} ports: ${seed_ports}"
      export SSHPASS="${SWITCH_PASSWORD}"
      {
        echo enable
        echo "${SWITCH_ENABLE_PASSWORD}"
        echo configure terminal
        for seed_port in ${seed_ports}; do
          echo "default interface ${seed_port}"
          echo "interface ${seed_port}"
          echo switchport
          echo "switchport mode access"
          echo "no shutdown"
        done
        echo end
        echo "write memory"
        echo exit
      } | sshpass -e ssh -tt \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o LogLevel=ERROR \
        "${SWITCH_USERNAME}@${seed_ip}"
      unset SSHPASS
    else
      echo "Skipping seed CLI recovery; resyncing LAN Automation seed ${seed_ip} only"
    fi
    "${ANSIBLE_PLAYBOOK}" -i "${INVENTORY}" "${playbook}" \
      "${ansible_extra_args[@]}" \
      -e "switch_refresh_seed_ip=${seed_ip}"
  } 2>&1 | tee "${log_file}"
  exit ${PIPESTATUS[0]}
fi

"${ANSIBLE_PLAYBOOK}" -i "${INVENTORY}" "${playbook}" \
  "${ansible_extra_args[@]}" \
  2>&1 | tee "${log_file}"