# Quick Start

Get an AI assistant running in your Odoo instance in under 10 minutes.

Linkup AI Agent connects Odoo to a local Ollama LLM, an Anthropic Claude cloud LLM,
or both simultaneously — giving you a slide-out side panel that can query your ERP
data using natural language. Complete Steps 1–4 below to finish your first conversation.

:::{warning}
Odoo 19.0 **Enterprise** edition is required. The `ai_app` module is not available in
Community edition, and installation will fail without it.
:::

## Prerequisites

Odoo 19.0 Enterprise
: A running instance with administrator access.

Ollama (for local LLM)
: Install and start Ollama from [ollama.com/download](https://ollama.com/download), then
  pull a model:

  ```bash
  # Recommended model for production
  ollama pull qwen3.5:9b
  ```

Anthropic API key (for Claude)
: Generate one at <https://console.anthropic.com/>.

Administrator account
: Required to access the Settings menu.

:::{tip}
You can configure both Ollama and Claude at the same time and assign a different provider
to each agent (hybrid setup).
:::

## Step 1 — Install the Modules

1. Go to the **Apps** menu.
2. Search for **"Linkup AI"**.
3. Install **Linkup AI Side Panel** (`lu_ai_ui`).
   Dependent modules (`lu_ai_ollama`, `ai`, `ai_app`, `web_enterprise`) are installed
   automatically.
4. To use Claude as well, install **Linkup AI Claude** (`lu_ai_claude`) separately.

:::{tip}
Installing **Linkup AI Side Panel** alone is enough to get all modules required for
Ollama integration.
:::

```{image} /_static/img/ai-agent/qs-install-modules.png
:alt: Linkup AI Side Panel and Linkup AI Claude in the Apps list
:width: 100%
```

## Step 2 — Configure Your LLM Provider

:::{note}
Ollama and Claude are configured on **separate Settings pages**.
Setting up both providers lets you choose a provider per agent in Step 3.
:::

### Option A: Ollama (Local LLM)

1. Go to **Settings → Integrations**.
2. Enable the **"Use local Ollama models"** toggle.
3. Enter your Ollama server address in the URL field (placeholder: `http://localhost:11434`).
   If Ollama is running locally, leave the default value as-is.
4. *(Optional)* API key field (placeholder: `API Key (optional for local setup)`) —
   only required for remote or authenticated endpoints. Leave blank for local installs.
5. Click **Save**.

:::{note}
The fields have no visible labels — only placeholder text. Refer to the screenshot below
to locate them.
:::

```{image} /_static/img/ai-agent/qs-settings-ollama.png
:alt: Settings → Integrations — "Use local Ollama models" section
:width: 100%
```

### Option B: Claude (Cloud LLM)

1. Go to **Settings → AI** (Providers section).
2. Find the **"Use your own Anthropic Claude account"** section and enter your API key.
   The provider is activated automatically once a key is entered.
3. *(Optional)* **Max Output Tokens** — default 16,384. The Odoo UI accepts up to 128,000,
   but actual limits depend on the model (Opus: 128k, Sonnet/Haiku: 64k).
   Values above the model limit are automatically capped at the API level.
4. Click **Save**.

:::{note}
The settings page may display RAG/embedding-related options. These are outside the scope
of Quick Start and are covered in the [Configuration](configuration.md) guide.
:::

```{image} /_static/img/ai-agent/qs-settings-claude.png
:alt: Settings → AI — "Use your own Anthropic Claude account" section
:width: 100%
```

:::{note}
For advanced parameter tuning and RAG (document retrieval) setup, see the
[Configuration](configuration.md) guide.
:::

## Step 3 — Create an AI Agent

1. Go to **AI → Agents → Agents** (Kanban view by default).
2. Click **Create**.
3. Enter an agent name (e.g., `Sales Assistant`).
4. Select a model from the **LLM Model** dropdown:
   - Ollama: `qwen3.5:9b` (recommended) or `qwen3.5:35b` (high performance)
   - Claude: `Claude Sonnet 4.6` (balanced) or `Claude Opus 4.6` (highest capability)
5. *(Optional)* Configure System Prompt, Topics, etc. — keep the defaults for Quick Start.
6. Click **Save**.

:::{tip}
For testing, `qwen3.5:9b` (local, free) or `Claude Haiku 4.5` (cloud, low cost) are
good starting points. For production, `qwen3.5:35b` or `Claude Sonnet 4.6` provide
higher tool-call accuracy. The available model list is populated automatically based on
your provider configuration.
:::

```{image} /_static/img/ai-agent/qs-create-agent.png
:alt: AI → Agents → Agents — agent creation form with LLM Model selector
:width: 100%
```

## Step 4 — Start Your First Chat

1. Click the **AI button** in the Odoo **systray** (top-right).
2. A **side panel** opens on the right side of the screen (purple header, 240–480 px,
   resizable).
3. If you have multiple agents, select one from the **agent selector** in the header.
4. Click **"+"** to start a new conversation.
5. Type a message in the input field at the bottom and press **Enter**.

The AI Agent supports both English and Korean:

- Example (full LLM tool-calling — queries live ERP data):
  > *"Show me the top 5 products by revenue this month"*
- Example (shortcut — instant response):
  > *"이번 달 매출 총액은?"*

Conversation names are set automatically from the first message.
Previous conversations are accessible via the **history button** in the header
(up to 50 recent conversations).

:::{tip}
Built-in shortcut queries cover major domains: Sales, Finance, Inventory, HR, and CRM.
Frequently asked questions bypass the LLM entirely for faster responses.
:::

```{image} /_static/img/ai-agent/qs-first-chat.png
:alt: Side panel showing a sample conversation
:width: 100%
```

## What You Just Set Up

:::{tip}
| Component | Role |
|-----------|------|
| **Ollama** or **Claude API** | LLM inference engine (local or cloud) |
| **`lu_ai_ollama`** / **`lu_ai_claude`** | Odoo ↔ LLM provider connector |
| **`lu_ai_ui`** | Slide-out side panel chat UI |
| **AI Agent** | Configuration unit that binds provider, model, and prompt |

In a hybrid setup, each agent can use a different provider — run latency-sensitive
agents on local Ollama and complex analysis on Claude.
:::

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Module not found: ai_app" during install | Community edition in use | Switch to Enterprise edition |
| "Connection refused" or no response | Ollama server not running | Run `ollama serve`; verify the Base URL |
| "No API key set for Anthropic Claude" | Claude API key not configured | Enter the key at **Settings → AI → Providers** |
| "429 Too Many Requests" or "Invalid API key" | Claude rate limit exceeded or wrong key | Check limits at console.anthropic.com; regenerate key |
| Side panel does not appear | Browser cache | Hard-refresh with Ctrl+Shift+R |

## Next Steps

- **[Configuration](configuration.md)** — Ollama parameter tuning (`num_ctx`,
  `num_predict`, `keep_alive`), Claude token limits, RAG setup, multi-model configuration
- **Domain Routing** — per-domain agent routing (Sales, HR, Finance, and more)
- **Workflows** — AI-driven multi-step automation
- **Proactive Alerts** — automatic detection of ERP anomalies such as low stock or
  overdue receivables
