# Architecture Overview

This page is written for **system integrators and technical evaluators** who need to understand how Linkup AI Agent fits into an Odoo 19 Enterprise environment — module wiring, data flows, and extension points.

---

## System Architecture

Linkup AI Agent is built around a **four-tier stack** that separates LLM providers, orchestration, automation, and enterprise extensions:

```
┌──────────────────────────────────────────────────────────┐
│  Tier 4 — Enterprise Extensions  (lu_ai_edge, lu_ai_admin)│
├──────────────────────────────────────────────────────────┤
│  Tier 3 — Automation             (lu_ai_workflow, lu_ai_pro)│
├──────────────────────────────────────────────────────────┤
│  Tier 2 — Core Services          (lu_ai_orch, lu_ai_rag)  │
├──────────────────────────────────────────────────────────┤
│  Tier 1 — LLM Providers          (lu_ai_ollama, lu_ai_claude)│
└──────────────────────────────────────────────────────────┘
```

A key design choice is **hybrid provider support**: `lu_ai_ollama` and `lu_ai_claude` can run simultaneously. Each AI agent is individually assigned to a provider, so you can route sensitive HR queries to a local Ollama model while using Claude for complex reasoning tasks — without changing any other configuration.

### High-Level Data Flow

```{mermaid}
graph LR
    U["User"]
    SP["Side Panel\nlu_ai_sidepanel"]
    OR["Orchestrator\nlu_ai_orch"]
    RAG["RAG Engine\nlu_ai_rag"]
    OL["Ollama Server\nlocal LLM"]
    CL["Anthropic API\ncloud LLM"]
    DB["Odoo Database\n& Domain Models"]

    U -->|"natural language"| SP
    SP -->|"route request"| OR
    OR -->|"fetch context"| RAG
    RAG -->|"vector search"| DB
    RAG -->|"injected context"| OR
    OR -->|"assembled prompt"| OL
    OR -->|"assembled prompt"| CL
    OL -->|"streaming response"| OR
    CL -->|"streaming response"| OR
    OR -->|"formatted result"| DB
    DB -->|"updated state"| U
```

---

## Module Dependencies

### Dependency Tier Hierarchy

```{mermaid}
graph TD
    subgraph T1["Tier 1 — LLM Providers"]
        OLL["lu_ai_ollama"]
        CLA["lu_ai_claude"]
    end

    subgraph T2["Tier 2 — Core Services"]
        ORC["lu_ai_orch"]
        RAG["lu_ai_rag"]
    end

    subgraph T3["Tier 3 — Automation"]
        WFL["lu_ai_workflow"]
        PRO["lu_ai_pro"]
    end

    subgraph T4["Tier 4 — Enterprise"]
        EDG["lu_ai_edge"]
        ADM["lu_ai_admin"]
    end

    subgraph DOM["Domain Extensions"]
        OD["lu_ai_orch_*\n6 domains"]
        RD["lu_ai_rag_*\n7 domains"]
        PD["lu_ai_pro_*\n3 domains"]
    end

    ORC --> OLL
    RAG --> OLL
    WFL --> ORC
    WFL --> OLL
    PRO --> WFL
    EDG --> ORC
    EDG --> RAG
    EDG --> WFL
    ADM --> ORC
    ADM --> RAG
    ADM --> WFL
    ADM --> PRO
    OD --> ORC
    RD --> RAG
    PD --> PRO
```

### Core Module Reference

| Module | Depends on | Role |
|---|---|---|
| `lu_ai_ollama` | `base`, `ai_app` | Local LLM provider — Ollama connector, model management, streaming |
| `lu_ai_claude` | `base`, `ai_app` | Cloud LLM provider — Anthropic Claude (Opus / Sonnet / Haiku) |
| `lu_ai_orch` | `ai`, `ai_app`, `lu_ai_ollama` | Orchestrator — domain routing, system prompts, context injection |
| `lu_ai_rag` | `ai`, `lu_ai_ollama` | RAG engine — file-server polling, Ollama embeddings, vector search |
| `lu_ai_workflow` | `base`, `mail`, `ai`, `base_automation`, `lu_ai_ollama`, `lu_ai_orch` | Workflow engine — agentic loop, HITL approval, async LLM queue |
| `lu_ai_pro` | `lu_ai_workflow` | Proactive monitor — anomaly detection, graduated autonomous execution |
| `lu_ai_edge` | `lu_ai_ollama`, `lu_ai_orch`, `lu_ai_rag`, `lu_ai_workflow` | Enterprise extension — advanced RAG, error recovery, dynamic planning |
| `lu_ai_admin` | `lu_ai_ollama`, `lu_ai_rag`, `lu_ai_orch`, `lu_ai_workflow`, `lu_ai_pro` | Admin dashboard — usage analytics, model monitoring |

### Domain Extension Modules

Each core tier ships domain-specific add-ons that plug in via `_inherit`:

| Domain | Orch extension | RAG extension | Proactive extension |
|---|---|---|---|
| CRM | `lu_ai_orch_crm` | `lu_ai_rag_crm` | `lu_ai_pro_crm` |
| Finance | `lu_ai_orch_account` | `lu_ai_rag_finance` | — |
| Helpdesk | `lu_ai_orch_helpdesk` | `lu_ai_rag_helpdesk` | `lu_ai_pro_helpdesk` |
| HR | `lu_ai_orch_hr` | `lu_ai_rag_hr` | — |
| Sales | `lu_ai_orch_sale` | `lu_ai_rag_sales` | — |
| Inventory | `lu_ai_orch_stock` | `lu_ai_rag_inventory` | `lu_ai_pro_stock` |
| Procurement | — | `lu_ai_rag_procurement` | — |

---

## Domain Routing Architecture

When a user sends a query, the orchestrator (`lu_ai_orch`) classifies it and dispatches to the matching domain agent. Each domain agent carries its own system prompt, Odoo field mappings, and context rules.

```{mermaid}
graph TD
    Q["User Query"]
    RT["Orchestrator Router\nlu_ai_orch"]

    subgraph AGENTS["Domain Agents"]
        AC["Account Agent\nlu_ai_orch_account"]
        CR["CRM Agent\nlu_ai_orch_crm"]
        HD["Helpdesk Agent\nlu_ai_orch_helpdesk"]
        HR["HR Agent\nlu_ai_orch_hr"]
        SL["Sales Agent\nlu_ai_orch_sale"]
        ST["Stock Agent\nlu_ai_orch_stock"]
    end

    subgraph MODELS["Odoo Models"]
        ACM["account.move\naccount.payment"]
        CRM["crm.lead"]
        HDM["helpdesk.ticket"]
        HRM["hr.employee\nhr.leave"]
        SLM["sale.order"]
        STM["stock.move\npurchase.order"]
    end

    Q --> RT
    RT --> AC & CR & HD & HR & SL & ST
    AC --> ACM
    CR --> CRM
    HD --> HDM
    HR --> HRM
    SL --> SLM
    ST --> STM
```

Domain agents are defined primarily in XML (`data/agent_*.xml`) — no Python subclass is required unless custom method overrides are needed. This makes adding a new domain a configuration task rather than a development task. See :doc:`domain-routing` for details.

---

## RAG & Context Injection

`lu_ai_rag` replaces Odoo's default OpenAI/Google embedding provider with **local Ollama embeddings** (`nomic-embed-text`). No file content ever leaves your server.

### Embedding Pipeline

1. **File Source Registration** — An administrator registers one or more network file sources (SMB share, local path) in the *AI → RAG → File Sources* view.
2. **Polling Cron** — `ir.cron` (`ir_cron.xml`) polls each source on a configurable schedule, detects new or changed files, and queues them for embedding.
3. **Embedding** — Changed files are chunked and sent to the Ollama embedding API. Resulting vectors are stored in `ai.embedding` records.
4. **Retrieval** — At query time, the user's prompt is embedded and a cosine-similarity search retrieves the top-k chunks. These are injected into the assembled prompt before the LLM call.

### Domain Partitioning

Each `lu_ai_rag_*` module attaches a domain tag to its `ai.embedding` records (e.g., `crm`, `finance`). The orchestrator filters embeddings by the active domain agent before retrieval, preventing cross-domain data leakage.

```{tip}
`lu_ai_edge` further improves retrieval quality with **MMR reranking** (Maximal Marginal Relevance) — selecting results that are both relevant *and* diverse rather than clustering around the nearest neighbors.
```

---

## Data Flow Architecture

### Step-by-Step: User Query → LLM Response

1. **User sends a message** in the side panel (`lu_ai_sidepanel`).
2. **Orchestrator receives the request** (`lu_ai_orch`), identifies the active agent and its assigned provider (Ollama or Claude).
3. **Domain routing** — The orchestrator matches the query against registered routes (`lu.ai.orchestrator.route`) and selects the best-fit domain agent.
4. **Context assembly**:
   - Domain-specific system prompt is loaded from the route record.
   - RAG retrieval runs against domain-filtered embeddings (`lu_ai_rag`).
   - Retrieved chunks are appended to the prompt context.
   - Runtime context is injected (user language, company name — see `lu_ai_edge`).
5. **LLM inference** — The assembled prompt is streamed to Ollama or the Anthropic API. Responses stream back token by token.
6. **Post-processing** — The response is formatted, linked to the originating Odoo record (chatter thread), and persisted.
7. **State update** — If the query triggered a write action (e.g., "update this lead's stage"), the result is applied to the Odoo model and an audit log entry is written.

### Workflow Execution Path

Queries that involve **multi-step automation** are handled by `lu_ai_workflow` instead:

```
Trigger (cron / record event / manual)
  → Workflow State created
  → Steps executed sequentially (llm_call / code_action / http_request)
  → HITL approval gate (if configured)
  → Security sandbox validates write actions
  → Result persisted, execution metric recorded
```

See :doc:`workflows` for the full workflow reference.

---

## Understanding the `_inherit` Pattern

Odoo uses `_inherit` to extend existing models without forking them. Linkup AI Agent modules are layered on this pattern extensively — each tier extends models from the tier below.

### How `_inherit` Works

```python
class MyExtension(models.Model):
    _inherit = 'existing.model'   # extend without a new database table

    # Add fields, override methods, or call super()
    def existing_method(self):
        result = super().existing_method()
        # ... custom logic
        return result
```

The child class shares the same database table as the parent. Multiple modules can extend the same model independently; Odoo merges them at runtime via Python's MRO.

### Example 1 — Advanced RAG Reranking (`lu_ai_edge`)

`AiAgentEdge` extends `ai.agent` to replace the default vector-nearest-neighbour retrieval with MMR reranking:

```python
class AiAgentEdge(ShortcutEngineMixin, models.Model):
    _inherit = 'ai.agent'

    def _rerank_rag_results(self, prompt, embeddings, top_n=2, prompt_embedding=None):
        """Cross-encoder reranking + MMR diversity selection."""
        # Compute cosine similarity between prompt vector and each embedding
        # Apply MMR: balance relevance vs. diversity via lambda parameter
        lam = float(self.env['ir.config_parameter'].sudo()
                        .get_param('ai.edge.mmr_lambda', '0.5'))
        # ... MMR selection loop
        return self.env['ai.embedding'].browse(selected_ids)
```

The `lam` parameter (0.0 = max diversity, 1.0 = max relevance) is tunable per deployment via `ir.config_parameter` without code changes.

### Example 2 — Workflow Error Recovery (`lu_ai_edge`)

`AiWorkflowEdge` extends `lu.ai.workflow` to add 9 automatic error-correction strategies before surfacing a failure:

```python
class AiWorkflowEdge(models.Model):
    _inherit = 'lu.ai.workflow'

    def _handle_step_error(self, state, step, error, attempt=1):
        """Delegates to ErrorRecoveryEngine; falls back to base on exhaustion."""
        from odoo.addons.lu_ai_edge.engine.advanced_error_recovery import ErrorRecoveryEngine
        recovery = ErrorRecoveryEngine(self.env).recover(state, step, error, attempt)
        if recovery is not None:
            return recovery
        return super()._handle_step_error(state, step, error, attempt=attempt)

    def _plan_execution(self, state, remaining_steps):
        """LLM-based dynamic step reordering (skipped for ≤2 remaining steps)."""
        if len(remaining_steps) <= 2:
            return remaining_steps
        from odoo.addons.lu_ai_edge.engine.advanced_planner import DynamicPlannerEngine
        return DynamicPlannerEngine(self.env).plan(state, remaining_steps)
```

The base implementation is always reachable via `super()`, so removing `lu_ai_edge` gracefully degrades to standard behavior.

### Example 3 — Advanced Prompt Engineering (`lu_ai_edge`)

`AiOrchestratorRouteEdge` extends `lu.ai.orchestrator.route` to layer Chain-of-Thought instructions, few-shot examples, and runtime context on top of the base system prompt:

```python
class AiOrchestratorRouteEdge(models.Model):
    _inherit = 'lu.ai.orchestrator.route'

    def _get_system_prompt(self):
        """Multi-layer CoT + few-shot + dynamic context (feature-flagged)."""
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'ai.edge.advanced_prompt_enabled', 'True'
        )
        if enabled.lower() not in ('true', '1', 'yes'):
            return super()._get_system_prompt()    # standard prompt
        return self._build_advanced_prompt(super()._get_system_prompt())
```

The feature can be disabled per environment via `ir.config_parameter` — useful for A/B testing prompt strategies.

---

## Security Model

### Role-Based Access Control

Linkup AI Agent ships its own security groups defined in `lu_ai_ollama/security/security.xml` and extended by each module. Access to AI configuration, RAG sources, workflow definitions, and proactive monitors is gated at the group level.

### AI Security Sandbox

`lu_ai_workflow` enforces a **security sandbox** for all write actions generated by AI steps. Before any AI-produced code action is executed, it is checked against a configurable allowlist (`ai.security.sandbox`). Actions outside the allowlist require explicit human approval (HITL gate).

```{warning}
The HITL approval gate is enabled by default for all `code_action` steps. Disabling it for autonomous workflows requires a conscious configuration choice in *AI → Settings → Security*.
```

### Data Isolation

- RAG embeddings are domain-partitioned; a CRM query cannot retrieve Finance embeddings.
- Field-level masking is configured per domain agent — sensitive fields (e.g., salary data) are excluded from prompt context automatically.
- Every AI interaction is written to an audit log (`ai.security.log`) accessible from the admin dashboard.

---

## Performance & Optimization

### Async LLM Queue

`lu_ai_workflow` routes all LLM calls through an async queue managed by two cron jobs:

| Cron | File | Role |
|---|---|---|
| `ir_cron_async_worker` | `data/ir_cron_async_worker.xml` | Picks up pending `lu.ai.llm.request` records and dispatches to the provider |
| `ir_cron_workflow_timeout` | `data/ir_cron_workflow_timeout.xml` | Marks stalled workflow states as `timeout` after the configured threshold |

This decouples user-facing response latency from heavy multi-step workflows.

### Caching & Connection Pooling

- **Embedding vectors** are stored per-chunk in `ai.embedding` and reused across queries.
- **Prompt templates** are cached in `data/prompt_templates.xml` (loaded by `lu_ai_edge`).
- The Ollama client maintains persistent HTTP connections; avoid setting a very short `OLLAMA_KEEP_ALIVE` on the server side to benefit from model keep-warm.

---

## Extending the Architecture

### Creating a Custom Domain Agent

Domain agents follow the `lu_ai_orch_*` pattern. The minimum required is an XML data file that registers a `lu.ai.orchestrator.route` record:

```xml
<record id="route_my_domain" model="lu.ai.orchestrator.route">
    <field name="name">My Domain</field>
    <field name="active">True</field>
    <field name="system_prompt">You are an expert in ...</field>
    <field name="model_fields">field_a,field_b,field_c</field>
</record>
```

Add a Python model only if you need to override routing logic or add custom fields. See :doc:`domain-routing` for a complete walkthrough.

### Adding a Custom Workflow Step Type

New step types are registered in `lu.ai.workflow.step` by extending the `step_type` selection field:

```python
class MyWorkflowStep(models.Model):
    _inherit = 'lu.ai.workflow.step'

    step_type = fields.Selection(
        selection_add=[('my_type', 'My Custom Step')],
    )

    def _execute_my_type(self, state):
        # Custom execution logic
        ...
```

Register the execution handler in the parent workflow's `_execute_step` dispatch table. See :doc:`workflows` for the step execution API.

### Enterprise Hook Points via `lu_ai_edge`

`lu_ai_edge` exposes three main extension points:

| Extension point | Model | Override method | Purpose |
|---|---|---|---|
| RAG quality | `ai.agent` | `_rerank_rag_results` | Replace or augment retrieval ranking |
| Workflow resilience | `lu.ai.workflow` | `_handle_step_error`, `_plan_execution` | Custom recovery strategies, dynamic ordering |
| Prompt engineering | `lu.ai.orchestrator.route` | `_get_system_prompt` | Layer CoT, few-shot, or runtime context onto the base prompt |

All three follow the same pattern: call `super()` to preserve base behavior and extend from there.

---

## Additional Resources

- :doc:`quickstart` — Install and connect Ollama in 10 minutes
- :doc:`configuration` — Model parameters, system prompts, security settings
- :doc:`domain-routing` — Define and customize domain agents
- :doc:`workflows` — Build multi-step agentic workflows
- :doc:`proactive-alerts` — Configure scheduled proactive monitors
