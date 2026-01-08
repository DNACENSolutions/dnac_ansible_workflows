import yaml
import re
import os
import sys
import argparse


def parse_yamale_schema(schema_file_path):
    """
    Parse a yamale schema file and extract field definitions from the main detail field only.
    Ignores global catalyst_center_* and other configuration variables.
    
    Args:
        schema_file_path (str): Path to the yamale schema file.
    
    Returns:
        dict: Parsed schema structure with field names and their constraints from the detail field.
    """
    schema_fields = {}
    detail_field_name = None
    detail_type_name = None
    
    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split by --- to handle multiple schema sections
        sections = content.split('---')
        
        # First pass: Find the main detail field (e.g., pathtrace_details, inventory_details)
        first_section_lines = sections[0].strip().split('\n')
        i = 0
        while i < len(first_section_lines):
            line = first_section_lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            # Look for fields ending with _details or containing 'details'
            if ':' in stripped:
                parts = stripped.split(':', 1)
                field_name = parts[0].strip()
                field_def = parts[1].strip() if len(parts) > 1 else ''
                
                # Identify detail fields (ignore catalyst_center_*, jinjatemplate*, passwords_file)
                if ('_details' in field_name or 'details' in field_name) and \
                   not field_name.startswith('catalyst_center') and \
                   not field_name.startswith('jinjatemplate') and \
                   not field_name.startswith('passwords_file'):
                    detail_field_name = field_name
                    
                    # Check if this is a direct list definition or nested structure
                    if field_def:
                        # Direct definition: pathtrace_details: list(include('pathtrace_details_type'))
                        include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
                        if include_match:
                            detail_type_name = include_match.group(1)
                            break
                    else:
                        # Nested structure: inventory_details: \n  network_devices: list(...)
                        # Look at next line(s) for nested fields
                        i += 1
                        if i < len(first_section_lines):
                            next_line = first_section_lines[i]
                            # Check if next line is indented (nested field)
                            if next_line.startswith('  ') or next_line.startswith('\t'):
                                next_stripped = next_line.strip()
                                if ':' in next_stripped:
                                    next_parts = next_stripped.split(':', 1)
                                    next_field_def = next_parts[1].strip() if len(next_parts) > 1 else ''
                                    include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', next_field_def)
                                    if include_match:
                                        detail_type_name = include_match.group(1)
                                        break
            i += 1
        
        if not detail_field_name or not detail_type_name:
            return {"error": "Could not find main detail field in schema (e.g., *_details)"}
        
        # Second pass: Extract the type definition for the detail field
        # Handle chained includes (e.g., network_devices_type -> network_devices_type_type)
        for section in sections[1:]:  # Skip first section, look in type definitions
            lines = section.strip().split('\n')
            current_type = None
            
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Check if this is the type definition we're looking for
                if ':' in stripped and not stripped.startswith(' ') and not stripped.startswith('\t'):
                    parts = stripped.split(':', 1)
                    type_name = parts[0].strip()
                    if type_name == detail_type_name:
                        current_type = type_name
                        # Check if this is a chained include
                        if len(parts) > 1 and parts[1].strip():
                            field_def = parts[1].strip()
                            chained_include = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
                            if chained_include:
                                # Follow the chain
                                detail_type_name = chained_include.group(1)
                                current_type = None
                        continue
                
                # If we're inside the correct type definition, parse its fields
                if current_type == detail_type_name and ':' in stripped:
                    # This is a field within the type definition
                    parts = stripped.split(':', 1)
                    field_name = parts[0].strip()
                    field_def = parts[1].strip() if len(parts) > 1 else ''
                    schema_fields[field_name] = parse_field_definition(field_def)
        
        return schema_fields
    
    except FileNotFoundError:
        return {"error": f"Schema file not found: {schema_file_path}"}
    except Exception as e:
        return {"error": f"Error parsing schema file: {e}"}


def parse_field_definition(field_def):
    """
    Parse a yamale field definition to extract type and constraints.
    
    Args:
        field_def (str): Field definition string (e.g., "str(required=True)")
    
    Returns:
        dict: Parsed field information with type, required, default, etc.
    """
    field_info = {
        'raw': field_def,
        'type': None,
        'required': None,
        'default': None,
        'choices': [],
        'elements': None,
        'min': None,
        'max': None,
        'include': None
    }
    
    # Extract type (str, int, bool, list, dict, enum, any, include)
    type_match = re.match(r'^(\w+)\s*\(', field_def)
    if type_match:
        field_info['type'] = type_match.group(1)
    else:
        # Simple type without parentheses
        field_info['type'] = field_def.split('(')[0].strip()
    
    # Extract required
    required_match = re.search(r'required\s*=\s*(True|False)', field_def)
    if required_match:
        field_info['required'] = required_match.group(1) == 'True'
    
    # Extract default
    default_match = re.search(r'default\s*=\s*([^,)]+)', field_def)
    if default_match:
        field_info['default'] = default_match.group(1).strip()
    
    # Extract enum choices
    if field_info['type'] == 'enum':
        choices_match = re.findall(r'["\']([^"\']+)["\']', field_def)
        field_info['choices'] = choices_match
    
    # Extract list elements type
    if field_info['type'] == 'list':
        elements_match = re.search(r'list\s*\(\s*(\w+)\s*\(', field_def)
        if elements_match:
            field_info['elements'] = elements_match.group(1)
        else:
            # Check for include
            include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
            if include_match:
                field_info['include'] = include_match.group(1)
    
    # Extract include reference
    if field_info['type'] == 'include':
        include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
        if include_match:
            field_info['include'] = include_match.group(1)
    
    # Extract min/max
    min_match = re.search(r'min\s*=\s*(\d+)', field_def)
    if min_match:
        field_info['min'] = int(min_match.group(1))
    
    max_match = re.search(r'max\s*=\s*(\d+)', field_def)
    if max_match:
        field_info['max'] = int(max_match.group(1))
    
    return field_info


def extract_documentation_spec(module_file_path):
    """
    Extract the DOCUMENTATION spec from an Ansible module file.
    
    Args:
        module_file_path (str): Path to the Ansible module file.
    
    Returns:
        dict: Parsed DOCUMENTATION structure or error dict.
    """
    try:
        with open(module_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract DOCUMENTATION block
        documentation_match = re.search(r'DOCUMENTATION\s*=\s*r?["\']""(.*?)"""', content, re.DOTALL)
        if not documentation_match:
            documentation_match = re.search(r"DOCUMENTATION\s*=\s*r?'''(.*?)'''", content, re.DOTALL)
        
        if not documentation_match:
            return {"error": "Could not find DOCUMENTATION block"}
        
        documentation_yaml = documentation_match.group(1)
        
        try:
            documentation = yaml.safe_load(documentation_yaml)
            return documentation
        except yaml.YAMLError as e:
            return {"error": f"Error parsing DOCUMENTATION YAML: {e}"}
    
    except FileNotFoundError:
        return {"error": f"Module file not found: {module_file_path}"}
    except Exception as e:
        return {"error": f"Error reading module file: {e}"}


def get_doc_config_fields(documentation):
    """
    Extract field definitions from DOCUMENTATION config suboptions.
    
    Args:
        documentation (dict): Parsed DOCUMENTATION dictionary.
    
    Returns:
        dict: Field definitions from documentation.
    """
    doc_fields = {}
    
    if not documentation or 'error' in documentation:
        return doc_fields
    
    # Navigate to config suboptions
    config = documentation.get('options', {}).get('config', {})
    suboptions = config.get('suboptions', {})
    
    for field_name, field_spec in suboptions.items():
        doc_fields[field_name] = {
            'type': field_spec.get('type'),
            'required': field_spec.get('required', False),
            'default': field_spec.get('default'),
            'choices': field_spec.get('choices', []),
            'elements': field_spec.get('elements'),
            'description': field_spec.get('description', ''),
            'suboptions': field_spec.get('suboptions', {})
        }
    
    return doc_fields


def compare_schema_with_documentation(schema_fields, doc_fields, verbose=False):
    """
    Compare yamale schema fields with documentation fields and identify mismatches.
    
    Args:
        schema_fields (dict): Parsed yamale schema fields.
        doc_fields (dict): Parsed documentation fields.
        verbose (bool): Enable verbose output.
    
    Returns:
        list: List of mismatch descriptions.
    """
    mismatches = []
    
    if 'error' in schema_fields:
        return [f"Schema Error: {schema_fields['error']}"]
    
    if 'error' in doc_fields:
        return [f"Documentation Error: {doc_fields.get('error', 'Unknown error')}"]
    
    # Check for fields in schema but not in documentation
    for schema_field, schema_info in schema_fields.items():
        if schema_field.startswith('#') or not schema_field:
            continue
        
        # Skip internal schema definitions (those ending with _type)
        if schema_field.endswith('_type'):
            continue
        
        if schema_field not in doc_fields:
            mismatches.append(
                f"Field '{schema_field}' exists in schema but missing in DOCUMENTATION"
            )
            continue
        
        doc_info = doc_fields[schema_field]
        
        # Compare types
        schema_type = schema_info.get('type')
        doc_type = doc_info.get('type')
        
        # Map yamale types to Ansible types
        type_mapping = {
            'str': 'str',
            'int': 'int',
            'bool': 'bool',
            'list': 'list',
            'dict': 'dict',
            'enum': 'str',
            'any': None  # any type can match anything
        }
        
        expected_doc_type = type_mapping.get(schema_type)
        
        if expected_doc_type and doc_type and expected_doc_type != doc_type:
            mismatches.append(
                f"Type mismatch for '{schema_field}': Schema expects '{schema_type}', "
                f"Documentation has '{doc_type}'"
            )
        
        # Compare required status
        schema_required = schema_info.get('required')
        doc_required = doc_info.get('required', False)
        
        if schema_required is True and not doc_required:
            mismatches.append(
                f"Field '{schema_field}' is required in schema but not marked as required in DOCUMENTATION"
            )
        
        # Compare choices (for enum types)
        if schema_info.get('choices') and doc_info.get('choices'):
            schema_choices = set(schema_info['choices'])
            doc_choices = set(doc_info['choices'])
            
            if schema_choices != doc_choices:
                missing_in_doc = schema_choices - doc_choices
                extra_in_doc = doc_choices - schema_choices
                
                if missing_in_doc:
                    mismatches.append(
                        f"Choices mismatch for '{schema_field}': Missing in DOCUMENTATION: {missing_in_doc}"
                    )
                if extra_in_doc:
                    mismatches.append(
                        f"Choices mismatch for '{schema_field}': Extra in DOCUMENTATION: {extra_in_doc}"
                    )
        
        # Compare elements type for lists
        if schema_type == 'list':
            schema_elements = schema_info.get('elements')
            doc_elements = doc_info.get('elements')
            
            if schema_elements and doc_elements:
                # Map schema element types
                elem_type_mapping = {
                    'str': 'str',
                    'int': 'int',
                    'bool': 'bool',
                    'dict': 'dict'
                }
                expected_elem_type = elem_type_mapping.get(schema_elements)
                
                if expected_elem_type and expected_elem_type != doc_elements:
                    mismatches.append(
                        f"Elements type mismatch for '{schema_field}': Schema expects '{schema_elements}', "
                        f"Documentation has '{doc_elements}'"
                    )
    
    # Check for fields in documentation but not in schema
    for doc_field in doc_fields.keys():
        if doc_field not in schema_fields:
            # Check if it's not a type definition
            if not doc_field.endswith('_type'):
                mismatches.append(
                    f"Field '{doc_field}' exists in DOCUMENTATION but missing in schema"
                )
    
    if verbose:
        print(f"\nSchema fields: {list(schema_fields.keys())}")
        print(f"Documentation fields: {list(doc_fields.keys())}")
    
    return mismatches


def compare_module_with_schema(module_file_path, schema_file_path, verbose=False):
    """
    Compare a module's documentation with its corresponding yamale schema file.
    
    Args:
        module_file_path (str): Path to the Ansible module file.
        schema_file_path (str): Path to the yamale schema file.
        verbose (bool): Enable verbose output.
    
    Returns:
        tuple: (module_filename, schema_filename, list of mismatches)
    """
    module_filename = os.path.basename(module_file_path)
    schema_filename = os.path.basename(schema_file_path)
    
    if verbose:
        print(f"\nProcessing module: {module_filename}")
        print(f"Using schema: {schema_filename}")
    
    # Parse schema
    schema_fields = parse_yamale_schema(schema_file_path)
    
    # Extract documentation
    documentation = extract_documentation_spec(module_file_path)
    
    if 'error' in documentation:
        return (module_filename, schema_filename, [documentation['error']])
    
    # Get documentation fields
    doc_fields = get_doc_config_fields(documentation)
    
    # Compare
    mismatches = compare_schema_with_documentation(schema_fields, doc_fields, verbose)
    
    return (module_filename, schema_filename, mismatches)


def generate_html_report(results):
    """
    Generate an HTML report from the comparison results.
    
    Args:
        results (list of tuples): Each tuple contains (module_filename, schema_filename, list of mismatches).
    
    Returns:
        str: The HTML content of the report.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schema-Documentation Validation Report</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ margin-top: 2em; color: #555; }}
            .module-info {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f0f0f0; font-weight: bold; }}
            .success {{ color: green; font-weight: bold; }}
            .error {{ color: red; font-weight: bold; }}
            .warning {{ color: orange; }}
            .summary {{ background-color: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Schema-Documentation Validation Report</h1>
        <div class="summary">
            <h3>Summary</h3>
            <p>Total modules processed: <strong>{total}</strong></p>
            <p>Modules with mismatches: <strong class="error">{with_errors}</strong></p>
            <p>Modules without mismatches: <strong class="success">{without_errors}</strong></p>
        </div>
    """.format(
        total=len(results),
        with_errors=sum(1 for _, _, m in results if m),
        without_errors=sum(1 for _, _, m in results if not m)
    )
    
    for module_filename, schema_filename, mismatches in results:
        html += f"<h2>Module: {module_filename}</h2>"
        html += f"<div class='module-info'><strong>Schema:</strong> {schema_filename}</div>"
        
        if mismatches:
            html += "<table>\n"
            html += "<thead><tr><th>Mismatch Description</th></tr></thead>\n"
            html += "<tbody>\n"
            for mismatch in mismatches:
                html += f"<tr><td><span class='error'>{mismatch}</span></td></tr>\n"
            html += "</tbody>\n</table>\n"
        else:
            html += "<p><span class='success'>✓ Success: Documentation and schema match perfectly.</span></p>\n"
    
    html += """
    </body>
    </html>
    """
    return html


def show_help():
    """Display help information."""
    help_text = """
Schema-Documentation Validator
==============================

This tool compares Ansible module DOCUMENTATION specs with yamale schema files
and generates a report of any mismatches found.

Usage:
    python schema_doc_validator.py <module_path> <schema_path> [options]

Arguments:
    module_path     Path to the Ansible module file (.py)
    schema_path     Path to the yamale schema file (.yml)

Options:
    --verbose       Enable verbose output
    --output FILE   Specify output HTML report filename (default: schema_doc_validation_report.html)
    --help          Show this help message

Examples:
    # Compare a single module with its schema
    python schema_doc_validator.py plugins/modules/inventory_workflow_manager.py \\
        workflows/inventory/schema/inventory_schema.yml

    # With verbose output
    python schema_doc_validator.py module.py schema.yml --verbose

    # Custom output file
    python schema_doc_validator.py module.py schema.yml --output my_report.html
"""
    print(help_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare Ansible module documentation with yamale schema files.",
        add_help=False
    )
    parser.add_argument("module_path", nargs='?', help="Path to the Ansible module file")
    parser.add_argument("schema_path", nargs='?', help="Path to the yamale schema file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", default="schema_doc_validation_report.html", 
                       help="Output HTML report filename")
    parser.add_argument("--help", action="store_true", help="Show help message")
    
    args = parser.parse_args()
    
    if args.help or not args.module_path or not args.schema_path:
        show_help()
        sys.exit(0)
    
    module_path = args.module_path
    schema_path = args.schema_path
    verbose = args.verbose
    output_file = args.output
    
    # Validate paths
    if not os.path.isfile(module_path):
        print(f"Error: Module file not found: {module_path}")
        sys.exit(1)
    
    if not os.path.isfile(schema_path):
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)
    
    print(f"Comparing module with schema...")
    print(f"Module: {module_path}")
    print(f"Schema: {schema_path}")
    
    # Perform comparison
    result = compare_module_with_schema(module_path, schema_path, verbose)
    
    # Generate report
    html_report = generate_html_report([result])
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"\n✓ HTML report generated: {output_file}")
        
        # Print summary to console
        module_filename, schema_filename, mismatches = result
        if mismatches:
            print(f"\n⚠ Found {len(mismatches)} mismatch(es):")
            for mismatch in mismatches:
                print(f"  - {mismatch}")
        else:
            print("\n✓ No mismatches found. Documentation and schema are in sync.")
    
    except Exception as e:
        print(f"Error writing HTML report: {e}")
        sys.exit(1)
