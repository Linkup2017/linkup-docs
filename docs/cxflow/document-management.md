# Document Management

This chapter covers the four document types, the shared doc mixin, versioning,
cross-document references, and tagging.

## Document Types at a Glance

| Type | Model | One-per-project? | Workflow | Use Case |
|---|---|---|---|---|
| **CPS** | `lu.cxflow.cps` | Yes | 5-state | Project root — Context / Problem / Solution |
| **CPS Section** | `lu.cxflow.cps.section` | No (hierarchical) | 5-state | Nested sections under CPS |
| **Deliverable** | `lu.cxflow.deliverable` | No | 5-state + gate | Template-based project documents |
| **Report** | `lu.cxflow.report` | No | 2-state | Weekly, gate check, custom reports |
| **Note** | `lu.cxflow.note` | No | 2-state | Meeting, interview, reference, freeform |

## CPS — Context / Problem / Solution

The CPS is the root document for a project. Each project has exactly one CPS.

### CPS Sections

Sections form a hierarchy with `parent_id` and `parent_path`. Each section has:

- **section_type** — `context`, `problem`, or `solution`
- **sequence** — drag to reorder within a parent
- **child_ids** — nested sub-sections

Sections support recursive serialization to Markdown via `action_serialize_to_md()`,
which produces a depth-based heading structure.

## Deliverables

Deliverables are template-based documents tied to project gates:

- **template_code** — unique identifier per project (e.g., `PM01`, `AN03`)
- **gate_no** — `G1` (Analysis), `G2` (Design), `G3` (Go-Live)
- **auto_level** — controls how templates fill content:
  - `A` — Fully automatic (replace all content)
  - `B` — Marker blocks only (selective replacement)
  - `C` — Manual (no auto-fill)

```{tip}
The engine module (`lu_cxflow_engine`) provides 34 pre-built templates across
8 project phases. See {doc}`engine` for details.
```

## Reports

Reports track project progress with three types:

| Type | Purpose |
|---|---|
| `weekly` | Weekly status updates |
| `gate_check` | Gate review results (linked to G1 / G2 / G3) |
| `custom` | Free-form reports |

Reports use a simplified 2-state workflow: **Draft → Approved**. A CxFlow User
can directly approve their own reports (the author restriction is relaxed).

Key fields:

- **period_start** / **period_end** — reporting period
- **auto_generated** — flag for system-generated reports

## Notes

Notes capture informal knowledge with four types:

| Type | Purpose |
|---|---|
| `meeting` | Meeting minutes with date and participants |
| `interview` | Stakeholder interview records |
| `reference` | External reference material |
| `freeform` | Anything else |

Notes use a 2-state workflow: **Draft → Archived**. Both transitions allow the
author.

Key fields:

- **meeting_date** — date of the event
- **participant_ids** — linked `res.partner` records
- **external_url** — link to external resources

## Doc Mixin — Common Features

All document types inherit from `lu.cxflow.doc.mixin`, which provides:

### Markdown as SSOT

The `md_source` field stores raw Markdown. The `html_cache` field is computed
on-the-fly using `markdown-it-py` and sanitized with `bleach`. You never store
or edit HTML.

### Slug Generation

Each document gets a URL-safe `slug` generated from the title after creation.
Slugs are unique per model and used for portal URLs.

### Workflow State Machine

The mixin defines a configurable transition policy:

```
Draft → Review        (CxFlow User, allow author)
Review → Approval     (CxFlow User, not author, creates activity)
Approval → Approved   (CxFlow Manager, not author)
Review → Draft        (CxFlow User, not author — rejection)
Approval → Draft      (CxFlow User, not author — rejection)
Approved → Revised    (CxFlow Manager, not author)
Revised → Review      (CxFlow User, allow author)
```

```{note}
Reports and Notes override this with simplified 2-state policies.
```

### Visibility Control

Each document has a `visibility` field:

| Value | Who Can See |
|---|---|
| `internal` | CxFlow Users and Managers only |
| `portal_customer` | Internal users + portal customers of the project |
| `public` | Everyone, including unauthenticated users |

```{warning}
Public documents must be in `approved` state. The system enforces this with a
constraint.
```

## Version Snapshots

Every time `md_source` is saved, the version counter increments and a snapshot
is created. Each snapshot stores:

- **md_source_snapshot** — immutable copy of the content
- **version_number** — sequential counter
- **name** / **state** — document metadata at the time of snapshot
- **is_pinned** — pinned versions are never auto-archived

### Restoring a Version

Click the version count badge → select a version → **Restore**. This writes
the snapshot's Markdown back to `md_source` and bumps the version counter
(optimistic lock aware).

### Automatic Cleanup

A daily cron job archives old versions beyond the configured limit:

- **Config parameter**: `lu_cxflow_docs.max_versions_per_doc` (default: `50`)
- Pinned versions are always kept
- Versions older than 6 months are eligible for deletion

## Cross-Document References

Use the `[[type:id]]` syntax to create inline references between documents:

```markdown
See [[cps:1]] for project context.
This deliverable addresses [[deliverable:42]].
```

Supported types: `cps`, `cps.section`, `deliverable`, `report`, `note`.

References are tracked in `lu.cxflow.doc.reference` with:

- **ref_type** — `inline_link`, `related_doc`, `cited`, `attachment`
- Back-references are computed so each document shows what links to it

## Tagging

`lu.cxflow.doc.tag` provides colored tags shared across all document types.
Tags are managed under **CxFlow → Configuration → Tags** (CxFlow Manager only).

Each document type uses its own Many2many relation table for tag assignment.

## Menu Structure

```
CxFlow
├── Workspace (3-panel editor)
├── Documents
│   ├── CPS
│   ├── Deliverables
│   ├── Reports
│   └── Notes
└── Configuration
    └── Tags (Manager only)
```
