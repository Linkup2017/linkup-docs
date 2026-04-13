# Workflows

**Module:** `lu_ai_workflow`

Workflows let you define multi-step automation sequences that AI agents execute
inside Odoo — calling LLMs, running server actions, branching on conditions,
requesting human approval, and sending notifications — all in a stateful,
auditable loop.

For agent and model setup, see [Configuration](configuration.md). For routing
messages to domain agents, see [Domain Routing](domain-routing.md).

---

## 1. What Is a Workflow?

A **workflow** is a sequence of typed steps executed by the `lu_ai_workflow`
engine. The engine maintains a shared **context** (a JSON dictionary) across all
steps — each step can read prior outputs and write its own result back, giving
the workflow a persistent memory throughout the run.

```{mermaid}
stateDiagram-v2
    [*] --> pending
    pending --> running : trigger fired
    running --> waiting_approval : approval step reached
    waiting_approval --> running : approved
    waiting_approval --> cancelled : rejected
    running --> done : all steps complete
    running --> error : unhandled exception
    running --> timeout : wall-clock limit exceeded
    running --> cancelled : manual cancel
    done --> [*]
    error --> [*]
    timeout --> [*]
    cancelled --> [*]
```

### Core components

| Model | Purpose |
|-------|---------|
| `lu.ai.workflow` | Workflow definition — trigger, agent, safety guards, steps |
| `lu.ai.workflow.step` | Individual execution unit — LLM call, action, approval, condition, notification |
| `lu.ai.workflow.state` | Single run record — context, progress, step logs, final state |
| `lu.ai.workflow.hook` | Event trigger or lifecycle interceptor |
| `lu.ai.llm.request` | Async LLM queue entry for background processing |
| `lu.ai.security.sandbox` | Optional model/field access policy for execution |

---

## 2. Creating a Workflow

Navigate to **AI → Workflows → Workflows** and click **New**.

### Workflow fields

| Field | Description |
|-------|-------------|
| **Name** | Display name of the workflow |
| **State** | `Draft` → `Active` → `Archived`.  Only Active workflows can be triggered. |
| **Trigger Type** | How the workflow is started — `Manual`, `Scheduled (Cron)`, or `Database Event` |
| **Default Agent** | LLM agent used by steps that do not override the agent individually |
| **Max Steps Guard** | Hard cap on step iterations per run.  Prevents infinite loops in branching workflows. Default: `50` |
| **Timeout (seconds)** | Wall-clock limit for the entire run.  The engine marks timed-out runs as `timeout`. Default: `300` |
| **Max Concurrent Runs** | Maximum number of simultaneous active runs.  `0` = unlimited. |
| **Security Sandbox** | Optional `lu.ai.security.sandbox` policy restricting which models and fields the workflow can access |
| **Description** | Internal documentation — not used in execution |

### Activating a workflow

1. Fill in all required fields and add at least one step.
2. Click **Activate** — the state changes from `Draft` to `Active`.
3. To disable without deleting, click **Archive**.

```{warning}
A workflow in `Draft` state cannot be triggered manually or by automation.
Always activate before testing.
```

---

## 3. Step Types

Add steps in the **Steps** tab of the workflow form.  Steps execute in ascending
**Sequence** order by default.  Set `Active = False` on a step to skip it
without deleting it.

### 3.1 LLM Call (`llm_call`)

Sends a prompt to an LLM agent and stores the response in the workflow context.

| Field | Description |
|-------|-------------|
| **Prompt Template** | Text sent to the LLM.  Use `{key}` placeholders to inject values from the current context (e.g., `{customer_name}`, `{analysis}`). |
| **Save Output As** | Context key under which the LLM response is stored.  Subsequent steps can reference it with `{key}`. |
| **Agent** | Override the workflow-level default agent for this step only. |
| **Async LLM** | If enabled, the LLM call is queued in the background and the run suspends until the worker processes it.  See [section 6](#6-async-llm). |

```{note}
Output chaining example: a step with `Save Output As = "analysis"` stores the
LLM response under the key `analysis`.  A later step can use `{analysis}` in
its prompt template to include that output.
```

### 3.2 Agent Delegate (`agent_delegate`)

Delegates the current context to a sub-agent and stores its response.

| Field | Description |
|-------|-------------|
| **Agent** | The target sub-agent to delegate to. |
| **Delegate Context Keys** | Comma-separated list of context keys to forward.  Leave blank to forward the full context. |
| **Save Output As** | Context key for the sub-agent response. |

### 3.3 Odoo Action (`odoo_action`)

Executes an existing **Server Action** (`ir.actions.server`).

| Field | Description |
|-------|-------------|
| **Server Action** | The `ir.actions.server` record to execute. |

```{tip}
Use Odoo Action steps to write records, send emails, or call Python business
logic without writing custom code in the workflow itself.
```

### 3.4 Human Approval (`approval`)

Pauses the workflow and requests a human decision before continuing.

| Field | Description |
|-------|-------------|
| **Approval Group** | User group notified when the workflow reaches this step.  Group members receive an activity in their inbox. |
| **Approval Timeout (hours)** | If no decision is made within this window, the run moves to `cancelled`. |

**Flow:**

1. Engine sets run state to `waiting_approval` and creates a `mail.activity`.
2. An authorised user opens the run and clicks **Approve** or **Reject**.
3. On **Approve** → execution continues from the next step.
4. On **Reject** → run moves to `cancelled` with the rejection reason recorded.

```{warning}
If **Approval Timeout** elapses without a decision, the run is automatically
cancelled by the `_cron_check_timeouts` scheduled action.  Ensure the group
members are aware of pending approvals.
```

### 3.5 Condition Branch (`condition`)

Evaluates a Python expression and jumps to a different step based on the result.

| Field | Description |
|-------|-------------|
| **Condition Expression** | A Python expression evaluated with `safe_eval` against the current context dict.  Must return a truthy or falsy value (e.g., `context.get('score', 0) >= 80`). |
| **Next Step if True** | Sequence number of the step to execute when the expression is truthy. |
| **Next Step if False** | Sequence number of the step to execute when the expression is falsy. |

```{mermaid}
flowchart LR
    C{Condition\nexpr} -- True --> T[Step at next_true\nsequence]
    C -- False --> F[Step at next_false\nsequence]
```

```{note}
The expression is evaluated against a Python dict where every context key is a
top-level variable.  For example, if the context contains `{"score": 85}`,
use `score >= 80` (not `context['score'] >= 80`).
```

### 3.6 Notify (`notify`)

Sends a Discuss message to partners or a channel.

| Field | Description |
|-------|-------------|
| **Partners** | List of `res.partner` records to notify. |
| **Channel** | Optional `discuss.channel` to post the message to. |
| **Message Template** | Message text.  Supports `{key}` placeholders from context. |

---

## 4. Triggers

### 4.1 Manual

Set **Trigger Type** to `Manual`.  Run the workflow by:

- Opening the workflow form and clicking **Run** in the action menu.
- Calling `workflow.action_run_manual(context_json={"key": "value"})` from Python
  to pass an initial context.

### 4.2 Scheduled (Cron)

Set **Trigger Type** to `Scheduled (Cron)`.  An `ir.cron` record is created
automatically.  Configure the schedule on the cron record at
**Settings → Technical → Automation → Scheduled Actions**.

### 4.3 Database Event (Automation)

Set **Trigger Type** to `Database Event`, then add an event hook in the
**Hooks** tab.  The hook creates a `base.automation` rule that fires the
workflow when a database event occurs.

#### Event hook fields

| Field | Description |
|-------|-------------|
| **Hook Type** | `Record Created`, `Record Updated`, or `Field Changed` |
| **Model** | Odoo model to watch (e.g., `sale.order`) |
| **Filter Domain** | Optional JSON domain to limit which records trigger the workflow (e.g., `[["state","=","sale"]]`) |
| **Watched Fields** | For `Field Changed` only — the specific fields that must change to fire the hook |

---

## 5. Monitoring Runs

Navigate to **AI → Workflows → Runs** to browse all execution records
(`lu.ai.workflow.state`).

### Run states

| State | Meaning |
|-------|---------|
| `pending` | Queued but not yet started |
| `running` | Actively executing steps |
| `waiting_approval` | Paused at a Human Approval step |
| `done` | Completed successfully |
| `error` | Stopped due to an unhandled exception |
| `timeout` | Wall-clock limit exceeded |
| `cancelled` | Manually cancelled or rejected at an approval step |

### Step logs

Open a run record and expand the **Step Logs** tab to see an immutable audit
trail for every executed step.

| Column | Description |
|--------|-------------|
| **Step** | Step name and type |
| **Duration (ms)** | Execution time in milliseconds |
| **Tokens In / Out** | LLM input and output token counts (LLM steps only) |
| **Output** | JSON output stored by the step |
| **Error** | Exception message if the step failed |

```{tip}
Use the **Dashboard** view (**AI → Workflows → Dashboard**) for aggregated
KPIs: total runs, success rate, average duration, and pending approvals over a
rolling 30-day window.
```

---

## 6. Async LLM

By default, LLM Call steps execute synchronously — the engine waits for the
model to respond before proceeding.  For slow models or high-concurrency
deployments, enable **Async LLM** on a step.

### Async execution flow

```{mermaid}
sequenceDiagram
    participant E as Workflow Engine
    participant Q as ai.llm.request queue
    participant W as AsyncLlmWorker (cron)
    participant L as LLM (Ollama / Claude)

    E->>Q: Enqueue request (priority, prompt)
    E-->>E: Suspend run (state = running,\ncurrent_step suspended)
    W->>Q: Poll pending requests
    W->>L: Send prompt
    L-->>W: Response
    W->>E: Resume run (_resume_from_llm_request)
    E-->>E: Store response in context,\nadvance to next step
```

### When to use Async LLM

| Scenario | Recommendation |
|----------|---------------|
| LLM response time > 30 s | Enable Async LLM to free up the Odoo worker process |
| Many concurrent workflows | Async queuing prevents worker exhaustion |
| Priority-sensitive workloads | Set request **Priority** (`low`, `normal`, `high`) to control processing order |

```{note}
The `AsyncLlmWorker` cron job must be active for async requests to be
processed.  Verify at **Settings → Technical → Automation → Scheduled
Actions** — look for the action named **AI: Process Async LLM Queue**.
```

---

## 7. Lifecycle Hooks

Hooks let you intercept execution at specific points or react to database
events.  Add hooks in the **Hooks** tab of the workflow form.

### Hook types

#### Event trigger hooks

These fire the workflow when a database change occurs (see [section 4.3](#43-database-event-automation)).

| Hook Type | Fires when |
|-----------|-----------|
| `record_created` | A matching record is created |
| `record_updated` | A matching record is updated |
| `field_changed` | A watched field on a matching record changes |

#### Execution interceptor hooks

These run inside the engine loop and can inspect or modify execution.

| Hook Type | Called when |
|-----------|-----------|
| `pre_step` | Before any step executes |
| `post_step` | After any step completes |
| `pre_tool` / `post_tool` | Before/after a tool is invoked by an LLM step |
| `on_complete` | When the run reaches a terminal state (done / error / timeout / cancelled) |
| `on_approve` / `on_reject` | When a Human Approval step is decided |

### Hook output

An interceptor hook's server action can return a `HookOutput` dict with the
following optional keys:

| Key | Type | Effect |
|-----|------|--------|
| `decision` | `"allow"` or `"deny"` | `deny` aborts the current step with a `StepDeniedError` |
| `reason` | string | Reason logged when decision is `deny` |
| `inject_context` | dict | Merged into the workflow context after the step |
| `stop` | bool | If `True`, marks the run as `done` immediately after the step |

```{note}
Installing the optional `lu_ai_edge` module activates three advanced
engine-level hooks on the workflow model:

- `_handle_step_error` — automatic error recovery with configurable retry strategies
- `_evaluate_step_result` — LLM-based quality assessment of step outputs (retries up to 3×)
- `_plan_execution` — LLM-driven dynamic step reordering at runtime
```

---

## 8. Security and Sandbox

### Permission groups

| Group | Permissions |
|-------|-------------|
| **System** (`base.group_system`) | Full access — create, edit, delete all workflow objects |
| **Workflow Manager** (`lu_ai_workflow.group_workflow_manager`) | Create and edit workflows, steps, hooks, and runs; cannot delete |
| **User** (`base.group_user`) | Read-only access to all workflow objects |

### Security sandbox

Attach a `lu.ai.security.sandbox` record to a workflow via the **Security
Sandbox** field to restrict which Odoo models and fields the execution engine
may access.  The sandbox policy is enforced by the `lu.ai.security.mixin`
during execution and prevents unauthorised `sudo()` escalation.

```{warning}
Workflows that call server actions with broad `sudo()` access can bypass
sandbox restrictions defined at the workflow level.  Always review server
actions linked to `odoo_action` steps before activating a workflow in
production.
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Run stuck in `running` | Infinite loop between condition branches | Check that `condition_next_true` and `condition_next_false` do not form a cycle; verify the expression eventually produces a different result |
| Run moves to `timeout` | Step processing exceeds `timeout_seconds` | Increase **Timeout** on the workflow, or enable **Async LLM** on slow LLM Call steps |
| HITL approval notification not received | `approval_group_id` not set or group has no members | Set a valid group on the Approval step; ensure group members exist |
| Async LLM step never resumes | `AsyncLlmWorker` cron is inactive | Go to **Settings → Technical → Automation → Scheduled Actions** and activate **AI: Process Async LLM Queue** |
| `condition_next_true` jumps to wrong step | Sequence number does not match any existing step | Open the Steps tab and verify the sequence numbers referenced in the condition |
| `{key}` not replaced in prompt template | Context key not yet set when step runs | Check that the step producing `Save Output As = "key"` runs before the step consuming `{key}` |
| Run count not increasing after trigger | Workflow still in `Draft` state | Click **Activate** on the workflow form |

---

## Next Steps

- [Proactive Alerts & Admin](proactive-alerts.md)
- [Architecture Overview](architecture.md)
