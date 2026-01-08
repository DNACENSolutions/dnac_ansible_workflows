#!/bin/bash

# generate_mapping.sh
# This script helps generate a workflow-module mapping file by scanning
# workflows and attempting to find corresponding modules.

set -e

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
WORKFLOWS_DIR="workflows"
MODULE_DIR=""
OUTPUT_FILE="workflow_module_mapping.txt"

# Display help
show_help() {
    cat << EOF
Generate Workflow-Module Mapping File
=====================================

This script scans workflows and modules to generate a mapping file.

Usage:
    ./generate_mapping.sh -m <module_directory> [options]

Required Arguments:
    -m, --module-dir DIR    Path to the directory containing Ansible module files

Optional Arguments:
    -w, --workflows-dir DIR Directory containing workflow schemas (default: workflows)
    -o, --output FILE       Output mapping file (default: workflow_module_mapping.txt)
    -h, --help              Show this help message

Examples:
    # Generate mapping file
    ./generate_mapping.sh -m /path/to/modules

    # Custom output file
    ./generate_mapping.sh -m /path/to/modules -o my_mapping.txt

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--module-dir)
            MODULE_DIR="$2"
            shift 2
            ;;
        -w|--workflows-dir)
            WORKFLOWS_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$MODULE_DIR" ]; then
    echo -e "${YELLOW}Error: Module directory is required${NC}"
    show_help
    exit 1
fi

if [ ! -d "$MODULE_DIR" ]; then
    echo -e "${YELLOW}Error: Module directory not found: $MODULE_DIR${NC}"
    exit 1
fi

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo -e "${YELLOW}Error: Workflows directory not found: $WORKFLOWS_DIR${NC}"
    exit 1
fi

# Function to find module file for a workflow
find_module_file() {
    local workflow_name=$1
    local module_dir=$2
    
    # Create variations of the workflow name
    local name_no_underscores=$(echo "$workflow_name" | tr -d '_')
    local name_accesspoint=$(echo "$workflow_name" | sed 's/access_point/accesspoint/')
    
    # Common module naming patterns
    local patterns=(
        "${workflow_name}_workflow_manager.py"
        "${name_accesspoint}_workflow_manager.py"
        "${name_no_underscores}_workflow_manager.py"
        "${workflow_name}_manager.py"
        "${name_accesspoint}_manager.py"
        "${name_no_underscores}_manager.py"
    )
    
    # Search for module file
    for pattern in "${patterns[@]}"; do
        if [ -f "$module_dir/$pattern" ]; then
            echo "$pattern"
            return 0
        fi
        
        local module_file=$(find "$module_dir" -maxdepth 2 -type f -name "$pattern" 2>/dev/null | head -n 1)
        if [ -n "$module_file" ]; then
            basename "$module_file"
            return 0
        fi
    done
    
    return 1
}

echo -e "${BLUE}Generating workflow-module mapping file...${NC}"
echo -e "${BLUE}Workflows Directory: $WORKFLOWS_DIR${NC}"
echo -e "${BLUE}Module Directory: $MODULE_DIR${NC}"
echo -e "${BLUE}Output File: $OUTPUT_FILE${NC}"
echo ""

# Create output file with header
cat > "$OUTPUT_FILE" << 'EOF'
# Workflow-Module Mapping File
# Format: workflow_name:module_filename
# Lines starting with # are comments and will be ignored
# Generated automatically - review and edit as needed

EOF

found_count=0
not_found_count=0

# Iterate through workflows
for workflow_dir in "$WORKFLOWS_DIR"/*; do
    if [ ! -d "$workflow_dir" ]; then
        continue
    fi
    
    workflow_name=$(basename "$workflow_dir")
    schema_dir="$workflow_dir/schema"
    
    # Skip if no schema directory
    if [ ! -d "$schema_dir" ]; then
        continue
    fi
    
    # Check if schema files exist
    schema_files=$(find "$schema_dir" -type f -name "*_schema.yml" ! -name "delete_*" 2>/dev/null)
    if [ -z "$schema_files" ]; then
        continue
    fi
    
    # Try to find module
    module_file=$(find_module_file "$workflow_name" "$MODULE_DIR")
    
    if [ -n "$module_file" ]; then
        echo "$workflow_name:$module_file" >> "$OUTPUT_FILE"
        echo -e "${GREEN}✓ $workflow_name -> $module_file${NC}"
        found_count=$((found_count + 1))
    else
        echo "# $workflow_name:MODULE_NOT_FOUND" >> "$OUTPUT_FILE"
        echo -e "${YELLOW}⚠ $workflow_name -> NOT FOUND${NC}"
        not_found_count=$((not_found_count + 1))
    fi
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Found mappings: $found_count${NC}"
echo -e "${YELLOW}Not found: $not_found_count${NC}"
echo -e "${BLUE}Output saved to: $OUTPUT_FILE${NC}"
echo ""
echo -e "${BLUE}Review the generated file and uncomment/edit mappings as needed.${NC}"
echo -e "${BLUE}Lines marked with 'MODULE_NOT_FOUND' need manual mapping.${NC}"
