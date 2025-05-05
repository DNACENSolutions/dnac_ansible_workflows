import yaml
import re
import ast
import os
import sys
import argparse

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
    try:
        with open(module_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not temp_spec_found:
                    if re.match(r"\s*temp_spec\s*=", line) or re.match(r"\s*temp_spec\s*=\s*{", line) or \
                        re.match(r"\s*validation_schema\s*=", line) or re.match(r"\s*validation_schema\s*=\s*{", line) or \
                        re.match(r"\s*lan_automation_spec\s*=", line) or re.match(r"\s*lan_automation_spec\s*=\s*{", line) or \
                        re.match(r"\s*pnp_spec\s*=\s*{", line) or re.match(r"\s*pnp_spec\s*=", line) or \
                        re.match(r"\s*rma_spec\s*=", line) or re.match(r"\s*rma_spec\s*=\s*\{", line) or \
                        re.match(r"\s*accesspoint_spec\s*=\s*\{", line) or re.match(r"\s*accesspoint_spec\s*=", line):
                        temp_spec_found = True
                        temp_spec_lines.append(line.split('=', 1)[1].strip())
                        brace_count += temp_spec_lines[0].count('{')
                        brace_count -= temp_spec_lines[0].count('}')
                elif temp_spec_found:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        temp_spec_lines.append(cleaned_line)
                        brace_count += cleaned_line.count('{')
                        brace_count -= cleaned_line.count('}')
                        if brace_count == 0:
                            break  # Found the end of temp_spec

            if not temp_spec_found:
                return (filename, ["Error: Could not find temp_spec definition."])

            temp_spec_str = "".join(temp_spec_lines)
            try:
                temp_spec = ast.literal_eval(temp_spec_str)
            except (SyntaxError, ValueError) as e:
                return (filename, [f"Error parsing temp_spec: {e} - Extracted string: '{temp_spec_str[:100]}...'"])
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
    parser.add_argument("keyword", help="Keyword to filter module files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    module_directory = args.module_directory
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
