# Engine — Validation & Gates

The **CxFlow Engine** (`lu_cxflow_engine`) adds template-based document
generation, validation rules, and a three-tier gate system to CxFlow.

## Templates

CxFlow ships with **34 deliverable templates** organized across 8 project
phases:

| Phase | Code Prefix | Examples |
|---|---|---|
| Project Management | `PM` | PM01 Project Charter, PM02 WBS, PM04 Weekly Report |
| Analysis | `AN` | AN01 Requirements Spec, AN02 As-Is Process, AN03 Gap Analysis |
| Design | `DS` | DS01 To-Be Process, DS02 Data Migration Plan |
| Development | `DV` | DV01 Customization Spec, DV02 Integration Spec |
| Testing | `TS` | TS01 Test Plan, TS02 Test Cases, TS03 Test Report |
| Training | `TR` | TR01 Training Plan, TR02 Training Material |
| Deployment | `DP` | DP01 Deployment Plan, DP02 Go-Live Checklist |
| Closure | `CL` | CL01 Closure Report, CL02 Lessons Learned |

### Template Structure

Each template (`lu.cxflow.template`) contains:

| Field | Type | Description |
|---|---|---|
| `code` | Char | Unique template code (e.g., `AN01`) |
| `name` | Char | Template display name |
| `gate_no` | Selection | Required gate: G1, G2, or G3 |
| `phase` | Char | Project phase |
| `jinja_source` | Text | Jinja2 template for Markdown generation |
| `default_auto_level` | Selection | Default automation level (A / B / C) |

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
| `state` | Selection | `pass`, `fail`, `warning` |
| `message` | Text | Human-readable result |
| `project_id` | Many2one | Checked project |

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
| `project_id` | Many2one | Project |
| `gate_no` | Selection | G1, G2, or G3 |
| `state` | Selection | `pending`, `passed`, `blocked` |
| `blocking_reasons` | Text | Collected reasons for blocking |

### Gate Check Process

When a gate check is triggered:

1. **Collect deliverables** assigned to the gate
2. **Verify all are approved** — if any are not, the gate is blocked
3. **Check prerequisite gates** — G2 requires G1 passed, G3 requires G2 passed
4. **Run relevant validation rules** (R05–R07)
5. **Record result** — update gate status with pass/block and reasons

```{tip}
Deliverables hook into the gate system via `_hook_gate_check_on_approve()`.
When a deliverable is approved, the engine automatically re-checks its
assigned gate.
```

## WBS Mapping

The engine maps project task stages to deliverable templates using a JSON-based
configuration. When a task moves to a new stage, the engine can automatically
create the corresponding deliverable.

8 project phases are pre-configured with bilingual names (Korean / English).

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

### Cron Jobs (3)

| Cron | Schedule | Purpose |
|---|---|---|
| Weekly validation | Weekly | Run all 11 validation rules on active projects |
| PM04 generation | Weekly | Auto-generate weekly status report (PM04) |
| Garbage collection | Daily | Clean up orphaned validation results |

## Menu Structure

Engine features are integrated into the existing CxFlow menu:

```
CxFlow
└── Engine
    ├── Templates
    ├── Validation Results
    └── Gate Status
```
