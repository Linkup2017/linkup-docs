# Domain Routing

**Module:** `lu_ai_orchestrator`

Domain Routing lets a single *Orchestrator* agent dispatch user messages to
specialised domain agents — Sales, Finance, HR, Inventory, and more — based on
keyword rules, with a configurable fallback when no rule matches.

For installation prerequisites and first-chat setup, see
[Quick Start](quickstart.md). For agent and model configuration, see
[Configuration](configuration.md).

---

## 1. What Is an Orchestrator?

A regular AI agent receives a prompt and generates a response directly using its
own LLM model and system prompt.  An **Orchestrator** agent sits in front of one
or more domain agents and decides which one should handle each prompt.

```{image} /_static/img/ai-agent/domain-routing-overview.png
:alt: Orchestrator dispatching to domain agents
:width: 100%
```

Enabling the **Is Orchestrator** toggle on an agent form activates the routing
layer.  The orchestrator itself may still hold an LLM model — it is used for
LLM-based fallback classification and for direct responses when no rule matches.

### Routing flow

```{mermaid}
flowchart TD
    U([User message]) --> O[Orchestrator agent]
    O --> K{Keyword match?\nsequence order}
    K -- match --> T[Target domain agent]
    T --> R([Response])
    K -- no match --> F{Fallback\nbehavior}
    F -- llm --> L[LLM classifies domain]
    L -- matched --> T
    L -- no match --> S[Orchestrator handles directly]
    F -- first --> T1[First active agent]
    T1 --> R
    F -- self --> S
    S --> R
```

---

## 2. Built-in Domains

`lu_ai_orchestrator` ships five pre-built domain system prompts.  Each domain
agent receives one of these prompts automatically when the orchestrator delegates
to it.

| Domain key | Display name | Odoo models in scope |
|-----------|-------------|----------------------|
| `sales` | Sales & CRM | `sale.order`, `crm.lead`, `res.partner`, `sale.report` |
| `finance` | Finance & Accounting | `account.move`, `account.payment`, `account.journal`, `account.analytic.line` |
| `inventory` | Inventory & Procurement | `stock.picking`, `stock.quant`, `purchase.order`, `product.product` |
| `hr` | Human Resources | `hr.employee`, `hr.attendance`, `hr.payslip`, `hr.leave`, `hr.applicant` |
| `crm` | Customer Relations | `res.partner`, `mail.message`, `crm.lead` |

Each domain prompt instructs the agent to stay strictly within its scope.  If a
user question falls outside the domain, the agent responds with a short
out-of-scope message (e.g., *"This is outside my finance domain."*) rather than
hallucinating an answer.

```{note}
The domain key is matched against the **Domain** field of the routing rule
(case-insensitive).  Routing rules named `"Sales"`, `"sales"`, or `"SALES"` all
resolve to the `sales` system prompt.  Custom rule names that do not match any
built-in key receive an empty system prompt — provide a custom one in the target
agent's own system prompt field.
```

---

## 3. Setting Up an Orchestrator Agent

### Step 1 — Create the orchestrator agent

1. Go to **AI → Agents → Agents**.
2. Click **New**.
3. In the **General** tab:
   - Set a name (e.g., `"Main Orchestrator"`).
   - Assign an LLM model.  This model is used for LLM-based fallback
     classification (section 5.3) and direct responses when no rule matches.
4. Enable the **Is Orchestrator** toggle.
5. Save.

```{image} /_static/img/ai-agent/domain-routing-orchestrator-form.png
:alt: Agent form with Is Orchestrator toggle enabled
:width: 100%
```

### Step 2 — Add routing rules

After enabling **Is Orchestrator**, a **Routing Rules** tab appears.

1. In the **Routing Rules** tab, click **Add a line**.
2. Fill in each rule (see field reference below).
3. Repeat for every domain.
4. Save.

### Routing rule fields

| Field | Required | Description |
|-------|----------|-------------|
| **Sequence** | — | Determines evaluation order.  Lower = higher priority.  Default: `10`. |
| **Domain** | Yes | Name of the domain (e.g., `Sales`, `Finance`).  Used to look up the built-in system prompt. |
| **Keywords** | — | Comma-separated list of trigger words.  Case-insensitive substring match.  Leave blank to create a catch-all rule. |
| **Target Agent** | Yes | The specialised agent to delegate to when this rule matches. |
| **Active** | — | Uncheck to disable the rule without deleting it. |
| **Description** | — | Internal note.  Not used in routing logic. |

```{tip}
Use **Sequence** to set priority between overlapping rules.  For example, a
general "CRM" rule at sequence 20 and a more specific "VIP customer" rule at
sequence 5 — the VIP rule is evaluated first and takes precedence.
```

---

## 4. Keyword Matching

When a user message arrives, the orchestrator:

1. Converts the message to lower-case.
2. **Strips agent-addressing prefixes** — phrases like `"sales agent야,"`,
   `"finance agent,"`, or `"재무 담당자,"` are removed before keyword matching.
   This prevents a false negative when the user addresses a specific agent by
   name but asks about a different domain.
3. Iterates over active routing rules in **sequence order**.
4. For each rule, checks whether any keyword in the comma-separated list is a
   **substring** of the cleaned prompt.
5. Returns the first matching rule's target agent.

### Keyword design tips

| Tip | Example |
|-----|---------|
| Use root forms so prefixes/suffixes match | `invoice` matches `invoices`, `invoicing` |
| Add Korean equivalents for bilingual workspaces | `invoice,인보이스,청구서` |
| Keep keywords distinct across rules to avoid overlap | Avoid `order` in both Sales and Purchase rules — prefer `sales order` vs `purchase order` |
| Avoid very short keywords | `hr` will match `"where"`, `"other"` — use `hr leave`, `payslip`, `employee` instead |

### Address-stripping patterns

The following prefixes are automatically removed before keyword matching.
They work in both English and Korean with optional grammatical particles.

| Prefix pattern | Example |
|---------------|---------|
| `sales agent` / `영업 에이전트` / `영업 담당자` | `"Sales agent, show me Q3 revenue"` → `"show me Q3 revenue"` |
| `finance agent` / `재무 에이전트` / `재무 담당자` | `"재무 담당자야, 청구서 목록 보여줘"` → `"청구서 목록 보여줘"` |
| `inventory agent` / `재고 에이전트` | — |
| `hr agent` / `인사 에이전트` | — |
| `crm agent` / `고객지원 담당자` | — |
| `helpdesk agent` / `헬프데스크 에이전트` | — |

---

## 5. Fallback Behavior

When no keyword rule matches, the orchestrator applies the **Fallback Behavior**
setting.  Configure it on the orchestrator agent form (General tab).

### 5.1 Handle directly (`self`)

The orchestrator responds using its own LLM model and system prompt.
`miss_count` is incremented on each miss so you can track how often no rule
matched (see section 6).

**Use when:** You want the orchestrator to act as a general-purpose assistant
for queries that fall outside defined domains.

### 5.2 Route to first active agent (`first`)

The orchestrator always delegates to the **first** routing rule (lowest
sequence number) regardless of keyword content.

**Use when:** You have a single primary domain agent and want all unmatched
traffic to reach it.

### 5.3 LLM Intent Classification (`llm`)

The orchestrator calls its own LLM with a classification prompt listing all
active routing rules and their keywords.  The LLM returns the single best
domain name.  If the returned name matches a rule, that rule's target agent
handles the message; otherwise, the orchestrator falls back to direct handling.

**Use when:** Keyword coverage is incomplete and you want semantics-based
routing for edge cases.

```{warning}
LLM classification adds a full inference round-trip before the target agent
responds.  This roughly doubles end-to-end latency for unmatched prompts.
Use it only when keyword rules cannot be tuned to sufficient coverage.
```

### Fallback comparison

| Fallback | Latency impact | When to use |
|----------|---------------|-------------|
| `self` | None | General-purpose orchestrator with a capable LLM |
| `first` | None | Single primary domain, simple setup |
| `llm` | +1 LLM call for unmatched prompts | Semantic routing when keyword coverage is insufficient |

---

## 6. Routing Statistics

The orchestrator collects statistics automatically.  No configuration is needed.

### Per-rule statistics

Navigate to **AI → Agents → Agents → (open orchestrator) → Routing Rules** tab.

| Column | Description |
|--------|-------------|
| **Match Count** | Total number of times this rule was selected.  Updated atomically — safe under concurrent requests. |
| **Last Matched** | UTC timestamp of the most recent trigger. |

### Orchestrator-level statistics

| Field | Description |
|-------|-------------|
| **Unmatched Requests** (`miss_count`) | Number of requests where no keyword rule matched and the orchestrator handled directly (fallback = `self`).  Visible on the agent form. |

### Using statistics to tune routing rules

A high `miss_count` means prompts are reaching the orchestrator without
matching any rule.  To investigate:

1. Enable Odoo server logging at `DEBUG` level for the
   `lu_ai_orchestrator` module.
2. Search logs for `[Orchestrator:…] No rule matched` — the full prompt is
   logged at this point.
3. Identify recurring unmatched themes.
4. Add the relevant terms to existing rule keyword lists, or create a new
   routing rule.

```{tip}
Review routing statistics weekly during the first month after deployment.
`miss_count` typically drops to near-zero after two or three rounds of keyword
tuning.
```

---

## 7. Ask AI Integration

When the user clicks the **Ask AI** button in Odoo's list and form views, the
system selects the most appropriate agent automatically.  If an orchestrator is
configured as the Ask AI agent, it takes precedence over domain agents — ensuring
that the routing layer is always invoked first.

To make an orchestrator the Ask AI agent:

1. Open the orchestrator agent form.
2. Enable the **Ask AI Agent** toggle.
3. Save.

Domain agents should **not** have the Ask AI toggle enabled when an orchestrator
is present.  Doing so would bypass the routing layer for Ask AI interactions.

---

## 8. Multi-Domain Example

The following example sets up three domain agents behind a single orchestrator.

### Agents to create

| Agent | LLM | Is Orchestrator | Notes |
|-------|-----|----------------|-------|
| `Main Orchestrator` | `qwen3.5:9b` | Yes | Entry point for all user messages |
| `Sales Agent` | `qwen3.5:9b` | No | Handles sales orders, CRM pipeline |
| `Finance Agent` | `claude-sonnet-4-6` | No | Handles invoices, payments |
| `HR Agent` | `qwen3.5:9b` | No | Handles leaves, payroll, attendance |

### Routing rules on Main Orchestrator

| Seq | Domain | Keywords | Target agent |
|-----|--------|----------|-------------|
| 10 | Sales | `sale order, quotation, opportunity, lead, revenue, 견적, 영업` | Sales Agent |
| 20 | Finance | `invoice, payment, journal, budget, 청구서, 지급, 회계` | Finance Agent |
| 30 | HR | `employee, leave, payroll, attendance, contract, 직원, 휴가, 급여` | HR Agent |

**Fallback behavior:** `self` — the orchestrator answers general ERP questions
that do not belong to any specific domain.

---

## 9. Advanced: Multi-layer Prompts (lu_ai_edge)

Installing the optional `lu_ai_edge` module extends the routing layer with
additional prompt assembly capabilities.

### Chain-of-Thought (CoT) instructions

Each domain rule gains a CoT instruction block appended after the base system
prompt.  These instructions guide the domain agent to reason step-by-step before
producing an answer — particularly useful for complex financial or inventory
calculations.

### Few-shot examples

Domain-specific few-shot examples can be stored in `ir.config_parameter` and
injected into the system prompt at routing time.  This improves consistency for
structured outputs such as tables, formatted reports, or JSON payloads.

### MMR RAG reranking

When a domain agent uses RAG (document retrieval), `lu_ai_edge` replaces the
default similarity-only reranking with **Maximal Marginal Relevance (MMR)**.
MMR balances relevance with diversity, reducing redundant chunks when multiple
documents cover similar content.

The MMR lambda parameter (`ai.edge.mmr_lambda`, default `0.5`) controls the
relevance-diversity trade-off:

- `1.0` — pure relevance (same as the default ranker)
- `0.0` — pure diversity
- `0.5` — balanced (recommended starting point)

Set it at **Settings → Technical → Parameters → System Parameters**.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| All messages handled by orchestrator, no routing | `is_orchestrator` not enabled | Enable **Is Orchestrator** toggle on agent form |
| Rule never matches despite correct keywords | Keyword has leading/trailing whitespace | Check the **Keywords** field — remove extra spaces around commas |
| Korean prompts not matching | Missing Korean keyword variants | Add Korean translations to the keyword list (e.g., `invoice,청구서`) |
| LLM fallback classification returns wrong domain | Ambiguous domain names | Make domain names more distinct; add descriptive keywords |
| `miss_count` keeps rising | Prompts use vocabulary not covered by any rule | Review server logs, identify recurring unmatched patterns, add keywords |
| Domain agent uses wrong system prompt | Domain name in rule does not match a built-in key | Check spelling (`sales`, `finance`, `inventory`, `hr`, `crm`) or add a custom system prompt to the target agent |
| Ask AI does not route through orchestrator | Domain agent has **Ask AI Agent** enabled | Disable **Ask AI Agent** on all domain agents; enable only on the orchestrator |
