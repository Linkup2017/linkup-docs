# Engine — Validation & Gates

The **CxFlow Engine** (`lu_cxflow_engine`) adds template-based document
generation, validation rules, and a three-tier gate system to CxFlow.

## Templates

CxFlow ships with **34 deliverable templates** organized across 8 project
categories:

| Category Code | Label | Examples |
|---|---|---|
| `pm` | Project Management | Project Charter, WBS, Weekly Report |
| `rd` | Requirements Definition | Requirements Spec, Scope Statement |
| `an` | Analysis | As-Is Process, Gap Analysis, Fit-Gap |
| `ds` | Design | To-Be Process, Data Migration Plan |
| `dv` | Development | Customization Spec, Integration Spec |
| `ts` | Testing | Test Plan, Test Cases, Test Report |
| `qa` | Quality Assurance | QA Checklist, Review Report |
| `op` | Operations Transfer | Deployment Plan, Go-Live Checklist, Lessons Learned |

### Template Structure

Each template (`lu.cxflow.template`) contains:

| Field | Type | Description |
|---|---|---|
| `code` | Char | Unique template code (e.g., `RD01`) |
| `name` | Char | Template display name |
| `category` | Selection | One of 8 category codes (`pm/rd/an/ds/dv/ts/qa/op`) |
| `gate_no` | Selection | Gate association: `none`, `g1`, `g2`, `g3` |
| `auto_level` | Selection | Automation level: `a` (full), `b` (marker blocks), `c` (manual) |
| `jinja_source` | Text | Jinja2 template for Markdown generation (added by engine) |
| `auto_prompt` | Text | LLM prompt for auto-fill context (added by engine) |
| `wbs_task_ids` | Many2many | Linked WBS tasks |

### Rendering

Templates use **Jinja2 sandboxed rendering** with a rich context:

```python
context = {
    'project': ...,        # lu.cxflow.project record
    'modules': [...],      # lu.cxflow.module records
    'requirements': [...], # lu.cxflow.requirement records
    'testcases': [...],    # lu.cxflow.testcase records
    'issues': [...],       # lu.cxflow.issue records
    'processes': [...],    # lu.cxflow.process records
    'integrations': [...], # lu.cxflow.integration records
    'decisions': [...],    # lu.cxflow.decision records
    'cps': ...,            # lu.cxflow.cps record
}
```

Rendering respects the deliverable's `auto_level`:

- **A (Fully Auto)** — replaces entire `md_source`
- **B (Marker Blocks)** — replaces only `<!-- AUTO:START -->...<!-- AUTO:END -->` blocks
- **C (Manual)** — no automatic changes

## Validation Rules

The engine defines **11 validation rules** that check project completeness:

| Rule | Check | Description |
|---|---|---|
| R01 | Structure | All modules have at least one requirement |
| R02 | Completeness | All required templates have deliverables |
| R03 | Templates | Deliverable template codes match known templates |
| R04 | CPS | CPS document exists and is approved |
| R05 | G1 Dependencies | G1 prerequisites are met before G2 |
| R06 | G2 Dependencies | G2 prerequisites are met before G3 |
| R07 | Gate Chain | Prerequisite gates are passed |
| R08 | Coverage | Requirements have linked test cases |
| R09 | Processes | Modules have process documentation |
| R10 | Integrations | Integration entries have endpoint details |
| R11 | Markers | AUTO marker pairs in deliverables are consistent |

Validation results are stored in `lu.cxflow.validation.result`:

| Field | Type | Description |
|---|---|---|
| `rule_code` | Char | Rule identifier (R01–R11) |
| `rule_name` | Char | Human-readable rule name |
| `checkpoint` | Selection | When triggered: `creation`, `confirmation`, `gate`, `weekly`, `manual` |
| `status` | Selection | `pass`, `fail`, `warning` |
| `severity` | Selection | `info`, `warning`, `critical` |
| `message` | Text | Human-readable result |
| `detail_json` | Json | Structured evidence for debugging |
| `project_id` | Many2one | Checked project |
| `ai_diagnosis` | Text | LLM-produced failure diagnosis (async, v5.3.0+) |
| `ai_diagnosis_status` | Selection | `pending` → `queued` → `done` / `failed` / `timeout` / `skipped` |

```{tip}
Failed validation results can be diagnosed by AI. In the Validation Results list,
click **Diagnose Now** (requires CxFlow Manager privilege) to enqueue an LLM
diagnosis run. Diagnosis text is auto-cleared after `cxflow.ai_diagnosis_retention_days`
(default 180 days) to control database size.
```

## Gate System

CxFlow uses a three-tier gate review process:

```{mermaid}
graph LR
    G1[G1 — Analysis Gate] --> G2[G2 — Design Gate]
    G2 --> G3[G3 — Go-Live Gate]
```

### Gate Status (`lu.cxflow.gate.status`)

| Field | Type | Description |
|---|---|---|
| `project_id` | Many2one | `project.project` |
| `cxflow_project_id` | Many2one | `lu.cxflow.project` |
| `gate_no` | Selection | `g1`, `g2`, `g3` |
| `state` | Selection | `not_ready` → `ready` → `passed` / `overridden` |
| `blocking_count` | Integer | Number of blocking deliverables (computed) |
| `blocking_detail` | Text | List of blocking items (computed) |
| `passed_date` | Datetime | When the gate was passed |
| `passed_by` | Many2one | User who passed the gate |
| `milestone_id` | Many2one | Linked `project.milestone` |
| `deadline` | Date | Gate deadline (read/write via milestone) |

Gate status records are **auto-created** when a `lu.cxflow.project` is first
created via `_cxflow_seed_gate_status()`.

### Gate Check Process

State transitions for a gate:

```{mermaid}
stateDiagram-v2
    [*] --> not_ready
    not_ready --> ready: all linked deliverables approved
    ready --> passed: action_pass_gate (Manager)
    ready --> overridden: action_force_override (Manager)
```

1. **not_ready** — one or more linked deliverables are not yet approved
2. **ready** — all linked deliverables approved; gate can be passed
3. **passed** — explicitly passed by a CxFlow Manager
4. **overridden** — forced past by a Manager with justification

```{tip}
Deliverables hook into the gate system via `_hook_gate_check_on_approve()`.
When a deliverable is approved, the engine automatically re-evaluates the
blocking count for the gate it belongs to.
```

## Deliverable Split Plan

When a deliverable grows beyond **600 lines** (configurable via
`cxflow.split_plan_threshold`), the AI can suggest splitting it into smaller
child deliverables. This feature is managed through `lu.cxflow.deliverable.split.plan`.

### Split Plan Workflow

```{mermaid}
stateDiagram-v2
    [*] --> suggested: LLM generates plan
    suggested --> approved: Manager approves
    suggested --> rejected: Manager rejects
    approved --> applied: Apply (feature-flagged)
    applied --> approved: Unapply (within window)
```

### Split Plan Fields

| Field | Type | Description |
|---|---|---|
| `deliverable_id` | Many2one | Source deliverable |
| `state` | Selection | `suggested` → `approved` → `applied` / `rejected` |
| `plan_json` | Text | LLM output — array of `{section_title, line_start, line_end, reason}` |
| `summary` | Text | Human-readable rationale |
| `line_count` | Integer | Source line count at suggestion time |
| `source_md_hash` | Char | SHA-256 of `md_source` at generation time (drift check) |
| `pre_apply_version_id` | Many2one | Version snapshot taken just before apply (for unapply) |
| `child_deliverable_ids` | One2many | Child deliverables created by apply |

### Applying a Split Plan

Applying a plan requires:

1. The `CxFlow Split Plan Apply` security group (`group_cxflow_split_plan_apply`)
2. The system parameter `cxflow.enable_split_plan_apply = True`

The apply operation runs atomically:

1. Acquires a **PostgreSQL advisory lock** on the parent deliverable ID
2. Runs **5 pre-flight checks** inside the lock:
   - Parent must be active
   - Plan must be in `approved` state
   - `md_source` hash must match (no drift since plan generation)
   - Section line ranges must be within source and non-overlapping
   - Referenced `target_template_code` values must still exist
3. Captures a **version snapshot** of the parent (stored in `pre_apply_version_id`)
4. Creates **child deliverables** with code `{parent_code}_s{n}`
5. Shrinks parent to a **facade TOC** containing `<!-- CXFLOW:FACADE -->` marker
6. Marks parent state as `applied`

### Unapplying a Split Plan

```{warning}
Unapply is only available within the window configured by
`cxflow.unapply_window_days` (default **2 days**). After the window closes,
restore manually via version history.
```

Unapply restores the parent `md_source` from `pre_apply_version_id` and
archives all child deliverables (soft-delete, `active=False`). The parent
reverts to `approved` state so a re-apply is possible.

## WBS Mapping

### WBS Task Library (`lu.cxflow.wbs.task`)

CxFlow ships with a master library of **58 WBS tasks** that define the
standard project structure across all project types (A / B / C).

| Field | Type | Description |
|---|---|---|
| `wbs_number` | Integer | WBS sequence number |
| `phase` | Char | Project phase label |
| `task_name` | Char | Task name |
| `default_deliverable` | Char | Default deliverable name |
| `default_md` | Float | Estimated man-days |
| `apply_type_a` | Selection | SI Build (Type A): `mandatory`, `optional`, `conditional`, `excluded` |
| `apply_type_b` | Selection | Consulting (Type B): same options |
| `apply_type_c` | Selection | Simple (Type C): same options |
| `is_gate` | Boolean | Whether this task is a gate review task |
| `gate_number` | Integer | 1 = BPA, 2 = UAT, 3 = Closure |

Call `get_applicable_tasks(project_type)` to retrieve all mandatory and
optional tasks for a given project type (`'A'`, `'B'`, or `'C'`).

Templates link back to WBS tasks via the `wbs_task_ids` Many2many field,
creating a template → WBS task traceability matrix.

## Automation

### Cascade Rules (5)

When registry data changes, the engine can auto-regenerate affected deliverables:

| Trigger | Effect |
|---|---|
| Requirement created / updated | Re-render affected deliverables (auto_level A/B) |
| Test case created / updated | Re-render test-related deliverables |
| Issue created / updated | Re-render issue-related deliverables |
| CPS section updated | Re-render CPS-dependent deliverables |
| Test case fails | Auto-create defect issue |

### Cron Jobs

| Cron | Schedule | Purpose |
|---|---|---|
| Weekly validation | Weekly | Run all 11 validation rules on active projects |
| Weekly report generation | Weekly | Auto-generate weekly status report |
| Validation result GC | Daily | Clean up results older than `cxflow.validation_result_retention_days` (default 180 days) |
| AI diagnosis GC | Daily | Null out diagnosis text older than `cxflow.ai_diagnosis_retention_days` (default 180 days) |
| Split plan GC | Weekly | Null out `plan_json` on terminal-state plans older than `cxflow.split_plan_retention_days` (default 180 days) |

## RTM Gap Analysis

The engine extends `project.project` with an AI-assisted Requirements
Traceability Matrix (RTM) analysis:

| Field | Type | Description |
|---|---|---|
| `cxflow_rtm_gap_count` | Integer (computed) | Number of requirements with no linked test cases |
| `cxflow_rtm_coverage_pct` | Float (computed) | Percentage of requirements with at least one test case |

Click **Analyze RTM** on the project form to trigger an AI workflow
(`lu.cxflow.rtm.workflow`) that scans requirement↔test case coverage and
produces a gap report. Requires:

- `lu_ai_workflow` to be installed
- CxFlow Manager privilege

## Menu Structure

Engine features are integrated into the existing CxFlow menu:

```
CxFlow
└── Engine
    ├── Templates
    ├── WBS Tasks
    ├── Validation Results
    ├── Gate Status
    └── Split Plans
```
