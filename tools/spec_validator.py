import yaml
import re
import ast
import os
import sys
import argparse


def normalize_spec_string(spec_str):
    """
    Normalize a spec string to make it parseable by ast.literal_eval.
    Handles common patterns like:
    - dict(key=value) syntax -> {"key": value}
    - Unquoted Python types (int, str, list, dict, bool) -> quoted strings
    - Comments
    
    Args:
        spec_str (str): The spec string to normalize.
    
    Returns:
        str: The normalized spec string.
    """
    # Remove inline comments (but preserve strings with # in them)
    # Note: spec_str might already be one long line without \n separators
    # so we process character by character
    result_chars = []
    in_string = False
    quote_char = None
    i = 0
    
    while i < len(spec_str):
        char = spec_str[i]
        
        # Track string boundaries
        if char in ('"', "'") and (i == 0 or spec_str[i-1] != '\\'):
            if not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char:
                in_string = False
                quote_char = None
        
        # If we encounter # outside of a string, skip everything until newline or end
        if char == '#' and not in_string:
            # Skip to end of line or end of string
            while i < len(spec_str) and spec_str[i] != '\n':
                i += 1
            if i < len(spec_str):
                # Include the newline
                result_chars.append('\n')
                i += 1
            continue
        
        result_chars.append(char)
        i += 1
    
    spec_str = ''.join(result_chars)
    
    # Replace dict(key=value, ...) with {"key": value, ...}
    # Use a more robust approach with manual parsing
    def replace_dict_syntax(match):
        content = match.group(1)
        # Convert key=value pairs to "key": value
        # Handle nested dict() recursively by processing innermost first
        parts = []
        current = []
        depth = 0
        in_string = False
        quote_char = None
        
        for i, char in enumerate(content):
            if char in ('"', "'") and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            
            if not in_string:
                if char in '({[':
                    depth += 1
                elif char in ')}]':
                    depth -= 1
                elif char == ',' and depth == 0:
                    parts.append(''.join(current).strip())
                    current = []
                    continue
            current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        converted = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Check if it's a key=value pair
            if '=' in part and not part.startswith('"') and not part.startswith("'"):
                # Find the = that's not inside parentheses or quotes
                depth = 0
                in_string = False
                quote_char = None
                eq_pos = -1
                
                for i, char in enumerate(part):
                    if char in ('"', "'") and (i == 0 or part[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                    if not in_string:
                        if char in '({[':
                            depth += 1
                        elif char in ')}]':
                            depth -= 1
                        elif char == '=' and depth == 0:
                            eq_pos = i
                            break
                
                if eq_pos > 0:
                    key = part[:eq_pos].strip()
                    value = part[eq_pos+1:].strip()
                    converted.append(f'"{key}": {value}')
                else:
                    converted.append(part)
            else:
                converted.append(part)
        
        return '{' + ', '.join(converted) + '}'
    
    # Replace dict() syntax iteratively, starting with innermost
    max_iterations = 10
    iteration = 0
    while 'dict(' in spec_str and iteration < max_iterations:
        # Match dict(...) - simpler pattern for innermost matches
        # This matches dict with content that doesn't contain dict(
        pattern = r'\bdict\s*\(([^()]+)\)'
        new_spec_str = re.sub(pattern, replace_dict_syntax, spec_str)
        if new_spec_str == spec_str:
            # No more simple replacements, try nested pattern
            pattern = r'\bdict\s*\(([^)]+)\)'
            new_spec_str = re.sub(pattern, replace_dict_syntax, spec_str)
        if new_spec_str == spec_str:
            break  # No changes made, stop iterating
        spec_str = new_spec_str
        iteration += 1
    
    # Replace unquoted Python type references with quoted strings
    # Match patterns like: "type": int, "type": str, "type": list, "type": dict, "type": bool
    # But NOT when they're already in quotes
    type_patterns = [
        (r'(\s*"type"\s*:\s*)int\b(?!["\'])', r'\1"int"'),
        (r'(\s*"type"\s*:\s*)str\b(?!["\'])', r'\1"str"'),
        (r'(\s*"type"\s*:\s*)list\b(?!["\'])', r'\1"list"'),
        (r'(\s*"type"\s*:\s*)dict\b(?!["\'])', r'\1"dict"'),
        (r'(\s*"type"\s*:\s*)bool\b(?!["\'])', r'\1"bool"'),
        (r'(\s*"type"\s*:\s*)float\b(?!["\'])', r'\1"float"'),
        # Also handle when 'type' key itself might not be quoted in some edge cases
        (r"(\s*'type'\s*:\s*)int\b(?!['\"])", r'\1"int"'),
        (r"(\s*'type'\s*:\s*)str\b(?!['\"])", r'\1"str"'),
        (r"(\s*'type'\s*:\s*)list\b(?!['\"])", r'\1"list"'),
        (r"(\s*'type'\s*:\s*)dict\b(?!['\"])", r'\1"dict"'),
        (r"(\s*'type'\s*:\s*)bool\b(?!['\"])", r'\1"bool"'),
        (r"(\s*'type'\s*:\s*)float\b(?!['\"])", r'\1"float"'),
    ]
    
    for pattern, replacement in type_patterns:
        spec_str = re.sub(pattern, replacement, spec_str)
    
    # Handle standalone type references in values (less common but possible)
    # Be careful not to replace True/False/None
    standalone_patterns = [
        (r':\s*int\s*([,}])', r': "int"\1'),
        (r':\s*str\s*([,}])', r': "str"\1'),
        (r':\s*list\s*([,}])', r': "list"\1'),
        (r':\s*dict\s*([,}])', r': "dict"\1'),
        (r':\s*bool\s*([,}])', r': "bool"\1'),
        (r':\s*float\s*([,}])', r': "float"\1'),
    ]
    
    for pattern, replacement in standalone_patterns:
        spec_str = re.sub(pattern, replacement, spec_str)
    
    # Remove trailing commas before closing braces/brackets
    # This handles cases like: }, } or ,} or ,] 
    spec_str = re.sub(r',\s*([}\]])', r'\1', spec_str)
    
    return spec_str


def compare_module_spec(module_file_path, verbose=True):
    """
    Compares the documentation spec and temp_spec within an Ansible module file.

    Args:
        module_file_path (str): The path to the Ansible module file.

    Returns:
        tuple: (filename, list of mismatch descriptions).
               Returns (filename, ["Error: ..."]) in case of errors.
    """
    filename = os.path.basename(module_file_path)
    mismatches = []
    temp_spec_lines = []
    temp_spec_found = False
    brace_count = 0
    paren_count = 0
    uses_dict_syntax = False  # Track if using dict() or {} syntax
    try:
        with open(module_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not temp_spec_found:
                    if re.match(r"\s*temp_spec\s*=", line) or re.match(r"\s*temp_spec\s*=\s*{", line) or re.match(r"\s*config_spec\s*=\s*{", line) or\
                        re.match(r"\s*validation_schema\s*=", line) or re.match(r"\s*validation_schema\s*=\s*{", line) or \
                        re.match(r"\s*lan_automation_spec\s*=", line) or re.match(r"\s*lan_automation_spec\s*=\s*{", line) or \
                        re.match(r"\s*pnp_spec\s*=\s*{", line) or re.match(r"\s*pnp_spec\s*=", line) or re.match(r"\s*self.temp_spec\s*=\s*{", line) or\
                        re.match(r"\s*rma_spec\s*=", line) or re.match(r"\s*rma_spec\s*=\s*\{", line) or re.match(r"\s*discovery_spec\s*=\s*{", line) or \
                        re.match(r"\s*device_configs_backup_spec\s*=\s*{", line) or re.match(r"\s*provision_spec\s*=\s*{", line) or \
                        re.match(r"\s*accesspoint_spec\s*=\s*{", line) or re.match(r"\s*accesspoint_spec\s*=", line):
                        temp_spec_found = True
                        first_line = line.split('=', 1)[1].strip()
                        temp_spec_lines.append(first_line)
                        
                        # Determine syntax type
                        if first_line.startswith('dict('):
                            uses_dict_syntax = True
                            paren_count += first_line.count('(') - first_line.count(')')
                        else:
                            uses_dict_syntax = False
                            brace_count += first_line.count('{') - first_line.count('}')
                elif temp_spec_found:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        temp_spec_lines.append(cleaned_line)
                        brace_count += cleaned_line.count('{')
                        brace_count -= cleaned_line.count('}')
                        paren_count += cleaned_line.count('(')
                        paren_count -= cleaned_line.count(')')
                        
                        # Check if we've reached the end based on syntax type
                        if uses_dict_syntax and paren_count == 0:
                            break
                        elif not uses_dict_syntax and brace_count == 0:
                            break

            if not temp_spec_found:
                return (filename, ["Error: Could not find temp_spec definition."])

            # Join with newlines to preserve line structure for comment removal
            temp_spec_str = "\n".join(temp_spec_lines)
            
            # Normalize the spec string before parsing
            normalized_spec_str = normalize_spec_string(temp_spec_str)
            
            try:
                temp_spec = ast.literal_eval(normalized_spec_str)
            except (SyntaxError, ValueError) as e:
                return (filename, [f"Error parsing temp_spec: {e} - Extracted string: '{temp_spec_str[:100]}...'\nNormalized: '{normalized_spec_str[:100]}...'"])
            if verbose:
                print(f"temp_spec: {temp_spec}\n")
        with open(module_file_path, 'r', encoding='utf-8') as f:
            # Extract DOCUMENTATION
            documentation_match = re.search(r"\s*DOCUMENTATION\s*=\s*r\"\"\"(.*?)\"\"\"", f.read(), re.DOTALL) # Re-read from start
            if not documentation_match:
                f.seek(0) # Reset file pointer
                documentation_match = re.search(r"DOCUMENTATION\s*=\s*r\"\"\"(.*?)\"\"\"", f, re.DOTALL)
                if not documentation_match:
                    return (filename, ["Error: Could not find DOCUMENTATION block."])

            documentation_yaml = documentation_match.group(1)
            try:
                documentation = yaml.safe_load(documentation_yaml)
            except yaml.YAMLError as e:
                return (filename, [f"Error parsing DOCUMENTATION YAML: {e}"])
            #if verbose:
            #    print(f"documentation: {documentation}\n")
        if not documentation or not isinstance(documentation, dict):
            return (filename, ["Error: Invalid DOCUMENTATION format."])
        return (filename, compare_temp_spec_with_documentation_config(temp_spec, documentation))

    except FileNotFoundError:
        return (filename, [f"Error: Module file not found."])
    except Exception as e:
        return (filename, [f"Error processing module file: {e}"])

def compare_temp_spec_with_documentation_config(temp_spec, documentation):
    """
    Compares the temp_spec with the 'config' suboptions in the Ansible module's
    DOCUMENTATION.  This function is designed to identify discrepancies between
    the data structure expected by the module (temp_spec) and the data structure
    documented for the user (in the 'config' option of DOCUMENTATION).

    Args:
        temp_spec (dict): The temp_spec dictionary, which defines the expected
                         structure of the module's input parameters.
        documentation (dict): The parsed DOCUMENTATION dictionary from the module.
                              This should be the result of parsing the YAML
                              within the DOCUMENTATION block.

    Returns:
        list: A list of mismatch descriptions.  Each mismatch is described as a
              string. An empty list is returned if no mismatches are found.
    """
    mismatches = []

    # 1. Access the 'config' option from the DOCUMENTATION
    # The 'config' option is where Ansible module documentation describes the
    # structure of the input parameters that the module expects.
    doc_config = documentation.get("options", {}).get("config")

    if not doc_config:
        return ["Error: 'config' option not found in DOCUMENTATION."]
    else:
        print(f"doc_config: {doc_config}\n")

    # 2. Basic 'config' structure check
    # The 'config' option is typically a dictionary with 'type', 'elements',
    # and 'suboptions' keys. We'll check for the 'elements' key.
    doc_config_elements = doc_config.get("elements")
    if doc_config_elements != 'dict':
        mismatches.append(
            f"Mismatch in 'config' elements type: Expected 'dict', found '{doc_config_elements}'."
        )

    # 3. Navigate to the suboptions
    # The actual parameter specifications are usually found within the
    # 'suboptions' key of the 'config' option.
    doc_config_suboptions = doc_config.get("suboptions", {})

    # 4. Iterate through the temp_spec structure
    # We'll traverse the temp_spec and compare its structure and constraints
    # with the corresponding information in the DOCUMENTATION.
    for top_level_key, top_level_spec in temp_spec.items():
        # Check if the top-level key from temp_spec exists in DOCUMENTATION
        if top_level_key not in doc_config_suboptions:
            mismatches.append(
                f"Missing top-level key '{top_level_key}' in DOCUMENTATION 'config' suboptions."
            )
            continue

        doc_suboption = doc_config_suboptions[top_level_key]

        # 5. Compare type and elements at the top level
        # Compare the 'type' of the parameter (e.g., 'list', 'dict', 'str').
        if "type" in top_level_spec and "type" in doc_suboption and top_level_spec["type"] != doc_suboption["type"]:
            mismatches.append(
                f"Type mismatch for '{top_level_key}': Expected '{top_level_spec['type']}', found '{doc_suboption['type']}'."
            )

        # If the parameter is a list, compare the type of its elements.
        if top_level_spec.get("type") == 'list':
            if (
                "elements" in top_level_spec
                and "elements" in doc_suboption
                and top_level_spec["elements"] != doc_suboption["elements"]
            ):
                mismatches.append(
                    f"Elements type mismatch for '{top_level_key}': Expected '{top_level_spec['elements']}', found '{doc_suboption['elements']}'."
                )
            elif "elements" in top_level_spec and "elements" not in doc_suboption:
                mismatches.append(
                    f"Missing 'elements' for '{top_level_key}' in DOCUMENTATION."
                )
            elif "elements" not in top_level_spec and "elements" in doc_suboption:
                mismatches.append(
                    f"Unexpected 'elements' for '{top_level_key}' in DOCUMENTATION."
                )
        # 6. Handle nested dictionaries (suboptions)
        # If the parameter is a dictionary, recursively compare its suboptions.
        elif top_level_spec.get("type") == 'dict':
            doc_sub_suboptions = doc_suboption.get("suboptions", {})
            temp_sub_spec = top_level_spec.get("suboptions", {})
            for sub_key, sub_spec in temp_sub_spec.items():
                if sub_key not in doc_sub_suboptions:
                    mismatches.append(
                        f"Missing sub-key '{sub_key}' under '{top_level_key}' in DOCUMENTATION."
                    )
                    continue

                doc_sub_suboption = doc_sub_suboptions[sub_key]
                if "type" in sub_spec and "type" in doc_sub_suboption and sub_spec["type"] != doc_sub_suboption["type"]:
                    mismatches.append(
                        f"Type mismatch for '{sub_key}' under '{top_level_key}': Expected '{sub_spec['type']}', found '{doc_sub_suboption['type']}'."
                    )
                if "choices" in sub_spec and "choices" in doc_sub_suboption and set(sub_spec["choices"]) != set(
                    doc_sub_suboption.get("choices", [])
                ):
                    mismatches.append(
                        f"Choices mismatch for '{sub_key}' under '{top_level_key}': Expected '{sub_spec['choices']}', found '{doc_sub_suboption.get('choices', [])}'."
                    )
                if sub_spec.get("required", False) and not doc_sub_suboption.get("required", False):
                    mismatches.append(
                        f"Parameter '{sub_key}' under '{top_level_key}' is required but not marked as such in documentation."
                    )
                if "elements" in sub_spec and "elements" in doc_sub_suboption and sub_spec["elements"] != doc_sub_suboption[
                    "elements"]:
                    mismatches.append(
                        f"Elements type mismatch for '{sub_key}' under '{top_level_key}': Expected '{sub_spec['elements']}', found '{doc_sub_suboption['elements']}'."
                    )
                elif "elements" in sub_spec and "elements" not in doc_sub_suboption:
                    mismatches.append(
                        f"Missing 'elements' for '{sub_key}' under '{top_level_key}' in DOCUMENTATION."
                    )
                elif "elements" not in sub_spec and "elements" in doc_sub_suboption:
                    mismatches.append(
                        f"Unexpected 'elements' for '{sub_key}' under '{top_level_key}' in DOCUMENTATION."
                    )

        # 7. Compare type, choices, and required for simple types (str, bool, int, float)
        elif "type" in top_level_spec and top_level_spec["type"] in ['str', 'bool', 'int', 'float']:
            if "type" in doc_suboption and top_level_spec["type"] != doc_suboption["type"]:
                mismatches.append(
                    f"Type mismatch for '{top_level_key}': Expected '{top_level_spec['type']}', found '{doc_suboption['type']}'."
                )
            if "choices" in top_level_spec and "choices" in doc_suboption and set(top_level_spec["choices"]) != set(
                doc_suboption.get("choices", [])
            ):
                mismatches.append(
                    f"Choices mismatch for '{top_level_key}': Expected '{top_level_spec['choices']}', found '{doc_suboption.get('choices', [])}'."
                )
            if top_level_spec.get("required", False) and not doc_suboption.get("required", False):
                mismatches.append(
                    f"Parameter '{top_level_key}' is required but not marked as such in documentation."
                )

    return mismatches

def generate_html_report(results):
    """
    Generates an HTML report from the comparison results.

    Args:
        results (list of tuples): Each tuple contains (filename, list of mismatches).

    Returns:
        str: The HTML content of the report.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ansible Module Specification Comparison Report</title>
        <style>
            body { font-family: sans-serif; }
            h2 { margin-top: 2em; }
            table { border-collapse: collapse; width: 100%; margin-top: 1em; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f0f0f0; }
            .success { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Ansible Module Specification Comparison Report</h1>
    """

    for filename, mismatches in results:
        html += f"<h2>Module: {filename}</h2>"
        if mismatches:
            html += "<table>\n"
            html += "<thead><tr><th>Mismatch Description</th></tr></thead>\n"
            html += "<tbody>\n"
            for mismatch in mismatches:
                html += f"<tr><td><span class='error'>{mismatch}</span></td></tr>\n"
            html += "</tbody>\n</table>\n"
        else:
            html += "<p><span class='success'>Success: Documentation and temp_spec match.</span></p>\n"

    html += """
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare Ansible module specs.")
    parser.add_argument("module_directory", help="Directory with module files")
    parser.add_argument("keyword", nargs='?', default="workflow_manager", help="Keyword to filter module files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    module_directory = args.module_directory
    #default keyword = "workflow_manager"
    keyword = args.keyword
    verbose = args.verbose
    if not module_directory or not keyword:
        print("Error: Both module_directory and keyword are required.")
        sys.exit(1)
    if not os.path.isdir(module_directory):
        print(f"Error: Directory not found: {module_directory}")
        sys.exit(1)
    if verbose:
        print(f"Verbose mode enabled. Module directory: {module_directory}, Keyword: {keyword}")
    results = []

    if not os.path.isdir(module_directory):
        print(f"Error: Directory not found: {module_directory}")
        sys.exit(1)

    matching_files = [
        os.path.join(module_directory, f)
        for f in os.listdir(module_directory)
        if f.endswith(".py") and keyword in f
    ]

    if not matching_files:
        print(f"No module files found in '{module_directory}' matching the keyword '{keyword}'.")
        sys.exit(0)

    print(f"Processing {len(matching_files)} module files...")
    for module_file in matching_files:
        print(f"Processing: {os.path.basename(module_file)}")
        result = compare_module_spec(module_file)
        results.append(result)

    html_report = generate_html_report(results)

    report_filename = f"spec_comparison_report_{keyword}.html"
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"\nHTML report generated: {report_filename}")
    except Exception as e:
        print(f"Error writing HTML report: {e}")
