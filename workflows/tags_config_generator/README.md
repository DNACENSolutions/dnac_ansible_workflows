# Tags Config Generator

## Overview

This workflow exports existing Catalyst Center tags and tag memberships into YAML compatible with `cisco.catalystcenter.tags_workflow_manager`, using the upstream `cisco.catalystcenter.tags_playbook_config_generator` module.

## Workflow Structure

```text
tags_config_generator/
├── playbook/tags_config_generator.yml
├── schema/tags_config_generator_schema.yml
├── vars/tags_config_generator_input.yml
└── README.md
```

## Supported Inputs

Each `tags_config` list item supports:

- `file_path`
- `file_mode`
- `config.component_specific_filters`
- legacy `generate_all_configurations`
- legacy top-level `component_specific_filters`

When `config` is omitted, the workflow runs in full discovery mode and exports all supported tag components. If `config` is provided, it must contain `component_specific_filters`.

Supported components:

- `tag`
- `tag_memberships`

Supported membership identifiers:

- `hostname`
- `serial_number`
- `mac_address`
- `ip_address`

## Validate

```bash
./tools/schemavalidation.sh -s workflows/tags_config_generator/schema/tags_config_generator_schema.yml \
  -d workflows/tags_config_generator/vars/tags_config_generator_input.yml
```

## Execute

```bash
ansible-playbook -i inventory/demo_lab/hosts.yaml \
  workflows/tags_config_generator/playbook/tags_config_generator.yml \
  --extra-vars VARS_FILE_PATH=./workflows/tags_config_generator/vars/tags_config_generator_input.yml
```

## Examples

Generate all tags and memberships:

```yaml
tags_config:
  - file_path: "generated_file/complete_tags_config.yml"
```

Generate only tag definitions:

```yaml
tags_config:
  - file_path: "generated_file/tag_definitions.yml"
    config:
      component_specific_filters:
        components_list: ["tag"]
```

Generate memberships for one tag using hostnames:

```yaml
tags_config:
  - file_path: "generated_file/tag_memberships_hostname.yml"
    config:
      component_specific_filters:
        components_list: ["tag_memberships"]
        tag_memberships:
          - tag_name: "Core-Routers"
            device_identifier: "hostname"
```
