# Source Parser

The **CxFlow Source Parser** (`lu_cxflow_parse`) scans Odoo module source code
and auto-populates the CxFlow registry with extracted metadata.

## Overview

The parser reads Odoo addon directories and extracts:

- **Manifests** — module name, version, dependencies, description
- **Models** — model names, fields, field types
- **Views** — XML view definitions and types
- **Security** — groups, ACL rules, record rules

Extracted data is stored as **parse artifacts** and optionally synced to the
CxFlow registry.

## Running a Parse Job

Navigate to **CxFlow → Parser → Jobs** and create a new job.

### Job Configuration

| Field | Description | Required |
|---|---|---|
| **Source Path** | Absolute path to addon directory on the server | Yes |
| **Module Filter** | Comma-separated module names (blank = all) | No |
| **Populate Registry** | Auto-sync parsed data to CxFlow registry | No (default: Yes) |

### Path Validation

The parser validates the source path for security:

- Must be an absolute path
- No `..` directory traversal allowed
- Must be an existing directory
- Must contain at least one `__manifest__.py` in immediate subdirectories

### Running

Click **Run Parse** to start. The job transitions through:

```{mermaid}
stateDiagram-v2
    [*] --> draft
    draft --> running: Run Parse
    running --> done: Success
    running --> error: Failure
    done --> draft: Reset
    error --> draft: Reset
```

```{note}
Only one parse job can run per project at a time. Concurrent runs are blocked.
```

## Parse Artifacts

Each discovered item is stored as a `lu.cxflow.parse.artifact`:

| Field | Description |
|---|---|
| `module_name` | Source module name |
| `artifact_type` | `manifest`, `model`, `view`, `security_group`, `security_acl`, `security_rule` |
| `file_path` | Source file location |
| `content_json` | Structured parsed data (JSON) |
| `line_count` | Lines in source file |
| `parse_warnings` | Any warnings during parsing |

## Registry Population

When `populate_registry` is enabled, the parser syncs extracted data to:

- **`lu.cxflow.module`** — creates or updates module entries with:
  - `last_parsed_at` — timestamp
  - `parsed_model_count` — number of models found
  - `parsed_field_count` — number of fields found
  - `parsed_view_count` — number of views found
  - `parsed_depends` — comma-separated dependency list

This connects the source code reality to the registry's project metadata,
ensuring documentation stays aligned with the actual codebase.

## Use Cases

| Scenario | How |
|---|---|
| **Initial project setup** | Parse the addon directory to auto-create module entries in the registry |
| **Post-development audit** | Re-parse to verify all models and views are documented |
| **Documentation generation** | Use parsed artifacts as input for template rendering in the engine |

## Dependencies

No external dependencies — the parser uses pure Python AST and XML parsing.
