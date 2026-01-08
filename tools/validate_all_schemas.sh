#!/bin/bash

# validate_all_schemas.sh
# This script runs schema_doc_validator.py for all workflow schemas,
# automatically finding corresponding module files from the provided module directory.

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
WORKFLOWS_DIR="workflows"
MODULE_DIR=""
OUTPUT_DIR="schema_validation_reports"
MAPPING_FILE=""
VERBOSE=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to display help
show_help() {
    cat << EOF
Schema-Documentation Validation Script
======================================

This script validates all workflow schemas against their corresponding module documentation.

Usage:
    ./validate_all_schemas.sh -m <module_directory> [options]

Required Arguments:
    -m, --module-dir DIR    Path to the directory containing Ansible module files

Optional Arguments:
    -w, --workflows-dir DIR Directory containing workflow schemas (default: workflows)
    -o, --output-dir DIR    Directory for output reports (default: schema_validation_reports)
    -f, --mapping-file FILE Path to workflow-module mapping file (optional)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

Mapping File Format:
    The mapping file should contain one mapping per line in the format:
    workflow_name:module_filename
    
    Example:
    access_point_location:accesspoint_location_workflow_manager.py
    inventory:inventory_workflow_manager.py
    assurance_pathtrace:assurance_pathtrace_workflow_manager.py

Examples:
    # Basic usage
    ./validate_all_schemas.sh -m /path/to/modules

    # With mapping file
    ./validate_all_schemas.sh -m /path/to/modules -f workflow_mapping.txt

    # With custom workflows directory
    ./validate_all_schemas.sh -m /path/to/modules -w /path/to/workflows

    # With verbose output
    ./validate_all_schemas.sh -m /path/to/modules -v

    # Custom output directory
    ./validate_all_schemas.sh -m /path/to/modules -o /path/to/reports

EOF
}

# Parse command line arguments
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
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--mapping-file)
            MAPPING_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$MODULE_DIR" ]; then
    echo -e "${RED}Error: Module directory is required${NC}"
    show_help
    exit 1
fi

# Validate directories exist
if [ ! -d "$MODULE_DIR" ]; then
    echo -e "${RED}Error: Module directory not found: $MODULE_DIR${NC}"
    exit 1
fi

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo -e "${RED}Error: Workflows directory not found: $WORKFLOWS_DIR${NC}"
    exit 1
fi

# Validate mapping file if provided
if [ -n "$MAPPING_FILE" ] && [ ! -f "$MAPPING_FILE" ]; then
    echo -e "${RED}Error: Mapping file not found: $MAPPING_FILE${NC}"
    exit 1
fi

# Load workflow-module mappings from file if provided
if [ -n "$MAPPING_FILE" ]; then
    echo -e "${BLUE}Loading workflow-module mappings from: $MAPPING_FILE${NC}"
    mapping_count=0
    while IFS=: read -r workflow module || [ -n "$workflow" ]; do
        # Skip empty lines and comments
        [[ -z "$workflow" || "$workflow" =~ ^[[:space:]]*# ]] && continue
        # Trim whitespace
        workflow=$(echo "$workflow" | xargs)
        module=$(echo "$module" | xargs)
        if [ "$VERBOSE" = true ]; then
            echo "  Mapped: $workflow -> $module"
        fi
        mapping_count=$((mapping_count + 1))
    done < "$MAPPING_FILE"
    echo -e "${GREEN}Loaded $mapping_count mapping(s)${NC}"
    echo ""
fi

# Function to get module from mapping file
get_mapped_module() {
    local workflow_name=$1
    local mapping_file=$2
    
    if [ -z "$mapping_file" ] || [ ! -f "$mapping_file" ]; then
        return 1
    fi
    
    # Search for the workflow in the mapping file
    local result=$(grep "^[[:space:]]*${workflow_name}:" "$mapping_file" | grep -v "^#" | head -n 1 | cut -d: -f2- | xargs)
    
    if [ -n "$result" ]; then
        echo "$result"
        return 0
    fi
    
    return 1
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR_SCRIPT="$SCRIPT_DIR/schema_doc_validator.py"

if [ ! -f "$VALIDATOR_SCRIPT" ]; then
    echo -e "${RED}Error: schema_doc_validator.py not found at $VALIDATOR_SCRIPT${NC}"
    exit 1
fi

# Check if Python and required modules are available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Test if yaml module is available
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${RED}Error: PyYAML module not found. Please install it with: pip install pyyaml${NC}"
    echo -e "${YELLOW}Note: You may need to activate your virtual environment first${NC}"
    exit 1
fi

# Initialize counters
total_schemas=0
successful_validations=0
failed_validations=0
skipped_validations=0
current_workflow=0

# Count total workflows with schemas for progress tracking
total_workflows=0
for workflow_dir in "$WORKFLOWS_DIR"/*; do
    if [ -d "$workflow_dir" ] && [ -d "$workflow_dir/schema" ]; then
        schema_count=$(find "$workflow_dir/schema" -type f -name "*_schema.yml" ! -name "delete_*" 2>/dev/null | wc -l)
        if [ "$schema_count" -gt 0 ]; then
            total_workflows=$((total_workflows + 1))
        fi
    fi
done

# Create summary file
SUMMARY_FILE="$OUTPUT_DIR/validation_summary_$TIMESTAMP.txt"
echo "Schema-Documentation Validation Summary" > "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"
echo "Date: $(date)" >> "$SUMMARY_FILE"
echo "Module Directory: $MODULE_DIR" >> "$SUMMARY_FILE"
echo "Workflows Directory: $WORKFLOWS_DIR" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

echo -e "${BLUE}Starting schema validation for all workflows...${NC}"
echo -e "${BLUE}Module Directory: $MODULE_DIR${NC}"
echo -e "${BLUE}Workflows Directory: $WORKFLOWS_DIR${NC}"
echo -e "${BLUE}Output Directory: $OUTPUT_DIR${NC}"
echo -e "${BLUE}Total workflows to process: $total_workflows${NC}"
echo ""

# Function to find module file for a workflow
find_module_file() {
    local workflow_name=$1
    local module_dir=$2
    
    # Create variations of the workflow name
    # e.g., access_point_location -> accesspoint_location, accesspointlocation
    local name_no_underscores=$(echo "$workflow_name" | tr -d '_')
    # Handle access_point -> accesspoint (remove underscore between access and point)
    local name_accesspoint=$(echo "$workflow_name" | sed 's/access_point/accesspoint/')
    
    # Common module naming patterns (in order of preference)
    local patterns=(
        "${workflow_name}_workflow_manager.py"
        "${name_accesspoint}_workflow_manager.py"
        "${name_no_underscores}_workflow_manager.py"
        "${workflow_name}_manager.py"
        "${name_accesspoint}_manager.py"
        "${name_no_underscores}_manager.py"
        "${workflow_name}_workflow.py"
        "${workflow_name}.py"
    )
    
    # Search for module file with maxdepth to limit search
    for pattern in "${patterns[@]}"; do
        # First try direct path (most common case)
        if [ -f "$module_dir/$pattern" ]; then
            echo "$module_dir/$pattern"
            return 0
        fi
        
        # Then try with find but limit depth to 2 levels
        local module_file=$(find "$module_dir" -maxdepth 2 -type f -name "$pattern" 2>/dev/null | head -n 1)
        if [ -n "$module_file" ]; then
            echo "$module_file"
            return 0
        fi
    done
    
    return 1
}

# Determine which workflows to process
if [ -n "$MAPPING_FILE" ]; then
    # If mapping file is provided, only process workflows listed in it
    workflows_to_process=$(grep -v "^#" "$MAPPING_FILE" | grep -v "^[[:space:]]*$" | cut -d: -f1 | xargs)
else
    # Otherwise, process all workflows in the directory
    workflows_to_process=$(find "$WORKFLOWS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
fi

# Iterate through workflows to process
for workflow_name in $workflows_to_process; do
    workflow_dir="$WORKFLOWS_DIR/$workflow_name"
    
    if [ ! -d "$workflow_dir" ]; then
        echo -e "${YELLOW}  ⚠ Workflow directory not found: $workflow_dir${NC}"
        continue
    fi
    
    schema_dir="$workflow_dir/schema"
    
    # Skip if no schema directory
    if [ ! -d "$schema_dir" ]; then
        if [ "$VERBOSE" = true ]; then
            echo -e "${YELLOW}  ⚠ No schema directory for: $workflow_name${NC}"
        fi
        continue
    fi
    
    # Find schema files (excluding delete schemas)
    schema_files=$(find "$schema_dir" -type f -name "*_schema.yml" ! -name "delete_*" 2>/dev/null)
    
    if [ -z "$schema_files" ]; then
        if [ "$VERBOSE" = true ]; then
            echo -e "${YELLOW}  ⚠ No schema files found for: $workflow_name${NC}"
        fi
        continue
    fi
    
    # Increment workflow counter
    current_workflow=$((current_workflow + 1))
    
    # Process each schema file
    for schema_file in $schema_files; do
        total_schemas=$((total_schemas + 1))
        schema_basename=$(basename "$schema_file")
        
        echo -e "${BLUE}[Workflow $current_workflow/$total_workflows] Processing: $workflow_name / $schema_basename${NC}"
        
        # Find corresponding module file
        # First check if there's a mapping in the mapping file
        mapped_module=$(get_mapped_module "$workflow_name" "$MAPPING_FILE")
        
        if [ -n "$mapped_module" ]; then
            # Check if it's an absolute path or just a filename
            if [[ "$mapped_module" = /* ]]; then
                module_file="$mapped_module"
            else
                module_file="$MODULE_DIR/$mapped_module"
            fi
            
            # Verify the mapped file exists
            if [ ! -f "$module_file" ]; then
                echo -e "${YELLOW}  ⚠ Mapped module file not found: $module_file${NC}"
                echo "SKIPPED: $workflow_name / $schema_basename - Mapped module not found" >> "$SUMMARY_FILE"
                skipped_validations=$((skipped_validations + 1))
                continue
            fi
            
            if [ "$VERBOSE" = true ]; then
                echo "  Using mapped module: $(basename "$module_file")"
            fi
        else
            # Use automatic pattern matching
            module_file=$(find_module_file "$workflow_name" "$MODULE_DIR")
        fi
        
        if [ -z "$module_file" ]; then
            echo -e "${YELLOW}  ⚠ Module file not found for $workflow_name${NC}"
            echo "SKIPPED: $workflow_name / $schema_basename - Module not found" >> "$SUMMARY_FILE"
            skipped_validations=$((skipped_validations + 1))
            continue
        fi
        
        echo -e "  Module: $(basename "$module_file")"
        echo -e "  Schema: $schema_basename"
        
        # Generate output filename
        output_file="$OUTPUT_DIR/${workflow_name}_validation_report.html"
        
        # Run validation
        verbose_flag=""
        if [ "$VERBOSE" = true ]; then
            verbose_flag="--verbose"
        fi
        
        # Create a temporary file for error output
        error_file=$(mktemp)
        
        # Run validation and capture output
        if python3 "$VALIDATOR_SCRIPT" "$module_file" "$schema_file" --output "$output_file" $verbose_flag 2>"$error_file"; then
            # Check if output file was created
            if [ -f "$output_file" ]; then
                # Try to extract mismatch count from the HTML file
                mismatch_count=$(grep -o "Found [0-9]* mismatch" "$output_file" 2>/dev/null | grep -o "[0-9]*" || echo "0")
                
                if [ "$mismatch_count" -eq 0 ] || [ -z "$mismatch_count" ]; then
                    echo -e "  ${GREEN}✓ Success: No mismatches found${NC}"
                    echo "SUCCESS: $workflow_name / $schema_basename - No mismatches" >> "$SUMMARY_FILE"
                else
                    echo -e "  ${YELLOW}⚠ Warning: $mismatch_count mismatch(es) found${NC}"
                    echo "WARNING: $workflow_name / $schema_basename - $mismatch_count mismatch(es)" >> "$SUMMARY_FILE"
                fi
                successful_validations=$((successful_validations + 1))
            else
                echo -e "  ${RED}✗ Failed: Output file not created${NC}"
                echo "FAILED: $workflow_name / $schema_basename - Output file not created" >> "$SUMMARY_FILE"
                failed_validations=$((failed_validations + 1))
            fi
        else
            echo -e "  ${RED}✗ Failed: Validation error${NC}"
            if [ "$VERBOSE" = true ] && [ -s "$error_file" ]; then
                echo -e "  ${RED}Error details:${NC}"
                cat "$error_file" | head -5
            fi
            echo "FAILED: $workflow_name / $schema_basename - Validation error" >> "$SUMMARY_FILE"
            failed_validations=$((failed_validations + 1))
        fi
        
        # Clean up temp file
        rm -f "$error_file"
        
        echo ""
    done
done

# Print summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total schemas processed: $total_schemas"
echo -e "${GREEN}Successful validations: $successful_validations${NC}"
echo -e "${RED}Failed validations: $failed_validations${NC}"
echo -e "${YELLOW}Skipped validations: $skipped_validations${NC}"
echo ""
echo -e "Reports saved to: ${BLUE}$OUTPUT_DIR${NC}"
echo -e "Summary saved to: ${BLUE}$SUMMARY_FILE${NC}"

# Append summary statistics
echo "" >> "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"
echo "Statistics" >> "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"
echo "Total schemas processed: $total_schemas" >> "$SUMMARY_FILE"
echo "Successful validations: $successful_validations" >> "$SUMMARY_FILE"
echo "Failed validations: $failed_validations" >> "$SUMMARY_FILE"
echo "Skipped validations: $skipped_validations" >> "$SUMMARY_FILE"

# Exit with appropriate code
if [ $failed_validations -gt 0 ]; then
    exit 1
else
    exit 0
fi
