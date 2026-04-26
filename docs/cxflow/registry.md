# Registry

The **CxFlow Registry** (`lu_cxflow_registry`) provides 9 structured metadata
models for project governance. It turns informal project knowledge into
traceable, auditable records.

## Registry Mixin

All registry models inherit from `lu.cxflow.registry.mixin` (abstract), which
provides:

| Field | Type | Description |
|---|---|---|
| `name` | Char | Entity name (tracked) |
| `project_id` | Many2one | Link to `project.project` (cascade delete) |
| `company_id` | Many2one | Auto-populated from project |
| `active` | Boolean | Soft-delete support |
| `description` | Text | Free-form description |

The mixin also enables `mail.thread` and `mail.activity.mixin` for all models,
so every registry entry supports comments, followers, and scheduled activities.

## Model Reference

### 1. Project (`lu.cxflow.project`)

The root metadata hub — one per Odoo project.

| Field | Type | Description |
|---|---|---|
| `code` | Char | Unique project code |
| `project_type` | Selection | `A` (SI Build), `B` (Consulting), `C` (Simple) |
| `industry` | Selection | `retail`, `manufacturing`, `service`, `it`, `other` |
| `scale` | Selection | `small` (~50), `medium` (50–200), `large` (200+) |
| `duration_weeks` | Integer | Planned duration in weeks |
| `start_date` | Date | Project start date |
| `end_date` | Date | Planned end date |
| `partner_id` | Many2one → `res.partner` | Customer account (related from `project.project`) |
| `sale_order_id` | Many2one | Sales order (related, requires `sale_project`) |
| `user_id` | Many2one | PM (related from `project.project`) |
| `team_ids` | Many2many → `res.users` | Project team members |
| `cps_id` | Many2one → `lu.cxflow.cps` | Link to the CPS document |
| `state` | Selection | `draft` → `active` → `gate1` → `gate2` → `gate3` → `closed` |
| `requirement_count` | Integer (computed) | Total requirements in this project |
| `issue_open_count` | Integer (computed) | Open issues (not resolved/closed) |
| `module_count` | Integer (computed) | Modules in scope |

```{note}
A unique constraint ensures only one `lu.cxflow.project` per `project.project`.
The `project_type` determines which WBS tasks are mandatory — see
{doc}`engine` for the WBS task library.
```

### 2. Module (`lu.cxflow.module`)

Tracks Odoo modules in scope for the project.

| Field | Type | Description |
|---|---|---|
| `technical_name` | Char | Module identifier (e.g., `sale_custom`) |
| `module_id` | Many2one → `ir.module.module` | Link to installed Odoo module |
| `responsible_id` | Many2one → `res.users` | Module owner |
| `status` | Selection | `planning` → `design` → `development` → `testing` → `deployment` → `production` |
| `sequence` | Integer | Display order |
| `requirement_ids` | One2many | Child requirements |
| `process_ids` | One2many | Child processes |

### 3. Requirement (`lu.cxflow.requirement`)

Functional and non-functional requirements with traceability.

| Field | Type | Description |
|---|---|---|
| `code` | Char | Unique code per project — format: `REQ-F-001`, `REQ-NF-001`, `REQ-D-001`, `REQ-I-001` |
| `req_type` | Selection | `functional`, `non_functional`, `data`, `integration` |
| `priority` | Selection | `low`, `medium`, `high`, `critical` |
| `module_id` | Many2one | Parent module (required) |
| `source` | Char | Origin reference (e.g., `인터뷰_04-17_홍길동`, `CPS_2.2`) |
| `state` | Selection | `draft` → `confirmed` → `rework` → `closed` |
| `testcase_ids` | One2many | Linked test cases (RTM) |
| `testcase_count` | Integer (stored) | Number of linked test cases |
| `issue_ids` | One2many | Related issues |

```{note}
The `code` field enforces the format `REQ-(F|NF|D|I)-\d{3,}` via a database
constraint. Codes must be unique within the same project.
```

### 4. Process (`lu.cxflow.process`)

Business process documentation for gap analysis.

| Field | Type | Description |
|---|---|---|
| `process_type` | Selection | `as_is`, `to_be`, `gap`, `pain_point` |
| `module_id` | Many2one | Parent module |
| `process_flow` | Text | Detailed process steps |

### 5. Integration (`lu.cxflow.integration`)

External system integration catalog.

| Field | Type | Description |
|---|---|---|
| `system_name` | Char | External system identifier |
| `api_type` | Selection | `rest`, `soap`, `rpc`, `webhook`, `file_transfer`, `database`, `other` |
| `auth_method` | Selection | `none`, `basic`, `bearer`, `api_key`, `oauth2`, `jwt` |
| `endpoint_url` | Char | API endpoint URL |

### 6. Issue (`lu.cxflow.issue`)

Issues, risks, change requests, defects, and pain points — with a CR
approval workflow.

| Field | Type | Description |
|---|---|---|
| `issue_type` | Selection | `issue`, `risk`, `cr` (Change Request), `defect`, `problem` (Pain Point) |
| `severity` | Selection | `low`, `medium`, `high`, `critical` |
| `state` | Selection | `new` → `assigned` → `in_progress` → `resolved` → `closed` |
| `approval_state` | Selection | `draft` → `pending` → `approved` / `rejected` (CRs only) |
| `approver_id` | Many2one | Internal approver |
| `partner_id` | Many2one | Customer who approves CR via portal |
| `module_id` | Many2one | Affected module |
| `requirement_id` | Many2one | Related requirement |
| `testcase_ids` | Many2many | Associated test cases |
| `resolution` | Text | Resolution details (all types) |
| `defect_step` | Text | Reproduction steps (defect only) |
| `defect_environment` | Char | Reproduction environment (defect only) |

**Change Request workflow:**

```{mermaid}
stateDiagram-v2
    [*] --> draft
    draft --> pending: Submit for Approval
    pending --> approved: Approve
    pending --> rejected: Reject (with reason)
```

### 7. Test Case (`lu.cxflow.testcase`)

Test cases mapped to requirements for the Requirements Traceability Matrix (RTM).

| Field | Type | Description |
|---|---|---|
| `scenario` | Char | Scenario label |
| `steps` | Text | Step-by-step instructions |
| `expected_result` | Text | Expected behavior |
| `actual_result` | Text | Observed result |
| `last_result` | Selection | `pass`, `fail`, `blocked` |
| `executed_date` | Date | Last execution date |
| `requirement_id` | Many2one | Parent requirement |
| `issue_ids` | Many2many | Linked issues / defects |
| `state` | Selection | `draft` → `ready` → `executed` → `closed` |

### 8. Decision (`lu.cxflow.decision`)

Audit trail of project decisions.

| Field | Type | Description |
|---|---|---|
| `decision_text` | Text | Decision details |
| `meeting_note_id` | Many2one → `lu.cxflow.note` | Meeting where the decision was made |
| `decided_date` | Date | Decision date |
| `decided_by` | Many2one → `res.users` | Decision maker |
| `state` | Selection | `active`, `superseded`, `archived` |

### 9. Project Task Extension (`project.task`)

Standard Odoo tasks are extended with CxFlow fields:

| Field | Type | Description |
|---|---|---|
| `cxflow_project_id` | Many2one | Associated CxFlow project |
| `cxflow_deliverable_ids` | Many2many | Linked deliverables |
| `cxflow_issue_ids` | Many2many | Linked issues |
| `cxflow_doc_status` | Selection (computed) | `not_applicable`, `pending`, `partially_approved`, `all_approved` |

The `cxflow_doc_status` field auto-computes from the approval state of linked
deliverables — useful for task kanban views and gate reviews.

```{warning}
Cross-project assignments are prevented by constraints. Deliverables and issues
linked to a task must belong to the same project.
```

## Menu Structure

All registry menus live under **CxFlow → Registry**:

```
CxFlow
└── Registry
    ├── Projects
    ├── Modules
    ├── Requirements
    ├── Processes
    ├── Integrations
    ├── Issues / Risks / CRs
    ├── Test Cases
    └── Decisions
```
