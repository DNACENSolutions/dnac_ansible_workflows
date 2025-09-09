#!/usr/bin/env python3
"""
Comprehensive Schema Validation Tool for DNAC Ansible Workflows

This tool validates all workflow variable files against their corresponding schema files
using yamale for YAML schema validation.
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import yamale
from yamale import YamaleError
import yaml
from typing import List, Tuple, Dict
import json

class WorkflowValidator:
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.results = []
        self.total_validations = 0
        self.successful_validations = 0
        self.failed_validations = 0
        
    def find_workflow_directories(self) -> List[Path]:
        """Find all workflow directories that contain both schema and vars subdirectories."""
        workflow_dirs = []
        
        if not self.workflows_dir.exists():
            print(f"Error: Workflows directory '{self.workflows_dir}' not found.")
            return workflow_dirs
            
        for item in self.workflows_dir.iterdir():
            if item.is_dir():
                schema_dir = item / "schema"
                vars_dir = item / "vars"
                if schema_dir.exists() and vars_dir.exists():
                    workflow_dirs.append(item)
                    
        return sorted(workflow_dirs)
    
    def get_schema_files(self, workflow_dir: Path) -> List[Path]:
        """Get all schema files from a workflow's schema directory."""
        schema_dir = workflow_dir / "schema"
        schema_files = []
        
        for ext in ['*.yml', '*.yaml']:
            schema_files.extend(schema_dir.glob(ext))
            
        return sorted(schema_files)
    
    def get_vars_files(self, workflow_dir: Path) -> List[Path]:
        """Get all variable files from a workflow's vars directory."""
        vars_dir = workflow_dir / "vars"
        vars_files = []
        
        for ext in ['*.yml', '*.yaml']:
            vars_files.extend(vars_dir.glob(ext))
            
        return sorted(vars_files)
    
    def match_schema_to_vars(self, schema_files: List[Path], vars_files: List[Path]) -> List[Tuple[Path, Path]]:
        """Match schema files to their corresponding variable files based on naming patterns."""
        matches = []
        
        for schema_file in schema_files:
            schema_name = schema_file.stem.lower()
            
            # Remove common schema suffixes to find base name
            schema_base = schema_name
            for suffix in ['_schema', 'schema']:
                if schema_base.endswith(suffix):
                    schema_base = schema_base[:-len(suffix)]
                    break
            
            # Look for matching vars files with enhanced logic
            matched = False
            for vars_file in vars_files:
                vars_name = vars_file.stem.lower()
                
                # Skip jinja template files for schema validation
                if vars_name.startswith('jinja_') or '_jinja_' in vars_name:
                    continue
                
                # Remove common vars suffixes
                vars_base = vars_name
                for suffix in ['_vars', '_inputs', '_input', 'vars']:
                    if vars_base.endswith(suffix):
                        vars_base = vars_base[:-len(suffix)]
                        break
                
                # Enhanced matching logic - match delete schemas with delete vars, non-delete with non-delete
                if schema_base.startswith('delete_') and vars_base.startswith('delete_'):
                    # Both are delete operations - match them
                    schema_clean = schema_base[7:]  # Remove 'delete_' prefix
                    vars_clean = vars_base[7:]      # Remove 'delete_' prefix
                    if (vars_clean in schema_clean or schema_clean in vars_clean or
                        schema_clean.replace('_', '') in vars_clean.replace('_', '') or
                        vars_clean.replace('_', '') in schema_clean.replace('_', '') or
                        (schema_clean == 'plug_and_play' and vars_clean == 'catalyst_center_pnp') or
                        (schema_clean == 'catalyst_center_pnp' and vars_clean == 'plug_and_play')):
                        matches.append((schema_file, vars_file))
                        matched = True
                        break
                elif not schema_base.startswith('delete_') and not vars_base.startswith('delete_'):
                    # Both are non-delete operations - match them
                    # Prioritize exact matches and avoid delete files
                    if (not vars_name.startswith('delete_') and 
                        (vars_base in schema_base or schema_base in vars_base or
                         schema_base.replace('_', '') in vars_base.replace('_', '') or
                         vars_base.replace('_', '') in schema_base.replace('_', '') or
                         (schema_base == 'plug_and_play' and vars_base == 'catalyst_center_pnp') or
                         (schema_base == 'catalyst_center_pnp' and vars_base == 'plug_and_play') or
                         any(part in vars_base for part in schema_base.split('_') if len(part) > 3))):
                        matches.append((schema_file, vars_file))
                        matched = True
                        break
            
            # If no specific match found, don't add random matches
            if not matched:
                # Only add a fallback match if there's exactly one vars file
                if len(vars_files) == 1:
                    matches.append((schema_file, vars_files[0]))
                    
        return matches
    
    def validate_file_pair(self, schema_file: Path, vars_file: Path) -> Dict:
        """Validate a single vars file against a schema file."""
        result = {
            'workflow': schema_file.parent.parent.name,
            'schema_file': schema_file.name,
            'vars_file': vars_file.name,
            'status': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load schema
            schema = yamale.make_schema(str(schema_file))
            
            # Load data
            data = yamale.make_data(str(vars_file))
            
            # Validate
            yamale.validate(schema, data)
            
            result['status'] = 'success'
            self.successful_validations += 1
            
        except YamaleError as e:
            result['status'] = 'failed'
            result['errors'] = [str(e)]
            self.failed_validations += 1
            
        except FileNotFoundError as e:
            result['status'] = 'error'
            result['errors'] = [f"File not found: {e}"]
            self.failed_validations += 1
            
        except yaml.YAMLError as e:
            result['status'] = 'error'
            result['errors'] = [f"YAML parsing error: {e}"]
            self.failed_validations += 1
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'] = [f"Unexpected error: {e}"]
            self.failed_validations += 1
            
        self.total_validations += 1
        return result
    
    def validate_workflow(self, workflow_dir: Path) -> List[Dict]:
        """Validate all schema-vars pairs in a workflow directory."""
        workflow_results = []
        
        schema_files = self.get_schema_files(workflow_dir)
        vars_files = self.get_vars_files(workflow_dir)
        
        if not schema_files:
            workflow_results.append({
                'workflow': workflow_dir.name,
                'schema_file': 'N/A',
                'vars_file': 'N/A',
                'status': 'warning',
                'errors': [],
                'warnings': ['No schema files found']
            })
            return workflow_results
            
        if not vars_files:
            workflow_results.append({
                'workflow': workflow_dir.name,
                'schema_file': 'N/A',
                'vars_file': 'N/A',
                'status': 'warning',
                'errors': [],
                'warnings': ['No vars files found']
            })
            return workflow_results
        
        # Match schemas to vars and validate
        matches = self.match_schema_to_vars(schema_files, vars_files)
        
        if not matches:
            # If no matches found, validate each schema against each vars file
            for schema_file in schema_files:
                for vars_file in vars_files:
                    result = self.validate_file_pair(schema_file, vars_file)
                    workflow_results.append(result)
        else:
            for schema_file, vars_file in matches:
                result = self.validate_file_pair(schema_file, vars_file)
                workflow_results.append(result)
                
        return workflow_results
    
    def validate_all_workflows(self) -> None:
        """Validate all workflows in the workflows directory."""
        workflow_dirs = self.find_workflow_directories()
        
        if not workflow_dirs:
            print("No workflow directories with both schema and vars found.")
            return
            
        print(f"Found {len(workflow_dirs)} workflows to validate...")
        print("=" * 80)
        
        for workflow_dir in workflow_dirs:
            print(f"\nValidating workflow: {workflow_dir.name}")
            print("-" * 50)
            
            workflow_results = self.validate_workflow(workflow_dir)
            self.results.extend(workflow_results)
            
            # Print immediate results for this workflow
            for result in workflow_results:
                status_symbol = "✓" if result['status'] == 'success' else "✗" if result['status'] == 'failed' else "⚠"
                print(f"{status_symbol} {result['schema_file']} -> {result['vars_file']}: {result['status'].upper()}")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"    ERROR: {error}")
                        
                if result['warnings']:
                    for warning in result['warnings']:
                        print(f"    WARNING: {warning}")
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of all validations."""
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY REPORT")
        print("=" * 80)
        
        print(f"Total validations performed: {self.total_validations}")
        print(f"Successful validations: {self.successful_validations}")
        print(f"Failed validations: {self.failed_validations}")
        
        if self.total_validations > 0:
            success_rate = (self.successful_validations / self.total_validations) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        # Group results by status
        failed_results = [r for r in self.results if r['status'] == 'failed']
        error_results = [r for r in self.results if r['status'] == 'error']
        warning_results = [r for r in self.results if r['status'] == 'warning']
        
        if failed_results:
            print(f"\nFAILED VALIDATIONS ({len(failed_results)}):")
            print("-" * 40)
            for result in failed_results:
                print(f"  {result['workflow']}: {result['schema_file']} -> {result['vars_file']}")
                for error in result['errors']:
                    print(f"    - {error}")
        
        if error_results:
            print(f"\nERRORS ({len(error_results)}):")
            print("-" * 40)
            for result in error_results:
                print(f"  {result['workflow']}: {result['schema_file']} -> {result['vars_file']}")
                for error in result['errors']:
                    print(f"    - {error}")
        
        if warning_results:
            print(f"\nWARNINGS ({len(warning_results)}):")
            print("-" * 40)
            for result in warning_results:
                print(f"  {result['workflow']}: {result['schema_file']} -> {result['vars_file']}")
                for warning in result['warnings']:
                    print(f"    - {warning}")
    
    def save_detailed_report(self, output_file: str = "schema_validation_report.json") -> None:
        """Save detailed results to a JSON file."""
        report_data = {
            'summary': {
                'total_validations': self.total_validations,
                'successful_validations': self.successful_validations,
                'failed_validations': self.failed_validations,
                'success_rate': (self.successful_validations / self.total_validations * 100) if self.total_validations > 0 else 0
            },
            'results': self.results
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\nDetailed report saved to: {output_file}")
        except Exception as e:
            print(f"Error saving report: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Schema Validation for DNAC Ansible Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all workflows in the current directory
  python comprehensive_schema_validation.py
  
  # Validate workflows in a specific directory
  python comprehensive_schema_validation.py --workflows-dir /path/to/workflows
  
  # Save detailed report to a specific file
  python comprehensive_schema_validation.py --output report.json
  
  # Validate a specific workflow
  python comprehensive_schema_validation.py --workflow device_discovery
        """
    )
    
    parser.add_argument(
        '--workflows-dir',
        default='workflows',
        help='Directory containing workflow subdirectories (default: workflows)'
    )
    
    parser.add_argument(
        '--workflow',
        help='Validate only a specific workflow by name'
    )
    
    parser.add_argument(
        '--output',
        default='schema_validation_report.json',
        help='Output file for detailed JSON report (default: schema_validation_report.json)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only show summary, suppress detailed output'
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = WorkflowValidator(args.workflows_dir)
    
    if args.workflow:
        # Validate specific workflow
        workflow_path = Path(args.workflows_dir) / args.workflow
        if not workflow_path.exists():
            print(f"Error: Workflow '{args.workflow}' not found in '{args.workflows_dir}'")
            sys.exit(1)
            
        print(f"Validating specific workflow: {args.workflow}")
        results = validator.validate_workflow(workflow_path)
        validator.results.extend(results)
        
        if not args.quiet:
            for result in results:
                status_symbol = "✓" if result['status'] == 'success' else "✗" if result['status'] == 'failed' else "⚠"
                print(f"{status_symbol} {result['schema_file']} -> {result['vars_file']}: {result['status'].upper()}")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"    ERROR: {error}")
                        
                if result['warnings']:
                    for warning in result['warnings']:
                        print(f"    WARNING: {warning}")
    else:
        # Validate all workflows
        if not args.quiet:
            validator.validate_all_workflows()
        else:
            # Quiet mode - just collect results
            workflow_dirs = validator.find_workflow_directories()
            for workflow_dir in workflow_dirs:
                workflow_results = validator.validate_workflow(workflow_dir)
                validator.results.extend(workflow_results)
    
    # Generate summary report
    validator.generate_summary_report()
    
    # Save detailed report
    validator.save_detailed_report(args.output)
    
    # Exit with appropriate code
    if validator.failed_validations > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
