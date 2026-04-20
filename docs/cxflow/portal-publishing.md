# Portal & Publishing

This chapter covers two modules: the **CxFlow Portal** for web-based document
viewing, and the **CxFlow Publisher** for PDF/DOCX export.

## Portal — GitBook-Style Viewer

The `lu_cxflow_portal` module provides a public-facing document portal with
clean, readable URLs.

### URL Structure

Portal URLs follow this pattern:

```
/cxflow/p/{project_slug}/{area}/{doc_slug}
```

| Component | Example | Source |
|---|---|---|
| `project_slug` | `1-erp-migration` | Auto-generated from `project.project.name` |
| `area` | `cps`, `section`, `deliverable`, `report`, `note` | Document type |
| `doc_slug` | `requirements-specification` | Auto-generated from document title |

### Visibility Rules

Portal access respects the document's `visibility` field:

| Visibility | Portal Users | Public Users |
|---|---|---|
| `internal` | No access | No access |
| `portal_customer` | Read-only | No access |
| `public` | Read-only | Read-only |

### Portal Features

- **Document tree** — left sidebar with folder-grouped navigation (JS: `tree.js`)
- **Table of contents** — auto-generated from Markdown headings (JS: `toc.js`)
- **Markdown rendering** — `html_cache` displayed with portal-specific CSS
- **Responsive layout** — works on desktop and tablet

### Change Request Portal

Issues with `issue_type=change_request` get a portal URL at `/my/cxflow/cr/{id}`,
allowing customers to review and approve CRs directly.

## Publisher — PDF / DOCX Export

The `lu_cxflow_publisher` module provides a full publishing pipeline with
configurable style profiles.

### Publish Profiles

A publish profile (`lu.cxflow.publish.profile`) defines the output styling:

| Setting | Options | Description |
|---|---|---|
| **Output format** | `pdf`, `docx`, `both` | Target format(s) |
| **Cover page** | Enable / disable | Logo, subtitle, color |
| **Header** | Enable / disable | Custom text with variables |
| **Footer** | Enable / disable | Custom text, page numbers |
| **Table of contents** | Enable / disable | Depth 1–3 |
| **Paper format** | Odoo paper format | A4, Letter, etc. |
| **Orientation** | Portrait / landscape | Page orientation |
| **Watermark** | Custom text | Auto-applies "DRAFT" if document is not approved |

Header and footer text supports template variables:

```
%(project_name)s  %(doc_name)s  %(version)s  %(date)s
```

### Publish Scopes

A publish job (`lu.cxflow.publish.job`) can target different scopes:

| Scope | Description |
|---|---|
| **Single** | One specific document |
| **Gate** | All deliverables assigned to a gate (G1 / G2 / G3) |
| **Area** | All documents of a type (CPS, deliverables, reports, or notes) |
| **Project** | All documents in the project |

### Quick Publish

Each document has one-click **Publish PDF** and **Publish DOCX** buttons that
use the `customer` profile. The generated file is attached to the document
and a download action is returned.

### Batch Publishing

For larger exports:

1. Go to **CxFlow → Publishing → Jobs**
2. Create a new job, select the profile and scope
3. Optionally filter by state (`all` or `approved` only)
4. Click **Run**

When multiple documents are exported with `both` format, the publisher creates
a ZIP bundle containing all generated files.

### Job States

```{mermaid}
stateDiagram-v2
    [*] --> draft
    draft --> running: Run
    running --> done: Success
    running --> error: Failure
    done --> draft: Reset
    error --> draft: Reset
```

Partial failures are handled — if some documents succeed and others fail, the
job moves to `done` with the successful attachments available.

### Dependencies

- **PDF**: requires `wkhtmltopdf` installed on the server
- **DOCX**: requires `python-docx` Python package
