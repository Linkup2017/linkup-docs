# Architecture Overview

This chapter gives system integrators and technical evaluators a bird's-eye view
of CxFlow — its module layout, dependency graph, and data flow.

## Module Dependency Map

```{mermaid}
graph TD
    DOCS[lu_cxflow_docs<br/>Document Core]
    REG[lu_cxflow_registry<br/>9 Registry Models]
    ENG[lu_cxflow_engine<br/>Validation & Gates]
    GIT[lu_cxflow_git_sync<br/>Git Sync]
    PORTAL[lu_cxflow_portal<br/>Portal Viewer]
    PUB[lu_cxflow_publisher<br/>PDF / DOCX]
    PARSE[lu_cxflow_parse<br/>Source Parser]
    MCP[lu_mcp_cxflow<br/>MCP Tools]

    REG --> DOCS
    ENG --> REG
    ENG --> DOCS
    GIT --> DOCS
    PORTAL --> DOCS
    PUB --> DOCS
    PARSE --> REG
    MCP --> DOCS

    ODOO_PROJECT[project.project]
    ODOO_PORTAL[portal / website]
    MCP_SERVER[lu_mcp_server]

    DOCS --> ODOO_PROJECT
    PORTAL --> ODOO_PORTAL
    MCP --> MCP_SERVER

    classDef core fill:#4A90D9,color:#fff
    classDef ext fill:#7CB342,color:#fff
    classDef odoo fill:#888,color:#fff

    class DOCS,REG core
    class ENG,GIT,PORTAL,PUB,PARSE,MCP ext
    class ODOO_PROJECT,ODOO_PORTAL,MCP_SERVER odoo
```

**Blue** = core modules, **Green** = extension modules, **Grey** = Odoo / external dependencies.

## Layer Architecture

CxFlow follows a three-layer design:

| Layer | Modules | Responsibility |
|---|---|---|
| **Data Layer** | `lu_cxflow_docs`, `lu_cxflow_registry` | Document storage (Markdown SSOT), version snapshots, 9 registry models, cross-document references |
| **Logic Layer** | `lu_cxflow_engine`, `lu_cxflow_parse` | Template rendering (Jinja2), validation rules, gate checks, source code parsing |
| **Presentation Layer** | `lu_cxflow_portal`, `lu_cxflow_publisher`, `lu_mcp_cxflow`, `lu_cxflow_git_sync` | Portal viewer, PDF/DOCX export, MCP tool API, Git bidirectional sync |

## Document Types

CxFlow manages four document types, all sharing a common `doc_mixin`:

| Type | Model | Purpose | Workflow |
|---|---|---|---|
| **CPS** | `lu.cxflow.cps` | Context / Problem / Solution — project root document | 5-state (draft → review → approval → approved → revised) |
| **Deliverable** | `lu.cxflow.deliverable` | Template-based project deliverables (34 templates) | 5-state + gate assignment (G1 / G2 / G3) |
| **Report** | `lu.cxflow.report` | Weekly, gate check, custom reports | 2-state (draft → approved) |
| **Note** | `lu.cxflow.note` | Meeting, interview, reference, freeform notes | 2-state (draft → archived) |

## Doc Mixin — Shared Foundation

All document types inherit from `lu.cxflow.doc.mixin`, which provides:

- **Markdown SSOT** — `md_source` stores raw Markdown; `html_cache` is computed on-the-fly
- **Optimistic Locking** — `version` counter prevents concurrent edit conflicts
- **Workflow State Machine** — configurable transition policy with group/author checks
- **Visibility Control** — `internal` / `portal_customer` / `public` scopes
- **Version Snapshots** — immutable history with restore and pin capabilities
- **Cross-Document References** — `[[cps:123]]` syntax tracked in `lu.cxflow.doc.reference`
- **Tagging** — `lu.cxflow.doc.tag` for flexible categorization

## 9 Registry Models

The `lu_cxflow_registry` module provides structured metadata via `registry_mixin`:

| # | Model | Purpose |
|---|---|---|
| 1 | `lu.cxflow.project` | Project metadata hub — links to `project.project` |
| 2 | `lu.cxflow.module` | Odoo modules in scope (planning → production) |
| 3 | `lu.cxflow.requirement` | Functional / non-functional / data / integration requirements |
| 4 | `lu.cxflow.process` | As-is / to-be / gap / pain-point analysis |
| 5 | `lu.cxflow.integration` | External system integration catalog |
| 6 | `lu.cxflow.issue` | Issues, risks, change requests, defects |
| 7 | `lu.cxflow.testcase` | Test cases linked to requirements (RTM) |
| 8 | `lu.cxflow.decision` | Decision log with meeting note references |
| 9 | `project.task` (ext) | Extended with CxFlow deliverable / issue links |

## Data Flow

```{mermaid}
sequenceDiagram
    participant User
    participant Workspace as CxFlow Workspace
    participant DocMixin as Doc Mixin
    participant Engine as Engine
    participant Git as Git Sync
    participant Portal as Portal
    participant MCP as MCP Tools

    User->>Workspace: Create / edit document
    Workspace->>DocMixin: Save md_source
    DocMixin->>DocMixin: Bump version, render html_cache
    DocMixin->>DocMixin: Create version snapshot
    DocMixin->>DocMixin: Upsert cross-references

    Engine->>DocMixin: Render from template (Jinja2)
    Engine->>Engine: Run validation rules
    Engine->>Engine: Gate check (G1 → G2 → G3)

    DocMixin->>Git: Auto-push on save
    Git->>DocMixin: Cron auto-pull

    User->>Portal: View approved documents
    Portal->>DocMixin: Read html_cache (visibility filtered)

    MCP->>DocMixin: AI agent CRUD operations
```

## Access Control

CxFlow uses two user groups:

| Group | Inherits | Capabilities |
|---|---|---|
| **CxFlow User** | `project.group_project_user` | Create, read, update documents; submit for review |
| **CxFlow Manager** | CxFlow User | Approve, reject, revise; manage tags; delete documents |

Record rules enforce:

- **Internal users** see only documents in projects they manage or follow
- **Portal users** see only `portal_customer` or `public` visibility documents (read-only)
- **Public users** see only `public` visibility documents (read-only)

## Technology Stack

| Component | Technology |
|---|---|
| Markdown parsing | `markdown-it-py` |
| HTML sanitization | `bleach` |
| Template rendering | Jinja2 (sandboxed) |
| Markdown editor | CodeMirror 6 |
| PDF generation | wkhtmltopdf |
| DOCX generation | python-docx |
| Git integration | PyYAML + git CLI |
