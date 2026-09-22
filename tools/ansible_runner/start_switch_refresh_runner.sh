#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

if [[ -z "${HOSTIP:-}" ]]; then
  read -rp 'Catalyst Center host/IP: ' HOSTIP
  export HOSTIP
fi

if [[ -z "${CATALYST_CENTER_USERNAME:-}" ]]; then
  read -rp 'Catalyst Center username: ' CATALYST_CENTER_USERNAME
  export CATALYST_CENTER_USERNAME
fi

if [[ -z "${SWITCH_CLI_USERNAME:-}" ]]; then
  read -rp 'Switch CLI username: ' SWITCH_CLI_USERNAME
  export SWITCH_CLI_USERNAME
fi

export SNMPV3_AUTH_PROTOCOL="${SNMPV3_AUTH_PROTOCOL:-SHA}"
export SNMPV3_PRIV_PROTOCOL="${SNMPV3_PRIV_PROTOCOL:-AES128}"
export ANSIBLE_COLLECTIONS_PATH="${ANSIBLE_COLLECTIONS_PATH:-$PWD/collections:$PWD/.ansible/collections:$PWD:$HOME/.ansible/collections}"
export ANSIBLE_ROLES_PATH="${ANSIBLE_ROLES_PATH:-$PWD/roles}"

if [[ -x "$PWD/tools/ansible_runner/.venv/bin/python" ]]; then
  RUNNER_PYTHON="$PWD/tools/ansible_runner/.venv/bin/python"
elif [[ -x "$PWD/python3env/bin/python" ]]; then
  RUNNER_PYTHON="$PWD/python3env/bin/python"
elif [[ -x "$PWD/.venv/bin/python" ]]; then
  RUNNER_PYTHON="$PWD/.venv/bin/python"
else
  RUNNER_PYTHON="$(command -v python3 || printf 'python3')"
fi

if [[ -z "${ANSIBLE_PYTHON_INTERPRETER:-}" ]]; then
  export ANSIBLE_PYTHON_INTERPRETER="$RUNNER_PYTHON"
fi
export ANSIBLE_PLAYBOOK_BIN="${ANSIBLE_PLAYBOOK_BIN:-$(command -v ansible-playbook || printf 'ansible-playbook')}"

if [[ -z "${CATALYST_CENTER_PASSWORD:-}" ]]; then
  read -rsp 'Catalyst Center password: ' CATALYST_CENTER_PASSWORD
  printf '\n'
  export CATALYST_CENTER_PASSWORD
fi

if [[ -z "${SWITCH_CLI_PASSWORD:-}" ]]; then
  read -rsp 'Switch CLI password: ' SWITCH_CLI_PASSWORD
  printf '\n'
  export SWITCH_CLI_PASSWORD
fi

if [[ -z "${SWITCH_ENABLE_PASSWORD:-}" ]]; then
  read -rsp 'Switch enable password: ' SWITCH_ENABLE_PASSWORD
  printf '\n'
  export SWITCH_ENABLE_PASSWORD
fi

if [[ -n "${SNMPV3_USERNAME:-}" ]]; then
  if [[ -z "${SNMPV3_AUTH_PASSWORD:-}" ]]; then
    read -rsp "SNMPv3 auth password for ${SNMPV3_USERNAME}: " SNMPV3_AUTH_PASSWORD
    printf '\n'
    export SNMPV3_AUTH_PASSWORD
  fi

  if [[ -z "${SNMPV3_PRIV_PASSWORD:-}" ]]; then
    read -rsp "SNMPv3 priv password for ${SNMPV3_USERNAME}: " SNMPV3_PRIV_PASSWORD
    printf '\n'
    export SNMPV3_PRIV_PASSWORD
  fi
fi

export RUNNER_HOST="${RUNNER_HOST:-0.0.0.0}"
export RUNNER_PORT="${RUNNER_PORT:-5006}"
export RUNNER_TMPDIR="${RUNNER_TMPDIR:-/tmp/catalystcenter-ansible-runner}"
exec "${RUNNER_PYTHON}" tools/ansible_runner/app.py
