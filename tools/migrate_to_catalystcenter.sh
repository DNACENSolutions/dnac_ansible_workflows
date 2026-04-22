#!/bin/bash
#
# Migration Script: cisco.dnac -> cisco.catalystcenter
# This script migrates all playbooks, documentation, and configuration files
# from cisco.dnac collection to cisco.catalystcenter collection
#
# Usage: ./migrate_to_catalystcenter.sh [--dry-run]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Dry run flag
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}Running in DRY RUN mode - no files will be modified${NC}\n"
fi

# Counters
TOTAL_FILES=0
MODIFIED_FILES=0

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

# Function to migrate a single file
migrate_file() {
    local file=$1
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file contains cisco.dnac
    if ! grep -q "cisco\.dnac\|dnac_host\|dnac_username\|dnac_password\|dnac_port\|dnac_verify\|dnac_version\|dnac_debug\|dnac_log" "$file" 2>/dev/null; then
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        print_status "info" "Would migrate: $file"
        MODIFIED_FILES=$((MODIFIED_FILES + 1))
        return 0
    fi
    
    # Create backup
    cp "$file" "${file}.bak"
    
    # Perform replacements
    # 1. Collection name
    sed -i '' 's/cisco\.dnac/cisco.catalystcenter/g' "$file"
    
    # 2. Module names in playbooks (keep the module name part after cisco.catalystcenter.)
    # This is already handled by the collection name replacement above
    
    # 3. Variable names in playbooks and inventory
    sed -i '' 's/dnac_host:/catalystcenter_host:/g' "$file"
    sed -i '' 's/dnac_host\([^a-zA-Z_]\)/catalystcenter_host\1/g' "$file"
    sed -i '' 's/dnac_host"/catalystcenter_host"/g' "$file"
    sed -i '' 's/dnac_host }}/catalystcenter_host }}/g' "$file"
    
    sed -i '' 's/dnac_username:/catalystcenter_username:/g' "$file"
    sed -i '' 's/dnac_username\([^a-zA-Z_]\)/catalystcenter_username\1/g' "$file"
    sed -i '' 's/dnac_username"/catalystcenter_username"/g' "$file"
    sed -i '' 's/dnac_username }}/catalystcenter_username }}/g' "$file"
    
    sed -i '' 's/dnac_password:/catalystcenter_password:/g' "$file"
    sed -i '' 's/dnac_password\([^a-zA-Z_]\)/catalystcenter_password\1/g' "$file"
    sed -i '' 's/dnac_password"/catalystcenter_password"/g' "$file"
    sed -i '' 's/dnac_password }}/catalystcenter_password }}/g' "$file"
    
    sed -i '' 's/dnac_port:/catalystcenter_port:/g' "$file"
    sed -i '' 's/dnac_port\([^a-zA-Z_]\)/catalystcenter_port\1/g' "$file"
    sed -i '' 's/dnac_port"/catalystcenter_port"/g' "$file"
    sed -i '' 's/dnac_port }}/catalystcenter_port }}/g' "$file"
    
    sed -i '' 's/dnac_verify:/catalystcenter_verify:/g' "$file"
    sed -i '' 's/dnac_verify\([^a-zA-Z_]\)/catalystcenter_verify\1/g' "$file"
    sed -i '' 's/dnac_verify"/catalystcenter_verify"/g' "$file"
    sed -i '' 's/dnac_verify }}/catalystcenter_verify }}/g' "$file"
    
    sed -i '' 's/dnac_version:/catalystcenter_version:/g' "$file"
    sed -i '' 's/dnac_version\([^a-zA-Z_]\)/catalystcenter_version\1/g' "$file"
    sed -i '' 's/dnac_version"/catalystcenter_version"/g' "$file"
    sed -i '' 's/dnac_version }}/catalystcenter_version }}/g' "$file"
    
    sed -i '' 's/dnac_debug:/catalystcenter_debug:/g' "$file"
    sed -i '' 's/dnac_debug\([^a-zA-Z_]\)/catalystcenter_debug\1/g' "$file"
    sed -i '' 's/dnac_debug"/catalystcenter_debug"/g' "$file"
    sed -i '' 's/dnac_debug }}/catalystcenter_debug }}/g' "$file"
    
    sed -i '' 's/dnac_log:/catalystcenter_log:/g' "$file"
    sed -i '' 's/dnac_log\([^a-zA-Z_]\)/catalystcenter_log\1/g' "$file"
    sed -i '' 's/dnac_log"/catalystcenter_log"/g' "$file"
    sed -i '' 's/dnac_log }}/catalystcenter_log }}/g' "$file"
    
    sed -i '' 's/dnac_log_level:/catalystcenter_log_level:/g' "$file"
    sed -i '' 's/dnac_log_level\([^a-zA-Z_]\)/catalystcenter_log_level\1/g' "$file"
    sed -i '' 's/dnac_log_level"/catalystcenter_log_level"/g' "$file"
    sed -i '' 's/dnac_log_level }}/catalystcenter_log_level }}/g' "$file"
    
    sed -i '' 's/dnac_log_file_path:/catalystcenter_log_file_path:/g' "$file"
    sed -i '' 's/dnac_log_file_path\([^a-zA-Z_]\)/catalystcenter_log_file_path\1/g' "$file"
    sed -i '' 's/dnac_log_file_path"/catalystcenter_log_file_path"/g' "$file"
    sed -i '' 's/dnac_log_file_path }}/catalystcenter_log_file_path }}/g' "$file"
    
    sed -i '' 's/dnac_log_append:/catalystcenter_log_append:/g' "$file"
    sed -i '' 's/dnac_log_append\([^a-zA-Z_]\)/catalystcenter_log_append\1/g' "$file"
    sed -i '' 's/dnac_log_append"/catalystcenter_log_append"/g' "$file"
    sed -i '' 's/dnac_log_append }}/catalystcenter_log_append }}/g' "$file"
    
    sed -i '' 's/dnac_api_task_timeout:/catalystcenter_api_task_timeout:/g' "$file"
    sed -i '' 's/dnac_api_task_timeout\([^a-zA-Z_]\)/catalystcenter_api_task_timeout\1/g' "$file"
    sed -i '' 's/dnac_api_task_timeout"/catalystcenter_api_task_timeout"/g' "$file"
    sed -i '' 's/dnac_api_task_timeout }}/catalystcenter_api_task_timeout }}/g' "$file"
    
    # 4. Update references to dnacentersdk (Python SDK)
    sed -i '' 's/dnacentersdk/catalystcentersdk/g' "$file"
    
    # 5. Update collection references in documentation
    sed -i '' 's/ansible-galaxy collection install cisco\.dnac/ansible-galaxy collection install cisco.catalystcenter/g' "$file"
    sed -i '' 's/dnacenter-ansible/catalystcenter-ansible/g' "$file"
    
    # Check if file was actually modified
    if ! diff -q "$file" "${file}.bak" > /dev/null 2>&1; then
        print_status "success" "Migrated: $(basename $file)"
        MODIFIED_FILES=$((MODIFIED_FILES + 1))
        rm "${file}.bak"
    else
        # No changes, remove backup
        rm "${file}.bak"
    fi
}

# Main execution
main() {
    print_status "info" "Starting migration from cisco.dnac to cisco.catalystcenter"
    print_status "info" "Repository: $REPO_ROOT"
    echo ""
    
    # Find all relevant files
    print_status "info" "Finding files to migrate..."
    
    # Migrate YAML files (playbooks, vars, inventory, schemas)
    while IFS= read -r -d '' file; do
        migrate_file "$file"
    done < <(find "$REPO_ROOT" -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)
    
    # Migrate Markdown files (documentation)
    while IFS= read -r -d '' file; do
        migrate_file "$file"
    done < <(find "$REPO_ROOT" -type f -name "*.md" -print0)
    
    # Migrate requirements files
    while IFS= read -r -d '' file; do
        migrate_file "$file"
    done < <(find "$REPO_ROOT" -type f -name "requirements*.txt" -print0)
    
    # Migrate config files
    if [ -f "$REPO_ROOT/ansible.cfg" ]; then
        migrate_file "$REPO_ROOT/ansible.cfg"
    fi
    
    if [ -f "$HOME/.ansible.cfg" ]; then
        print_status "warning" "Found ~/.ansible.cfg - you may need to manually update this file"
    fi
    
    # Summary
    echo ""
    print_status "info" "Migration Summary"
    echo "  Total files scanned: $TOTAL_FILES"
    echo "  Files modified: $MODIFIED_FILES"
    
    if [ "$DRY_RUN" = false ]; then
        echo ""
        print_status "success" "Migration completed successfully!"
        echo ""
        print_status "warning" "Next steps:"
        echo "  1. Review the changes: git diff"
        echo "  2. Update requirements: pip install catalystcentersdk"
        echo "  3. Install new collection: ansible-galaxy collection install cisco.catalystcenter --force"
        echo "  4. Test your playbooks in a lab environment"
        echo "  5. Commit changes: git add -A && git commit -m 'Migrate from cisco.dnac to cisco.catalystcenter'"
    else
        echo ""
        print_status "info" "Dry run completed. Run without --dry-run to apply changes."
    fi
}

# Run main function
main
