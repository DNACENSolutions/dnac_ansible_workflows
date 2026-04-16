#!/bin/bash
#
# Run All Config Generator Playbooks
# This script discovers and executes all *_config_generator workflows with their corresponding var files
#
# Usage:
#   ./run_all_config_generators.sh [inventory_file] [--continue-on-error]
#
# Arguments:
#   inventory_file       - Optional: Path to inventory file (default: inventory/demo_lab/hosts.yaml)
#   --continue-on-error  - Optional: Continue running even if a playbook fails (default: stop on first failure)
#
# Examples:
#   ./run_all_config_generators.sh
#   ./run_all_config_generators.sh inventory/mylab/hosts.yaml
#   ./run_all_config_generators.sh inventory/mylab/hosts.yaml --continue-on-error
#

# Don't exit on error by default - we'll handle errors manually
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKFLOWS_DIR="${REPO_ROOT}/workflows"
LOG_DIR="${REPO_ROOT}/logs/config_generators"

# Default inventory
DEFAULT_INVENTORY="${REPO_ROOT}/inventory/demo_lab/hosts.yaml"

# Create log directory
mkdir -p "${LOG_DIR}"

# Timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SUMMARY_LOG="${LOG_DIR}/summary_${TIMESTAMP}.log"

# Counters
TOTAL=0
SUCCESS=0
FAILED=0
SKIPPED=0

# Arrays to track results
declare -a SUCCESSFUL_WORKFLOWS
declare -a FAILED_WORKFLOWS
declare -a SKIPPED_WORKFLOWS

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "error")
            echo -e "${RED}✗${NC} $message"
            ;;
        "warning")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "info")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Function to find playbook file
find_playbook() {
    local workflow_dir=$1
    local playbook_dir="${workflow_dir}/playbook"
    
    if [ ! -d "$playbook_dir" ]; then
        echo ""
        return
    fi
    
    # Look for playbook file (try multiple naming patterns)
    local playbook=""
    if [ -f "${playbook_dir}/$(basename ${workflow_dir}).yml" ]; then
        playbook="${playbook_dir}/$(basename ${workflow_dir}).yml"
    elif [ -f "${playbook_dir}/$(basename ${workflow_dir})_playbook.yml" ]; then
        playbook="${playbook_dir}/$(basename ${workflow_dir})_playbook.yml"
    else
        # Find first .yml file in playbook directory
        playbook=$(find "$playbook_dir" -maxdepth 1 -name "*.yml" -o -name "*.yaml" | head -n 1)
    fi
    
    echo "$playbook"
}

# Function to find vars file
find_vars_file() {
    local workflow_dir=$1
    local vars_dir="${workflow_dir}/vars"
    
    if [ ! -d "$vars_dir" ]; then
        echo ""
        return
    fi
    
    # Look for vars file (try multiple naming patterns)
    local vars_file=""
    if [ -f "${vars_dir}/$(basename ${workflow_dir})_input.yml" ]; then
        vars_file="${vars_dir}/$(basename ${workflow_dir})_input.yml"
    elif [ -f "${vars_dir}/$(basename ${workflow_dir})_inputs.yml" ]; then
        vars_file="${vars_dir}/$(basename ${workflow_dir})_inputs.yml"
    else
        # Find first .yml file in vars directory
        vars_file=$(find "$vars_dir" -maxdepth 1 -name "*input*.yml" -o -name "*input*.yaml" | head -n 1)
    fi
    
    echo "$vars_file"
}

# Function to run a single config generator
run_config_generator() {
    local workflow_name=$1
    local workflow_dir="${WORKFLOWS_DIR}/${workflow_name}"
    local playbook=$(find_playbook "$workflow_dir")
    local vars_file=$(find_vars_file "$workflow_dir")
    local inventory="$2"
    local continue_on_error="${3:-false}"
    
    TOTAL=$((TOTAL + 1))
    
    print_header "[$TOTAL] Running: $workflow_name"
    
    # Validate playbook exists
    if [ -z "$playbook" ] || [ ! -f "$playbook" ]; then
        print_status "warning" "Playbook not found, skipping"
        SKIPPED=$((SKIPPED + 1))
        SKIPPED_WORKFLOWS+=("$workflow_name (no playbook)")
        echo "---" >> "$SUMMARY_LOG"
        return
    fi
    
    # Validate vars file exists
    if [ -z "$vars_file" ] || [ ! -f "$vars_file" ]; then
        print_status "warning" "Vars file not found, skipping"
        SKIPPED=$((SKIPPED + 1))
        SKIPPED_WORKFLOWS+=("$workflow_name (no vars file)")
        echo "---" >> "$SUMMARY_LOG"
        return
    fi
    
    # Validate inventory exists
    if [ ! -f "$inventory" ]; then
        print_status "error" "Inventory file not found: $inventory"
        FAILED=$((FAILED + 1))
        FAILED_WORKFLOWS+=("$workflow_name (inventory not found)")
        echo "---" >> "$SUMMARY_LOG"
        return
    fi
    
    print_status "info" "Playbook: $(basename $playbook)"
    print_status "info" "Vars: $(basename $vars_file)"
    print_status "info" "Inventory: $(basename $inventory)"
    
    # Create log file for this run
    local log_file="${LOG_DIR}/${workflow_name}_${TIMESTAMP}.log"
    
    # Run ansible-playbook
    echo -e "\n${BLUE}Executing playbook...${NC}\n"
    
    # Run playbook and capture output to log file
    # Use PIPESTATUS to get the actual exit code of ansible-playbook, not tee
    ansible-playbook \
        -i "$inventory" \
        "$playbook" \
        --extra-vars "VARS_FILE_PATH=${vars_file}" \
        2>&1 | tee "$log_file"
    
    # Capture the exit code from ansible-playbook (first command in pipeline)
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        print_status "success" "Completed successfully (exit code: $exit_code)"
        SUCCESS=$((SUCCESS + 1))
        SUCCESSFUL_WORKFLOWS+=("$workflow_name")
        
        # Log to summary
        echo "✓ SUCCESS: $workflow_name" >> "$SUMMARY_LOG"
    else
        print_status "error" "Failed with exit code: $exit_code"
        FAILED=$((FAILED + 1))
        FAILED_WORKFLOWS+=("$workflow_name")
        
        # Log to summary
        echo "✗ FAILED: $workflow_name (exit code: $exit_code)" >> "$SUMMARY_LOG"
        echo "  Log: $log_file" >> "$SUMMARY_LOG"
        
        # Stop execution if continue_on_error is false
        if [ "$continue_on_error" = "false" ]; then
            echo "" >> "$SUMMARY_LOG"
            echo "Execution stopped due to failure (use --continue-on-error to continue)" >> "$SUMMARY_LOG"
            print_status "error" "Stopping execution due to failure. Use --continue-on-error to continue running."
            print_summary
            exit 1
        fi
    fi
    
    echo "---" >> "$SUMMARY_LOG"
}

# Function to print final summary
print_summary() {
    print_header "Execution Summary"
    
    echo -e "Total workflows: ${BLUE}$TOTAL${NC}"
    echo -e "Successful: ${GREEN}$SUCCESS${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"
    echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
    
    if [ ${#SUCCESSFUL_WORKFLOWS[@]} -gt 0 ]; then
        echo -e "\n${GREEN}Successful workflows:${NC}"
        for workflow in "${SUCCESSFUL_WORKFLOWS[@]}"; do
            echo -e "  ${GREEN}✓${NC} $workflow"
        done
    fi
    
    if [ ${#FAILED_WORKFLOWS[@]} -gt 0 ]; then
        echo -e "\n${RED}Failed workflows:${NC}"
        for workflow in "${FAILED_WORKFLOWS[@]}"; do
            echo -e "  ${RED}✗${NC} $workflow"
        done
    fi
    
    if [ ${#SKIPPED_WORKFLOWS[@]} -gt 0 ]; then
        echo -e "\n${YELLOW}Skipped workflows:${NC}"
        for workflow in "${SKIPPED_WORKFLOWS[@]}"; do
            echo -e "  ${YELLOW}⚠${NC} $workflow"
        done
    fi
    
    echo -e "\n${BLUE}Summary log:${NC} $SUMMARY_LOG"
    echo -e "${BLUE}Detailed logs:${NC} $LOG_DIR\n"
}

# Main execution
main() {
    # Parse command line arguments
    local inventory="$DEFAULT_INVENTORY"
    local continue_on_error=false
    
    for arg in "$@"; do
        case $arg in
            --continue-on-error)
                continue_on_error=true
                ;;
            --help|-h)
                echo "Usage: $0 [inventory_file] [--continue-on-error]"
                echo ""
                echo "Arguments:"
                echo "  inventory_file       - Optional: Path to inventory file (default: inventory/demo_lab/hosts.yaml)"
                echo "  --continue-on-error  - Optional: Continue running even if a playbook fails"
                echo ""
                echo "Examples:"
                echo "  $0"
                echo "  $0 inventory/mylab/hosts.yaml"
                echo "  $0 inventory/mylab/hosts.yaml --continue-on-error"
                exit 0
                ;;
            *)
                if [ -f "$arg" ]; then
                    inventory="$arg"
                elif [[ "$arg" != "--"* ]]; then
                    # Assume it's a relative path from repo root
                    if [ -f "${REPO_ROOT}/${arg}" ]; then
                        inventory="${REPO_ROOT}/${arg}"
                    else
                        print_status "error" "Inventory file not found: $arg"
                        exit 1
                    fi
                fi
                ;;
        esac
    done
    
    print_header "Config Generator Batch Execution"
    
    echo "Repository: $REPO_ROOT"
    echo "Workflows directory: $WORKFLOWS_DIR"
    echo "Inventory: $inventory"
    echo "Log directory: $LOG_DIR"
    echo "Timestamp: $TIMESTAMP"
    echo "Continue on error: $continue_on_error"
    
    # Check if inventory exists
    if [ ! -f "$inventory" ]; then
        print_status "error" "Inventory file not found: $inventory"
        echo "Please specify a valid inventory file"
        exit 1
    fi
    
    # Initialize summary log
    echo "Config Generator Batch Execution - $TIMESTAMP" > "$SUMMARY_LOG"
    echo "================================================" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"
    
    # Find all config_generator workflows
    local workflows=()
    while IFS= read -r -d '' workflow_dir; do
        local workflow_name=$(basename "$workflow_dir")
        workflows+=("$workflow_name")
    done < <(find "$WORKFLOWS_DIR" -maxdepth 1 -type d -name "*_config_generator" -print0 | sort -z)
    
    if [ ${#workflows[@]} -eq 0 ]; then
        print_status "warning" "No config_generator workflows found"
        exit 0
    fi
    
    print_status "info" "Found ${#workflows[@]} config_generator workflows"
    
    # Run each workflow
    for workflow_name in "${workflows[@]}"; do
        run_config_generator "$workflow_name" "$inventory" "$continue_on_error"
        
        # Small delay between runs
        sleep 1
    done
    
    # Print summary
    print_summary
    
    # Exit with error if any failed
    if [ $FAILED -gt 0 ]; then
        exit 1
    fi
}

# Run main function
main "$@"
