# MCP Integration

The **Linkup MCP — CxFlow** (`lu_mcp_cxflow`) module exposes 12 MCP tools for
AI-assisted document management. It follows the **Markdown SSOT** principle —
zero HTML↔MD conversion since `md_source` is already Markdown.

## Prerequisites

- `lu_mcp_server` module installed and configured
- `lu_cxflow_docs` module installed
- Optional: `lu_cxflow_engine` for template rendering and gate tools

## Tool Reference

### Document CRUD

#### `cxflow/list_projects`

Lists all projects that have CxFlow documents, with per-model document counts.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `limit` | Integer | No | 50 |

#### `cxflow/list_docs`

Lists documents by kind, project, and state.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `doc_kind` | String | Yes | — |
| `project_id` | Integer | Yes | — |
| `state` | String | No | all |
| `limit` | Integer | No | 50 |

**doc_kind values**: `cps`, `section`, `deliverable`, `report`, `note`

#### `cxflow/read_doc`

Reads a single document — returns metadata header + raw Markdown body.

| Parameter | Type | Required |
|---|---|---|
| `doc_kind` | String | Yes |
| `doc_id` | Integer | Yes |

Response format:

```markdown
**Requirements Specification** (id=42)
Kind: deliverable | State: draft | Version: 3
Project: ERP Migration (id=1)
Template: AN01 | Gate: G1

---

## 1. Introduction

This document describes the functional requirements...
```

#### `cxflow/create_doc`

Creates a new document with kind-specific fields.

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `doc_kind` | String | Yes | |
| `project_id` | Integer | Yes | |
| `name` | String | Yes | |
| `md_source` | String | No | Initial Markdown content |
| `template_code` | String | No | Deliverables only |
| `gate_no` | String | No | Deliverables only |
| `report_type` | String | No | Reports only |
| `note_type` | String | No | Notes only |

#### `cxflow/update_doc`

Updates a document with optimistic locking.

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `doc_kind` | String | Yes | |
| `doc_id` | Integer | Yes | |
| `name` | String | No | |
| `md_source` | String | No | |
| `expected_version` | Integer | No | Prevents race conditions |

```{tip}
Always pass `expected_version` when updating `md_source` to detect concurrent
edits. If the version has changed since you last read the document, the update
will fail with a conflict error.
```

#### `cxflow/create_note`

Shortcut for creating notes with participant matching.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `project_id` | Integer | Yes | — |
| `name` | String | Yes | — |
| `note_type` | String | No | `meeting` |
| `md_source` | String | No | — |
| `meeting_date` | String | No | — |
| `participant_names` | List | No | Fuzzy-matched to `res.partner` |
| `external_url` | String | No | — |

### Search & Navigation

#### `cxflow/search_docs`

Searches across all 5 document models by name and content.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `query` | String | Yes | — |
| `project_id` | Integer | No | all projects |
| `limit` | Integer | No | 20 |

#### `cxflow/get_doc_tree`

Returns the full workspace tree for a project — CPS hierarchy + folder-grouped
areas.

| Parameter | Type | Required |
|---|---|---|
| `project_id` | Integer | Yes |

### Cross-References

#### `cxflow/link_docs`

Creates a cross-document reference in `lu.cxflow.doc.reference`.

| Parameter | Type | Required | Default |
|---|---|---|---|
| `source_kind` | String | Yes | — |
| `source_id` | Integer | Yes | — |
| `target_kind` | String | Yes | — |
| `target_id` | Integer | Yes | — |
| `ref_type` | String | No | `related_doc` |

**ref_type values**: `inline_link`, `related_doc`, `cited`, `attachment`

### Engine Tools (Conditional)

These tools are only available when `lu_cxflow_engine` is installed.

#### `cxflow/render_from_template`

Renders a deliverable from its Jinja2 template, respecting the auto_level
setting.

#### `cxflow/advance_gate`

Triggers a gate check, pass, or override for a project gate (G1/G2/G3).

#### `cxflow/aggregate_summary`

Regenerates a deliverable's summary section from aggregated project data.

## Response Format

All tools return **Markdown strings** (not JSON). This makes responses directly
readable by both humans and AI agents.

- **Metadata header**: document name, ID, state, version, project info
- **Separator**: `---` between metadata and content
- **Tables**: used for list and search results

## AI Agent Workflow Example

A typical AI agent session using CxFlow MCP tools:

```
1. cxflow/list_projects              → Find the target project
2. cxflow/get_doc_tree               → Understand document structure
3. cxflow/read_doc (kind=cps)        → Read project context
4. cxflow/create_doc (kind=note)     → Create meeting notes
5. cxflow/search_docs                → Find related deliverables
6. cxflow/update_doc                 → Update a deliverable with new content
7. cxflow/link_docs                  → Link the note to the deliverable
```
