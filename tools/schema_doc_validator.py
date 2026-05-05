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
        # Only split on standalone '---' lines (not '---' inside comments like '# ------')
        sections = re.split(r'^---\s*$', content, flags=re.MULTILINE)
        
        # Find the section with the main detail field
        # Some schemas start with ---, so the first section might be empty
        first_section_lines = []
        for section in sections:
            section_lines = section.strip().split('\n')
            # Skip empty sections or sections with only comments
            has_content = any(line.strip() and not line.strip().startswith('#') for line in section_lines)
            if has_content:
                first_section_lines = section_lines
                break
        
        # System fields to ignore when searching for main detail field
        _SYSTEM_FIELD_PREFIXES = ('catalyst_center', 'jinjatemplate', 'passwords_file')
        _SYSTEM_FIELD_NAMES = ('config_verify',)

        def _is_system_field(name):
            return (name.startswith(_SYSTEM_FIELD_PREFIXES) or name in _SYSTEM_FIELD_NAMES)

        def _try_extract_detail_field(lines):
            """Return (detail_field_name, detail_type_name) or (None, None)."""
            i = 0
            fallback_field = None
            fallback_type = None
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    i += 1
                    continue
                if ':' in stripped:
                    parts = stripped.split(':', 1)
                    field_name = parts[0].strip()
                    field_def = parts[1].strip() if len(parts) > 1 else ''
                    if not _is_system_field(field_name):
                        include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
                        if include_match:
                            type_name = include_match.group(1)
                            # Prefer _details fields; otherwise keep first match as fallback
                            if 'details' in field_name:
                                return field_name, type_name
                            elif fallback_field is None:
                                fallback_field = field_name
                                fallback_type = type_name
                        elif not field_def:
                            # Nested structure: field_name: \n  sub_field: list(include(...))
                            i += 1
                            if i < len(lines):
                                next_line = lines[i]
                                if next_line.startswith('  ') or next_line.startswith('\t'):
                                    next_stripped = next_line.strip()
                                    if ':' in next_stripped:
                                        next_parts = next_stripped.split(':', 1)
                                        next_field_def = next_parts[1].strip() if len(next_parts) > 1 else ''
                                        include_match = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', next_field_def)
                                        if include_match:
                                            type_name = include_match.group(1)
                                            if 'details' in field_name:
                                                return field_name, type_name
                                            elif fallback_field is None:
                                                fallback_field = field_name
                                                fallback_type = type_name
                i += 1
            return fallback_field, fallback_type

        # First pass: Find the main detail field
        # Prefers fields with '_details' in the name; falls back to first list(include(...)) field
        detail_field_name, detail_type_name = _try_extract_detail_field(first_section_lines)
        
        if not detail_field_name or not detail_type_name:
            return {"error": f"Could not find main detail field in schema. Searched in {len(first_section_lines)} lines."}
        
        # Build a lookup: type_name -> list of (field_name, field_def) from all sections
        type_definitions = {}
        for section in sections[1:]:
            lines = section.strip().split('\n')
            current_type = None
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if ':' in stripped and not line.startswith(' ') and not line.startswith('\t'):
                    parts = stripped.split(':', 1)
                    type_name = parts[0].strip()
                    field_def = parts[1].strip() if len(parts) > 1 else ''
                    # Check for chained include at type level
                    chained = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', field_def)
                    if chained:
                        # Alias: this type redirects to another
                        type_definitions.setdefault(type_name, [])
                        type_definitions[type_name].append(('__chain__', chained.group(1)))
                    else:
                        type_definitions.setdefault(type_name, [])
                        current_type = type_name
                elif current_type and ':' in stripped:
                    parts = stripped.split(':', 1)
                    f_name = parts[0].strip()
                    f_def = parts[1].strip() if len(parts) > 1 else ''
                    type_definitions[current_type].append((f_name, f_def))

        # Recursively collect all fields from a type and its nested includes
        def collect_fields(type_name, visited=None):
            if visited is None:
                visited = set()
            if type_name in visited:
                return {}
            visited.add(type_name)
            fields = {}
            for f_name, f_def in type_definitions.get(type_name, []):
                if f_name == '__chain__':
                    # Follow chain/alias
                    fields.update(collect_fields(f_def, visited))
                else:
                    fields[f_name] = parse_field_definition(f_def)
                    # Follow include references recursively
                    nested_include = re.search(r'include\s*\(\s*["\']([^"\']+)["\']', f_def)
                    if nested_include:
                        fields.update(collect_fields(nested_include.group(1), visited))
            return fields

        schema_fields = collect_fields(detail_type_name)
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


def parse_suboptions_recursive(suboptions, parent_path=''):
    """
    Recursively parse suboptions and flatten them into a single dict.
    
    Args:
        suboptions (dict): Dictionary of suboptions to parse.
        parent_path (str): Parent field path (used for nested fields).
    
    Returns:
        dict: Flattened field definitions with nested fields included.
    """
    fields = {}
    
    for field_name, field_spec in suboptions.items():
        # Create full field path
        full_path = f"{parent_path}.{field_name}" if parent_path else field_name
        
        # Store field info
        fields[field_name] = {
            'type': field_spec.get('type'),
            'required': field_spec.get('required', False),
            'default': field_spec.get('default'),
            'choices': field_spec.get('choices', []),
            'elements': field_spec.get('elements'),
            'description': field_spec.get('description', ''),
            'suboptions': {}
        }
        
        # Recursively process nested suboptions
        nested_suboptions = field_spec.get('suboptions', {})
        if nested_suboptions:
            # Parse nested fields recursively
            nested_fields = parse_suboptions_recursive(nested_suboptions, full_path)
            fields[field_name]['suboptions'] = nested_fields
            
            # Also add nested fields to the root level with full path
            # This helps with flat comparison against schema
            for nested_name, nested_spec in nested_fields.items():
                fields[nested_name] = nested_spec
        
        # Handle list elements with suboptions
        if field_spec.get('type') == 'list' and 'suboptions' in field_spec:
            elements_suboptions = field_spec.get('suboptions', {})
            if elements_suboptions:
                nested_fields = parse_suboptions_recursive(elements_suboptions, full_path)
                fields[field_name]['suboptions'] = nested_fields
                # Add nested fields to root level
                for nested_name, nested_spec in nested_fields.items():
                    fields[nested_name] = nested_spec
    
    return fields


def get_doc_config_fields(documentation):
    """
    Extract field definitions from DOCUMENTATION config suboptions recursively.
    
    Args:
        documentation (dict): Parsed DOCUMENTATION dictionary.
    
    Returns:
        dict: Field definitions from documentation, including all nested fields.
    """
    doc_fields = {}
    
    if not documentation or 'error' in documentation:
        return doc_fields
    
    # Navigate to config suboptions
    config = documentation.get('options', {}).get('config', {})
    suboptions = config.get('suboptions', {})
    
    # Recursively parse all suboptions
    doc_fields = parse_suboptions_recursive(suboptions)
    
    return doc_fields


def _build_top_level_options(full_documentation):
    """
    Extract non-system top-level options from DOCUMENTATION as a fallback lookup.

    Schema detail types may contain fields (e.g. file_path, file_mode, config)
    that are documented as top-level module options rather than config suboptions.
    This helper builds a dict of those options so the comparison can fall back to
    them when a schema field is not found in config.suboptions.

    Args:
        full_documentation (dict): The full parsed DOCUMENTATION dictionary.

    Returns:
        dict: Mapping of option name to parsed field info.
    """
    _SYSTEM_PREFIXES = ('dnac_', 'catalyst_center_')
    _SYSTEM_NAMES = ('state', 'validate_response_schema', 'config_verify')

    top_level = {}
    if not full_documentation or not isinstance(full_documentation, dict):
        return top_level

    for opt_name, opt_spec in full_documentation.get('options', {}).items():
        if any(opt_name.startswith(p) for p in _SYSTEM_PREFIXES):
            continue
        if opt_name in _SYSTEM_NAMES:
            continue
        if not isinstance(opt_spec, dict):
            continue
        top_level[opt_name] = {
            'type': opt_spec.get('type'),
            'required': opt_spec.get('required', False),
            'default': opt_spec.get('default'),
            'choices': opt_spec.get('choices', []),
            'elements': opt_spec.get('elements'),
            'description': opt_spec.get('description', ''),
            'suboptions': {}
        }
    return top_level


def compare_schema_with_documentation(schema_fields, doc_fields, verbose=False, full_documentation=None, exclude_fields=None):
    """
    Compare yamale schema fields with documentation fields and identify mismatches.
    
    Args:
        schema_fields (dict): Parsed yamale schema fields.
        doc_fields (dict): Parsed documentation fields.
        verbose (bool): Enable verbose output.
        full_documentation (dict): Full parsed DOCUMENTATION dict used as
            fallback for top-level options not inside config.suboptions.
        exclude_fields (set): Field names to skip during comparison
            (e.g. playbook-only convenience parameters).
    
    Returns:
        list: List of mismatch descriptions.
    """
    mismatches = []
    
    if 'error' in schema_fields:
        return [f"Schema Error: {schema_fields['error']}"]
    
    if 'error' in doc_fields:
        return [f"Documentation Error: {doc_fields.get('error', 'Unknown error')}"]
    
    # Build fallback lookup from top-level DOCUMENTATION options so that
    # schema fields mapped to top-level module params (e.g. file_path,
    # file_mode, config) are not falsely reported as missing.
    top_level_options = _build_top_level_options(full_documentation)
    
    if exclude_fields is None:
        exclude_fields = set()

    # Check for fields in schema but not in documentation
    for schema_field, schema_info in schema_fields.items():
        if schema_field.startswith('#') or not schema_field:
            continue
        
        # Skip internal schema definitions (those ending with _type)
        if schema_field.endswith('_type'):
            continue

        # Skip playbook-only / workflow-level convenience fields
        if schema_field in exclude_fields:
            continue
        
        if schema_field in doc_fields:
            doc_info = doc_fields[schema_field]
        elif schema_field in top_level_options:
            doc_info = top_level_options[schema_field]
        else:
            mismatches.append(
                f"Field '{schema_field}' exists in schema but missing in DOCUMENTATION"
            )
            continue
        
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


def compare_module_with_schema(module_file_path, schema_file_path, verbose=False, exclude_fields=None):
    """
    Compare a module's documentation with its corresponding yamale schema file.
    
    Args:
        module_file_path (str): Path to the Ansible module file.
        schema_file_path (str): Path to the yamale schema file.
        verbose (bool): Enable verbose output.
        exclude_fields (set): Field names to skip during comparison.
    
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
    
    # Compare (pass full documentation for top-level option fallback)
    mismatches = compare_schema_with_documentation(schema_fields, doc_fields, verbose, documentation, exclude_fields)
    
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
    --exclude-fields FIELDS  Comma-separated schema field names to skip (playbook-only fields)
    --help          Show this help message

Examples:
    # Compare a single module with its schema
    python schema_doc_validator.py plugins/modules/inventory_workflow_manager.py \\
        workflows/inventory/schema/inventory_schema.yml

    # With verbose output
    python schema_doc_validator.py module.py schema.yml --verbose

    # Exclude playbook-only fields
    python schema_doc_validator.py module.py schema.yml \\
        --exclude-fields generate_all_configurations

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
    parser.add_argument("--exclude-fields", default="",
                       help="Comma-separated list of schema field names to skip (playbook-only fields)")
    parser.add_argument("--help", action="store_true", help="Show help message")
    
    args = parser.parse_args()
    
    if args.help or not args.module_path or not args.schema_path:
        show_help()
        sys.exit(0)
    
    module_path = args.module_path
    schema_path = args.schema_path
    verbose = args.verbose
    output_file = args.output
    exclude_fields = set(f.strip() for f in args.exclude_fields.split(',') if f.strip())
    
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
    
    if exclude_fields and verbose:
        print(f"Excluding fields: {exclude_fields}")

    # Perform comparison
    result = compare_module_with_schema(module_path, schema_path, verbose, exclude_fields)
    
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
