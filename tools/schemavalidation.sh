#!/bin/bash

# Comprehensive Schema Validation Script for DNAC Ansible Workflows
# This script validates all workflow inputs against their schemas using yamale

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOWS_DIR="$PROJECT_ROOT/workflows"

# Python environment
PYTHON_ENV=$(which python)
PYTHON_BIN=$(which python)

# Help function
show_help() {
    echo
    echo "================================================================================"
    echo "  DNAC Ansible Workflows - Comprehensive Schema Validation Tool"
    echo "================================================================================"
    echo
    echo "This script validates all workflow variable files against their corresponding"
    echo "schema files using yamale for YAML schema validation."
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -w, --workflow NAME     Validate only a specific workflow"
    echo "  -d, --workflows-dir DIR Directory containing workflows (default: workflows)"
    echo "  -o, --output FILE       Output file for detailed JSON report"
    echo "  -q, --quiet             Only show summary, suppress detailed output"
    echo "  -s, --schema FILE       Validate specific schema file"
    echo "  -v, --vars FILE         Validate specific vars file (requires -s)"
    echo "  --python-tool           Use Python validation tool instead of yamale directly"
    echo "  --list-workflows        List all available workflows"
    echo
    echo "Examples:"
    echo "  $0                                    # Validate all workflows"
    echo "  $0 -w device_discovery               # Validate specific workflow"
    echo "  $0 -s schema.yml -v vars.yml         # Validate specific files"
    echo "  $0 --list-workflows                  # List all workflows"
    echo "  $0 --python-tool -o report.json     # Use Python tool with JSON output"
    echo
}

# List workflows function
list_workflows() {
    echo "Available workflows:"
    echo "==================="
    
    if [ ! -d "$WORKFLOWS_DIR" ]; then
        echo -e "${RED}Error: Workflows directory not found: $WORKFLOWS_DIR${NC}"
        exit 1
    fi
    
    count=0
    for workflow_dir in "$WORKFLOWS_DIR"/*; do
        if [ -d "$workflow_dir" ]; then
            workflow_name=$(basename "$workflow_dir")
            schema_dir="$workflow_dir/schema"
            vars_dir="$workflow_dir/vars"
            
            if [ -d "$schema_dir" ] && [ -d "$vars_dir" ]; then
                schema_count=$(find "$schema_dir" -name "*.yml" -o -name "*.yaml" | wc -l)
                vars_count=$(find "$vars_dir" -name "*.yml" -o -name "*.yaml" | wc -l)
                echo -e "${GREEN}✓${NC} $workflow_name (${schema_count} schemas, ${vars_count} vars)"
                ((count++))
            else
                echo -e "${YELLOW}⚠${NC} $workflow_name (missing schema or vars directory)"
            fi
        fi
    done
    
    echo
    echo "Total workflows with schema and vars: $count"
}

# Validate specific files using yamale directly
validate_files() {
    local schema_file="$1"
    local vars_file="$2"
    
    if [ ! -f "$schema_file" ]; then
        echo -e "${RED}Error: Schema file not found: $schema_file${NC}"
        return 1
    fi
    
    if [ ! -f "$vars_file" ]; then
        echo -e "${RED}Error: Vars file not found: $vars_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Validating:${NC}"
    echo "  Schema: $schema_file"
    echo "  Vars:   $vars_file"
    echo
    
    "$PYTHON_BIN" -c "
import yamale
import sys
try:
    schema = yamale.make_schema('$schema_file')
    data = yamale.make_data('$vars_file')
    yamale.validate(schema, data)
    print('✓ Validation successful')
    sys.exit(0)
except Exception as e:
    print(f'✗ Validation failed: {e}')
    sys.exit(1)
"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Validation successful${NC}"
    else
        echo -e "${RED}✗ Validation failed${NC}"
    fi
    
    return $exit_code
}

# Validate all workflows in a directory
validate_all_workflows() {
    local workflows_dir="$1"
    local specific_workflow="$2"
    local quiet_mode="$3"
    
    if [ ! -d "$workflows_dir" ]; then
        echo -e "${RED}Error: Workflows directory not found: $workflows_dir${NC}"
        exit 1
    fi
    
    local total_validations=0
    local successful_validations=0
    local failed_validations=0
    
    echo "================================================================================"
    echo "  Starting Comprehensive Schema Validation"
    echo "================================================================================"
    echo
    
    for workflow_dir in "$workflows_dir"/*; do
        if [ ! -d "$workflow_dir" ]; then
            continue
        fi
        
        workflow_name=$(basename "$workflow_dir")
        
        # Skip if specific workflow requested and this isn't it
        if [ -n "$specific_workflow" ] && [ "$workflow_name" != "$specific_workflow" ]; then
            continue
        fi
        
        schema_dir="$workflow_dir/schema"
        vars_dir="$workflow_dir/vars"
        
        if [ ! -d "$schema_dir" ] || [ ! -d "$vars_dir" ]; then
            if [ "$quiet_mode" != "true" ]; then
                echo -e "${YELLOW}⚠ Skipping $workflow_name: missing schema or vars directory${NC}"
            fi
            continue
        fi
        
        if [ "$quiet_mode" != "true" ]; then
            echo -e "${BLUE}Validating workflow: $workflow_name${NC}"
            echo "$(printf '%.0s-' {1..50})"
        fi
        
        # Find schema and vars files
        schema_files=($(find "$schema_dir" -name "*.yml" -o -name "*.yaml" | sort))
        vars_files=($(find "$vars_dir" -name "*.yml" -o -name "*.yaml" | sort))
        
        if [ ${#schema_files[@]} -eq 0 ]; then
            if [ "$quiet_mode" != "true" ]; then
                echo -e "${YELLOW}⚠ No schema files found in $workflow_name${NC}"
            fi
            continue
        fi
        
        if [ ${#vars_files[@]} -eq 0 ]; then
            if [ "$quiet_mode" != "true" ]; then
                echo -e "${YELLOW}⚠ No vars files found in $workflow_name${NC}"
            fi
            continue
        fi
        
        # Validate each schema against matching vars files
        for schema_file in "${schema_files[@]}"; do
            schema_basename=$(basename "$schema_file" .yml)
            schema_basename=$(basename "$schema_basename" .yaml)
            
            # Try to find matching vars file
            matched=false
            for vars_file in "${vars_files[@]}"; do
                vars_basename=$(basename "$vars_file" .yml)
                vars_basename=$(basename "$vars_basename" .yaml)
                
                # Enhanced matching logic - match delete schemas with delete vars, non-delete with non-delete
                schema_base=$(echo "$schema_basename" | sed 's/_schema$//')
                vars_base=$(echo "$vars_basename" | sed 's/_vars$//' | sed 's/_inputs$//' | sed 's/_input$//')
                
                # Check if both are delete operations or both are non-delete operations
                if [[ "$schema_base" == delete_* && "$vars_base" == delete_* ]]; then
                    # Both are delete operations - match them
                    schema_clean=$(echo "$schema_base" | sed 's/^delete_//')
                    vars_clean=$(echo "$vars_base" | sed 's/^delete_//')
                    if [[ "$vars_clean" == *"$schema_clean"* ]] || [[ "$schema_clean" == *"$vars_clean"* ]]; then
                        match_found=true
                    fi
                elif [[ "$schema_base" != delete_* && "$vars_base" != delete_* ]]; then
                    # Both are non-delete operations - match them
                    if [[ "$vars_base" == *"$schema_base"* ]] || [[ "$schema_base" == *"$vars_base"* ]]; then
                        match_found=true
                    fi
                else
                    match_found=false
                fi
                
                if [[ "$match_found" == "true" ]]; then
                    
                    ((total_validations++))
                    
                    if [ "$quiet_mode" != "true" ]; then
                        echo -n "  $(basename "$schema_file") -> $(basename "$vars_file"): "
                    fi
                    
                    if "$PYTHON_BIN" -c "import yamale; schema = yamale.make_schema('$schema_file'); data = yamale.make_data('$vars_file'); yamale.validate(schema, data)" >/dev/null 2>&1; then
                        if [ "$quiet_mode" != "true" ]; then
                            echo -e "${GREEN}SUCCESS${NC}"
                        fi
                        ((successful_validations++))
                    else
                        if [ "$quiet_mode" != "true" ]; then
                            echo -e "${RED}FAILED${NC}"
                            # Show detailed error in non-quiet mode
                            "$PYTHON_BIN" -c "import yamale; schema = yamale.make_schema('$schema_file'); data = yamale.make_data('$vars_file'); yamale.validate(schema, data)" 2>&1 | sed 's/^/    /'
                        fi
                        ((failed_validations++))
                    fi
                    
                    matched=true
                    break
                fi
            done
            
            # If no specific match found, validate against first vars file
            if [ "$matched" = false ] && [ ${#vars_files[@]} -gt 0 ]; then
                vars_file="${vars_files[0]}"
                ((total_validations++))
                
                if [ "$quiet_mode" != "true" ]; then
                    echo -n "  $(basename "$schema_file") -> $(basename "$vars_file"): "
                fi
                
                if "$PYTHON_BIN" -c "import yamale; schema = yamale.make_schema('$schema_file'); data = yamale.make_data('$vars_file'); yamale.validate(schema, data)" >/dev/null 2>&1; then
                    if [ "$quiet_mode" != "true" ]; then
                        echo -e "${GREEN}SUCCESS${NC}"
                    fi
                    ((successful_validations++))
                else
                    if [ "$quiet_mode" != "true" ]; then
                        echo -e "${RED}FAILED${NC}"
                    fi
                    ((failed_validations++))
                fi
            fi
        done
        
        if [ "$quiet_mode" != "true" ]; then
            echo
        fi
    done
    
    # Summary report
    echo "================================================================================"
    echo "  VALIDATION SUMMARY REPORT"
    echo "================================================================================"
    echo "Total validations performed: $total_validations"
    echo "Successful validations: $successful_validations"
    echo "Failed validations: $failed_validations"
    
    if [ $total_validations -gt 0 ]; then
        success_rate=$((successful_validations * 100 / total_validations))
        echo "Success rate: ${success_rate}%"
    fi
    
    if [ $failed_validations -gt 0 ]; then
        echo -e "${RED}Some validations failed. Check the output above for details.${NC}"
        return 1
    else
        echo -e "${GREEN}All validations passed successfully!${NC}"
        return 0
    fi
}

# Main script logic
main() {
    local workflows_dir="$WORKFLOWS_DIR"
    local specific_workflow=""
    local schema_file=""
    local vars_file=""
    local output_file=""
    local quiet_mode="false"
    local use_python_tool="false"
    local list_only="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -w|--workflow)
                specific_workflow="$2"
                shift 2
                ;;
            -d|--workflows-dir)
                workflows_dir="$2"
                shift 2
                ;;
            -s|--schema)
                schema_file="$2"
                shift 2
                ;;
            -v|--vars)
                vars_file="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -q|--quiet)
                quiet_mode="true"
                shift
                ;;
            --python-tool)
                use_python_tool="true"
                shift
                ;;
            --list-workflows)
                list_only="true"
                shift
                ;;
            *)
                echo -e "${RED}Error: Unknown option $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check if yamale is available in the Python environment
    if [ ! -f "$PYTHON_BIN" ]; then
        echo -e "${RED}Error: Python environment not found at $PYTHON_BIN${NC}"
        echo "Please ensure the Python environment is set up correctly"
        exit 1
    fi
    
    if ! "$PYTHON_BIN" -c "import yamale" >/dev/null 2>&1; then
        echo -e "${RED}Error: yamale not found in Python environment.${NC}"
        echo "Please install yamale in the environment: source $PYTHON_ENV && pip install yamale"
        exit 1
    fi
    
    # Handle list workflows
    if [ "$list_only" = "true" ]; then
        list_workflows
        exit 0
    fi
    
    # Handle specific file validation
    if [ -n "$schema_file" ]; then
        if [ -z "$vars_file" ]; then
            echo -e "${RED}Error: --vars option is required when using --schema${NC}"
            exit 1
        fi
        validate_files "$schema_file" "$vars_file"
        exit $?
    fi
    
    # Handle Python tool
    if [ "$use_python_tool" = "true" ]; then
        python_script="$SCRIPT_DIR/comprehensive_schema_validation.py"
        if [ ! -f "$python_script" ]; then
            echo -e "${RED}Error: Python validation tool not found: $python_script${NC}"
            exit 1
        fi
        
        python_args=()
        if [ -n "$specific_workflow" ]; then
            python_args+=(--workflow "$specific_workflow")
        fi
        if [ -n "$workflows_dir" ] && [ "$workflows_dir" != "$WORKFLOWS_DIR" ]; then
            python_args+=(--workflows-dir "$workflows_dir")
        fi
        if [ -n "$output_file" ]; then
            python_args+=(--output "$output_file")
        fi
        if [ "$quiet_mode" = "true" ]; then
            python_args+=(--quiet)
        fi
        
        "$PYTHON_BIN" "$python_script" "${python_args[@]}"
        exit $?
    fi
    
    # Handle workflow validation
    validate_all_workflows "$workflows_dir" "$specific_workflow" "$quiet_mode"
    exit $?
}

# Run main function with all arguments
main "$@"
