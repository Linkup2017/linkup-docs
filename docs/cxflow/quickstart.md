# Quick Start

Get CxFlow up and running in your Odoo 19.0 instance — from installation to
your first document in under 10 minutes.

## Prerequisites

- Odoo 19.0 Enterprise with **Project** app installed
- Python packages: `markdown-it-py`, `bleach`
- Admin access to install modules

## Step 1 — Install the Base Module

Install **Linkup CxFlow Docs** (`lu_cxflow_docs`) from the Apps menu.

```
Apps → Search "CxFlow" → Install "Linkup CxFlow Docs"
```

This creates the **CxFlow** top-level menu with:

- **Workspace** — 3-panel document editor
- **Documents** — CPS, Deliverables, Reports, Notes
- **Configuration** — Tags (manager only)

```{tip}
Install `lu_cxflow_registry` next if you need structured metadata (requirements,
processes, test cases). The other modules can be added later as needed.
```

## Step 2 — Create a Project

CxFlow documents are scoped to Odoo projects. Create or select an existing
project:

```
Project → Create → Enter project name → Save
```

## Step 3 — Open the Workspace

Navigate to **CxFlow → Workspace** and select your project. The workspace
provides a 3-panel layout:

| Panel | Purpose |
|---|---|
| **Left** — Doc Tree | Browse CPS, deliverables, reports, notes in a folder structure |
| **Center** — Editor | Markdown editor (CodeMirror 6) with live preview |
| **Right** — TOC & Meta | Table of contents, tags, version info, workflow buttons |

## Step 4 — Create a CPS Document

The CPS (Context / Problem / Solution) is the root document for your project.
Only one CPS per project is allowed.

1. In the Workspace, click **+ New CPS**
2. Enter a title (e.g., "ERP Migration Project")
3. Write your project context in Markdown:

```markdown
## Context

The customer currently runs SAP ECC 6.0 and wants to migrate to Odoo 19.0.

## Problem

- Manual data entry across 5 disconnected systems
- No real-time inventory visibility
- Reporting takes 3+ business days

## Solution

Deploy Odoo 19.0 with CRM, Sales, Inventory, and Accounting modules.
Integrate with the existing WMS via REST API.
```

4. Click **Save**

```{note}
CxFlow stores Markdown as the single source of truth (`md_source`). The HTML
preview is computed on-the-fly — you never edit HTML directly.
```

## Step 5 — Add Sections

CPS supports hierarchical sections with type annotations:

1. Click **+ Section** under your CPS
2. Set **Section Type** to `context`, `problem`, or `solution`
3. Write the section content in Markdown
4. Drag sections to reorder using the sequence handle

## Step 6 — Submit for Review

When your CPS is ready:

1. Click **Submit for Review** in the header
2. A reviewer (another CxFlow User) reviews and clicks **Request Approval**
3. A CxFlow Manager clicks **Approve**

```{tip}
The full workflow is: **Draft → Review → Approval → Approved**.
Reports use a simpler 2-state flow (Draft → Approved), and Notes use
Draft → Archived.
```

## What's Next?

| Goal | Chapter |
|---|---|
| Learn all document types and versioning | {doc}`document-management` |
| Set up structured metadata (requirements, test cases) | {doc}`registry` |
| Use templates and gate reviews | {doc}`engine` |
| Publish documents as PDF / DOCX | {doc}`portal-publishing` |
| Sync documents with Git | {doc}`git-sync` |
| Connect AI agents via MCP | {doc}`mcp-integration` |

## Recommended Install Order

```{mermaid}
graph LR
    A[lu_cxflow_docs] --> B[lu_cxflow_registry]
    B --> C[lu_cxflow_engine]
    A --> D[lu_cxflow_portal]
    A --> E[lu_cxflow_publisher]
    A --> F[lu_cxflow_git_sync]
    B --> G[lu_cxflow_parse]
    A --> H[lu_mcp_cxflow]
```

Install `lu_cxflow_docs` first, then add modules as your needs grow.
