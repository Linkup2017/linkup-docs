# Proactive Monitoring & Admin

**Modules:** `lu_ai_pro` · `lu_ai_pro_crm` · `lu_ai_pro_helpdesk` · `lu_ai_pro_stock` · `lu_ai_admin`

Proactive Monitoring continuously watches your Odoo data and acts before problems
escalate — without waiting for a user to ask. You define **monitor rules** that
evaluate conditions on a schedule; when a violation is detected, the system can
notify your team, suggest a workflow, or execute a corrective action automatically
depending on the autonomy level you choose.

For workflow configuration, see [Workflows](workflows.md). For agent and model
setup, see [Configuration](configuration.md).

---

## 1. Overview

The proactive stack consists of:

| Module | Role |
|---|---|
| `lu_ai_pro` | Core engine — monitor rules, detection events, cron sweep, dashboard |
| `lu_ai_pro_crm` | CRM domain — lead stagnation and at-risk opportunity detection |
| `lu_ai_pro_helpdesk` | Helpdesk domain — SLA breach, low CSAT, stale ticket detection |
| `lu_ai_pro_stock` | Inventory domain — stock shortage detection with PO coverage check |
| `lu_ai_admin` | Unified admin dashboard — cross-module KPI overview for system admins |

```{mermaid}
flowchart TB
    CRON["Cron Sweep\n(every 5 min)"]
    ENGINE["MonitorEngine\n_run_check()"]
    CHECKERS["Checker\nThreshold / Trend / Anomaly\n+ Domain Custom"]
    DEDUP["Deduplication\nunresolved lock or\ncooldown window"]
    EVENT["Detection Event\nlu.ai.proactive.event"]

    L0["L0 notify_only\nDiscuss message"]
    L1["L1 suggest\nNotify + Workflow"]
    L2["L2 conditional_auto\nAuto if under budget,\notherwise L1 fallback"]
    L3["L3 full_auto\nAuto + Rollback token"]

    CRON --> ENGINE
    ENGINE --> CHECKERS
    CHECKERS --> DEDUP
    DEDUP --> EVENT
    EVENT --> L0
    EVENT --> L1
    EVENT --> L2
    EVENT --> L3
```

---

## 2. How Detection Works

### Detection Cycle

A dedicated cron job (`_cron_sweep_all_monitors`) runs every **5 minutes** and
processes all active monitors whose next scheduled check time is due. It uses
`FOR UPDATE SKIP LOCKED` to safely distribute work across multiple Odoo worker
processes without double-processing the same monitor.

```{mermaid}
flowchart LR
    A["Query target records\n(model + domain_filter)"] --> B["Run checker\n(per record)"]
    B --> C{"Violation?"}
    C -- No --> END["No action"]
    C -- Yes --> D["Deduplication check\n(unresolved or cooldown)"]
    D -- Duplicate --> END
    D -- New --> E["Create Event record"]
    E --> F["Act on event\n(L0 / L1 / L2 / L3)"]
```

### Check Types

| `check_type` | Description | Typical Use |
|---|---|---|
| `threshold` | Compares a numeric field against a static value or a dynamic field path (dot notation) | Stock below reorder point, opportunity probability drop |
| `trend` | Queries a history model for time-series data and detects percentage deviation from the moving average | Sales volume decline, ticket volume spike |
| `anomaly` | Phase 1: statistical (mean ± 2σ); Phase 2: LLM judgment if confidence > 0.7 | Unstructured anomalies with no fixed threshold |

### Deduplication

The `dedup_cooldown_hours` field on each monitor controls how duplicates are
suppressed:

- **`0` (default)** — A new event is only created if no *unresolved* event exists
  for the same monitor + record combination. Once you resolve an event, the monitor
  can fire again.
- **`> 0`** — Suppresses new events for a fixed time window after the last
  detection, regardless of resolved status. Use this for high-frequency checks
  where you want quiet periods.

### Prediction Verification

An hourly cron job (`_cron_verify_predictions`) re-evaluates events that were
detected more than 24 hours ago. It checks whether the violation condition still
holds and records `prediction_correct` (yes/no) on the event. Repeated
mispredictions feed the **circuit breaker** described in the next section.

---

## 3. Autonomy Levels

Each monitor has an **autonomy level** that determines what the engine does when
a new violation event is created:

| Level | Field value | Behaviour |
|---|---|---|
| L0 | `notify_only` | Posts a formatted message to the Discuss channel and/or notifies listed partners. No workflow is triggered. |
| L1 | `suggest` | Sends the notification *and* triggers the linked workflow in **waiting_approval** state — a human must approve before any action executes. |
| L2 | `conditional_auto` | Auto-executes the workflow if the per-monitor and company-wide hourly budgets are not exhausted. Falls back to L1 if either budget is exceeded. |
| L3 | `full_auto` | Executes immediately and issues a **24-hour rollback token**. The notification includes a one-click rollback link valid for 24 hours. |

### Rate Limits

To prevent runaway automation, the engine enforces two hard limits for L2/L3
execution:

- **Per-monitor:** maximum **3 auto-executions per hour**.
- **Company-wide:** configurable (default **20 auto-executions per hour**).
  Adjust via *AI → Settings → Proactive Max Auto Per Company Per Hour*.

When either limit is hit, the engine falls back to L1 (suggest) for that event.

### Monitor Health and Circuit Breaker

If a monitor's check raises an unhandled exception, the engine increments
`consecutive_errors`. At **3 consecutive errors** the monitor transitions to
`error` state and is paused automatically. An alert is posted to the monitor's
notify channel.

The monitor restarts automatically after `auto_restart_after_hours` (configurable
per monitor). You can also manually set it back to *Draft* and re-activate it.

```{mermaid}
stateDiagram-v2
    [*] --> draft
    draft --> active : Activate
    active --> paused : Pause
    paused --> active : Activate
    active --> error : 3 consecutive check errors\n(circuit breaker)
    error --> draft : Manual reset
    error --> active : auto_restart_after_hours elapsed
```

---

## 4. First-Time Setup

### Onboarding Wizard

The fastest way to get started is the built-in onboarding wizard.

**Path:** *AI → Proactive → Setup Wizard*

The wizard walks you through four steps:

1. **Welcome** — Overview of what will be created.
2. **Channel** — Select an existing Discuss channel for notifications, or type a
   name to create one. The AI service user is added as a member automatically.
3. **Scenarios** — Choose which built-in domain scenarios to activate. Scenarios
   from installed domain modules (`lu_ai_pro_crm`, etc.) appear automatically.
4. **Review** — Preview the monitors that will be created, then click
   **Create Monitors**.

```{note}
The wizard is safe to re-run. If a monitor with the same name and target model
already exists for your company and is active, it is skipped — no duplicates are
created.
```

### Installation Order

Install modules in this order to ensure all dependencies resolve correctly:

```
lu_ai_pro
└── lu_ai_pro_crm        (requires: crm)
└── lu_ai_pro_helpdesk   (requires: helpdesk)
└── lu_ai_pro_stock      (requires: stock, purchase)
lu_ai_admin              (requires: lu_ai_pro, lu_ai_rag, lu_ai_orch, lu_ai_workflow)
```

---

## 5. Monitor Configuration

Navigate to *AI → Proactive → Monitors* to view and edit monitor rules.

### Field Reference

**Identity**

| Field | Description |
|---|---|
| `name` | Display name for the monitor |
| `active` | Uncheck to soft-delete without losing history |
| `state` | `draft` / `active` / `paused` / `error` |
| `company_id` | Multi-company scope |

**Target**

| Field | Description |
|---|---|
| `model_id` | The Odoo model to scan (e.g. `crm.lead`) |
| `domain_filter` | Additional Odoo domain to filter records before checking |

**Check Logic**

| Field | Description |
|---|---|
| `check_type` | `threshold`, `trend`, or `anomaly` (domain modules may add custom types) |
| `target_field_id` | The field to evaluate on each matched record |
| `threshold_operator` | `lt`, `lte`, `gt`, `gte`, `eq`, `neq` |
| `threshold_value` | Static numeric threshold |
| `threshold_ref_path` | Dynamic threshold — dot-notation field path on the same record (e.g. `product_min_qty`). Takes precedence over `threshold_value` when set. |
| `trend_window_days` | Number of days of history to analyse for trend checks |
| `trend_change_pct` | Deviation percentage that triggers a trend violation |
| `anomaly_prompt_template` | Custom LLM prompt suffix for anomaly checks |

**Schedule**

| Field | Description |
|---|---|
| `cron_interval_number` | Numeric interval value |
| `cron_interval_type` | `minutes`, `hours`, or `days` |
| `last_check_at` | Timestamp of the last completed run (read-only) |

**Response / Action**

| Field | Description |
|---|---|
| `severity` | `info`, `warning`, or `critical` — affects the notification style |
| `autonomy_level` | `notify_only`, `suggest`, `conditional_auto`, or `full_auto` |
| `auto_workflow_id` | Workflow to trigger for L1/L2/L3 levels |
| `notify_channel_id` | Discuss channel to post alerts to |
| `notify_partner_ids` | Additional partners to notify by direct message |
| `conditional_auto_limit` | Per-event L2 budget cap override |

**Deduplication**

| Field | Description |
|---|---|
| `dedup_cooldown_hours` | `0` = block while unresolved event exists; `> 0` = cooldown window in hours |

**Health**

| Field | Description |
|---|---|
| `consecutive_errors` | Current error streak (resets on success) |
| `auto_restart_after_hours` | Hours after circuit break before automatic restart |
| `sandbox_id` | Security sandbox defining which models the service user may read |

### Running a Check Manually

Open any active monitor and click **Run Now** in the action toolbar. The check
executes synchronously and the result appears in the *Detection Events* smart
button immediately.

---

## 6. Detection Events

When a monitor detects a violation, it creates a **detection event**
(`lu.ai.proactive.event`).

### Key Event Fields

| Field | Description |
|---|---|
| `current_value` | The measured value at detection time |
| `threshold_value` | The threshold value used for comparison |
| `deviation_pct` | Percentage deviation from threshold (computed) |
| `check_summary_html` | Formatted HTML gauge summarising the check result |
| `llm_analysis` | LLM explanation (populated for anomaly check type) |
| `action_taken` | Current action state (see below) |
| `resolved` | Whether the event has been marked resolved |

### Action State Lifecycle

| `action_taken` | Meaning |
|---|---|
| `pending` | Event created, no action yet |
| `notified` | Notification sent (L0) |
| `suggested` | Notification sent + workflow triggered in approval state (L1 / L2 fallback) |
| `auto_executed` | Workflow executed automatically (L2/L3) |
| `escalated` | Manually escalated by an operator |

### Resolving an Event

Open an event and click **Resolve**. Fill in the optional *Resolution Note* and
confirm. This sets `resolved = True` and records who resolved it and when.
Resolving an event allows the monitor to fire again for the same record (when
`dedup_cooldown_hours = 0`).

### L3 Rollback

For `full_auto` events, the notification message includes a **Rollback** button.
The rollback token is valid for **24 hours** from detection time. After that, the
token expires and rollback is no longer possible from the UI.

---

## 7. Built-in Scenarios

### CRM (`lu_ai_pro_crm`)

| Scenario | Target Model | Detection Condition | Interval | Autonomy |
|---|---|---|---|---|
| CRM Lead Stagnation | `crm.lead` | Stage unchanged for **> 30 days**. Skipped automatically if the lead has a planned or due activity. | 1 day | suggest |
| High-Value At-Risk Lead | `crm.lead` | `probability < 30%` on open opportunities | 6 hours | suggest |

```{tip}
The stagnation check uses **activity suppression**: if a salesperson has already
scheduled a follow-up activity on the lead, no alert is generated. This avoids
noise for leads that are actively being worked.
```

### Helpdesk (`lu_ai_pro_helpdesk`)

| Scenario | Target Model | Detection Condition | Interval | Autonomy |
|---|---|---|---|---|
| SLA Deadline Alert | `helpdesk.ticket` | SLA deadline within **< 4 hours** on open tickets | 30 min | suggest |
| Low Customer Satisfaction | `rating.rating` | Customer rating **< 3.0** on consumed helpdesk ratings | 60 min | notify_only |
| Stale Ticket Nudge | `helpdesk.ticket` | Stage unchanged for **> 48 hours** on open tickets | 1 day | suggest |

### Inventory (`lu_ai_pro_stock`)

| Scenario | Target Model | Detection Condition | Interval | Autonomy |
|---|---|---|---|---|
| Stock Shortage Alert | `stock.warehouse.orderpoint` | `qty_on_hand < product_min_qty`. Suppressed if an open purchase order already covers the product. | 60 min | suggest |

```{tip}
The stock shortage check includes **PO coverage suppression**: if a draft, sent, or
confirmed purchase order line already exists for the same product, no alert is
generated. This prevents duplicate re-order suggestions when the procurement team
has already acted.
```

---

## 8. Proactive Dashboard

**Path:** *AI → Proactive → Dashboard*

The dashboard shows aggregated KPIs for all proactive monitors in your company.
Use the **Period** selector to adjust the time window (default: 30 days).

| KPI Field | Description |
|---|---|
| `active_monitors` | Monitors currently in `active` state |
| `error_monitors` | Monitors paused by the circuit breaker |
| `events_24h` | Events detected in the last 24 hours |
| `events_7d` | Events detected in the last 7 days |
| `events_30d` | Events detected in the selected period |
| `auto_executed_24h` | L2/L3 auto-executions in the last 24 hours |
| `pending_approval` | Events with `action_taken = suggested`, awaiting workflow approval |
| `avg_detection_action_secs` | Average seconds from detection to action taken |
| `success_rate` | Percentage of verified events where the prediction was correct |
| `global_cap_usage_pct` | Company-wide L2/L3 hourly budget consumption (%) |

---

## 9. AI Admin Dashboard

**Path:** *AI → AI Dashboard*

```{note}
Access is restricted to **System Administrators** (`base.group_system`).
```

The AI Admin Dashboard is the unified monitoring cockpit for the entire Linkup
AI stack. It aggregates live KPIs from all installed AI modules onto a single
read-only form. Click **Refresh** to reload all metrics on demand.

### Dashboard Sections

**Workflow Execution Status**

| Metric | Description |
|---|---|
| Running | Workflows currently in `running` state |
| Awaiting Approval | Workflows paused at an approval step |
| Failed (24 h) | Workflows that entered `error` state in the last 24 hours |
| Completed (24 h) | Workflows that reached `done` in the last 24 hours |
| LLM Queue | Pending LLM tool-call executions waiting to be processed |

**Proactive Monitor Summary**

| Metric | Description |
|---|---|
| Active Monitors | Monitors in `active` state |
| Error Monitors | Monitors paused by circuit breaker |
| Events (24 h) | Detection events from the last 24 hours |
| Pending Approval | Events awaiting human approval |
| Auto-Executed (24 h) | L2/L3 automatic actions in the last 24 hours |

**Embedding Status by Domain**

Displays per-domain RAG document counts broken down by embedding state:
*Done*, *Pending*, *In Progress*, and *Error*. Useful for monitoring RAG
pipeline health after adding new file sources.

**Agent Routing Status**

| Metric | Description |
|---|---|
| Orchestrator Agents | Number of configured orchestrator agents |
| Unmatched Requests | Routing misses (no domain matched) |
| Routing Rules | Total active routing rules |
| Matched Requests | Successful route hits |

**File Server Status**

Total file sources configured and the number currently in an error state
(connection failures, authentication issues).

### Quick Navigation

The dashboard toolbar provides direct links to the six most common admin tasks:

| Button | Destination |
|---|---|
| Approve Workflows | Workflow states awaiting human approval |
| Approve Proactive Actions | Proactive events with `action_taken = suggested` |
| Proactive Monitors | Full list of monitor rules |
| File Source Config | RAG file server source list |
| Orchestrator Routes | Domain routing rule list |
| AI / LLM Settings | Odoo Settings → AI section |

### Settings: Max Successive LLM Calls

**Path:** *Settings → AI → Max Successive LLM Calls* (default: **5**)

This setting caps how many consecutive LLM tool-call iterations are allowed
within a single conversation turn. Lowering the value prevents runaway loops in
complex agentic tasks; raising it allows more autonomous multi-step reasoning.

---

## 10. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Monitor transitions to `error` state | 3 consecutive check failures triggered the circuit breaker | Open the monitor, check the error message posted to the notify channel, fix the root cause (e.g. domain syntax, field path), then set back to *Draft* and re-activate. Or wait for `auto_restart_after_hours`. |
| No events are generated despite expected violations | `domain_filter` excludes the affected records, or the service user lacks model access | Click **Run Now** and inspect the server log. Check `sandbox_id` whitelist — the target model and any referenced relation models must be listed. |
| L2/L3 auto-execution stops and falls back to suggest | Company-wide or per-monitor hourly budget exhausted | Increase *Proactive Max Auto Per Company Per Hour* in settings, or reduce the check interval on high-frequency monitors. |
| Duplicate events created for the same record | `dedup_cooldown_hours = 0` but a prior event was manually resolved | Either set `dedup_cooldown_hours > 0` to enforce a quiet period, or leave the prior event unresolved until the underlying issue is fixed. |
| Rollback button missing from event notification | More than 24 hours have passed since detection | The rollback token has expired. Undo the action manually through the relevant Odoo record. |
| Prediction verification lowers `success_rate` | AnomalyChecker LLM confidence < 0.7, or thresholds are too sensitive | Review and adjust `threshold_value` or `anomaly_prompt_template`. Consider switching to `threshold` check type for well-defined conditions. |
