# Configuration

This guide covers deep configuration for Linkup AI Agent — Ollama connection
tuning, model parameters, Claude API setup, agent customization, RAG (document
retrieval), access control, and multi-model setup.

For initial installation and getting a first chat running, see the
[Quick Start](quickstart.md) guide.

---

## 1. Ollama Provider Settings

**Module:** `lu_ai_ollama`

### Accessing the settings

1. Go to **Settings → Integrations**.
2. Enable the **"Use local Ollama models"** toggle if it is not already on.

The Ollama configuration block becomes visible immediately after enabling the toggle.

### Fields

| Field | Default | Description |
|-------|---------|-------------|
| **Base URL** | `http://localhost:11434` | Address of the Ollama HTTP server. Change this if Ollama runs on a remote host or a non-default port. |
| **API Key** | *(empty)* | Optional. Required only for remote or authenticated endpoints (e.g., a shared Ollama server behind a reverse proxy). Leave blank for local installs. |

### Testing the connection

Click **Test Connection** after saving. A green banner confirms that Odoo can
reach the Ollama server and retrieve its model list. A red banner with an error
message indicates a network or authentication issue.

```{image} /_static/img/ai-agent/cfg-ollama-settings.png
:alt: Settings → Integrations — Ollama configuration block
:width: 100%
```

### Network setup recommendations

| Scenario | Base URL |
|----------|----------|
| Ollama on the same machine as Odoo | `http://localhost:11434` |
| Ollama on a separate LAN host | `http://192.168.x.x:11434` |
| Ollama behind a reverse proxy with TLS | `https://ollama.example.com` |

```{warning}
Do **not** expose the Ollama port directly to the internet without authentication.
Use a reverse proxy with API key enforcement or restrict access at the firewall level.
```

---

## 2. Model Management

**Module:** `lu_ai_ollama`

### Viewing installed models

Go to **AI → Configuration → Ollama Models**. The list is populated
automatically by querying the Ollama server's `/api/tags` endpoint. Each row
shows the model name, size on disk, and last modified date.

Click **Refresh Models** to sync the list after pulling a new model in Ollama.

### Pulling models from the UI

1. In the model list, click **Pull Model**.
2. Enter the model tag (e.g., `qwen3.5:9b`).
3. Odoo calls Ollama's `/api/pull` endpoint in the background. Progress is
   shown in the chatter.

Alternatively, pull models directly on the host:

```bash
ollama pull qwen3.5:9b
ollama pull llama3.1:8b
```

Then click **Refresh Models** in Odoo to make them available.

### Model parameters

Each AI Agent can override the following Ollama parameters. Leave a field blank
to use the Ollama server default.

| Parameter | Default | Accepted range | Effect |
|-----------|---------|---------------|--------|
| `num_ctx` | 4096 | 512 – 128 000 | Context window in tokens. Higher values let the model see more conversation history and injected context. |
| `num_predict` | 512 | 1 – 4096 | Maximum tokens the model generates per response. |
| `keep_alive` | `5m` | `0` – unlimited | How long the model stays loaded in VRAM between requests. `0` unloads immediately; `-1` keeps it loaded indefinitely. |

```{warning}
Setting `num_ctx` above your GPU's available VRAM causes Ollama to fall back to
CPU inference or crash. A 9B model at `num_ctx=4096` needs ~6 GB VRAM; at
`num_ctx=32768` it needs ~14 GB. Start conservatively and increase as needed.
```

These parameters are set per agent at **AI → Agents → Agents → (open agent) →
Advanced** tab.

### Recommended models by use case

| Use case | Recommended model | Notes |
|----------|------------------|-------|
| General assistant / quick replies | `qwen3.5:9b` | Best balance of speed and quality for 8–12 GB VRAM |
| Complex analysis, multi-step tool calls | `qwen3.5:35b` | Requires 24+ GB VRAM |
| Coding and structured output | `llama3.1:8b` | Strong at JSON/function output |
| Korean language tasks | `qwen3.5:9b` | Good Korean support out of the box |
| Low-resource environments | `qwen3.5:3b` | Runs on 4 GB VRAM |

```{note}
The available model list in the agent form is populated automatically from the
Ollama server. If a model you just pulled is not visible, click **Refresh
Models**.
```

---

## 3. Claude Provider Settings

**Module:** `lu_ai_claude`

### Accessing the settings

Go to **Settings → AI** (Providers section). Find the
**"Use your own Anthropic Claude account"** block.

### Fields

| Field | Default | Description |
|-------|---------|-------------|
| **API Key** | *(empty)* | Your Anthropic API key. Stored encrypted in `ir.config_parameter`. Never logged in plain text. |
| **Max Output Tokens** | 16 384 | Per-request token cap. Actual limit is enforced by the model (see table below). |

```{warning}
Anthropic API keys are billed per token. Set **Max Output Tokens** conservatively
in production to avoid unexpectedly large charges on long conversations.
```

### Model selection

Select a model per agent at **AI → Agents → Agents → (open agent) → LLM Model**
dropdown. The list is populated from the Claude connector's built-in model
catalogue.

| Model | Context | Max output | Best for |
|-------|---------|-----------|---------|
| Claude Opus 4.6 | 200 000 | 128 000 | Highest capability, complex reasoning |
| Claude Sonnet 4.6 | 200 000 | 64 000 | Balanced — recommended for production |
| Claude Haiku 4.5 | 200 000 | 64 000 | Lowest cost, fastest response |

```{note}
Anthropic releases new model versions regularly. The dropdown in the agent form
always reflects the current catalogue — use it as the authoritative source rather
than the table above.
```

### Verifying your API key

There is no dedicated "Test Connection" button for the Claude provider. To
verify the key:

1. Save the Settings page.
2. Open any agent that uses a Claude model.
3. Start a new conversation and send a short message (e.g., `ping`).

A successful response confirms the key is valid. An error banner with
`"401 Unauthorized"` or `"Invalid API key"` indicates the key needs to be
regenerated at [console.anthropic.com](https://console.anthropic.com/).

```{image} /_static/img/ai-agent/cfg-claude-settings.png
:alt: Settings → AI — Claude provider configuration block
:width: 100%
```

---

## 4. AI Agent Configuration

**Module:** `lu_ai_orchestrator`

### Creating an agent

1. Go to **AI → Agents → Agents**.
2. Click **New**.
3. Fill in the fields described below.
4. Click **Save**.

### Agent fields

| Field | Description |
|-------|-------------|
| **Name** | Display name shown in the side panel agent selector. |
| **LLM Model** | Provider and model combination (e.g., `Ollama / qwen3.5:9b`). |
| **Temperature** | Randomness of responses. Range 0.0–2.0. Lower = more deterministic; higher = more creative. Default 0.7. |
| **Max Tokens** | Upper bound on response length for this agent. Overrides the provider-level default. |
| **Active** | Uncheck to hide the agent from the side panel without deleting it. |

### System prompt

The system prompt is the persistent instruction prepended to every conversation
with this agent. It defines the agent's role, tone, and constraints.

**Best practices:**

- State the agent's role in the first sentence:
  `"You are a Sales Assistant for Linkup Infotech's Odoo ERP system."`
- Specify the language if needed:
  `"Always respond in Korean unless the user writes in English."`
- Add output format constraints for tool-heavy agents:
  `"When presenting tabular data, always use a Markdown table."`
- Keep it under 500 tokens. Longer prompts increase latency and cost without
  proportional benefit.

```{tip}
Test your system prompt with a few representative questions before deploying to
users. The side panel shows the exact model output, making iteration fast.
```

### Context injection

Domain-specific Odoo record fields are automatically injected into the
conversation context at query time (e.g., the current Sales Order when the
user asks from the Sales module). For details on which fields are injected per
domain and how to customise routing, see [Domain Routing](domain-routing.md).

```{image} /_static/img/ai-agent/cfg-agent-form.png
:alt: AI Agent form — General tab
:width: 100%
```

---

## 5. Document Retrieval (RAG)

**Module:** `lu_ai_rag`

RAG (Retrieval-Augmented Generation) attaches relevant documents to the prompt
at query time, letting the agent answer questions about your company's internal
knowledge base without retraining the model.

### How it works

1. Documents are chunked and embedded into a vector index when a knowledge
   source is attached to an agent.
2. At query time, the user's message is embedded and the top-N most similar
   chunks are retrieved.
3. The retrieved chunks are injected into the prompt before the LLM generates a
   response.

### Accessing knowledge source settings

Go to **AI → Configuration → Knowledge Sources**.

### Supported source types

| Type | Description |
|------|-------------|
| **Odoo Attachments** | PDF, DOCX, TXT files attached to any Odoo record. |
| **External URL** | Publicly accessible URL (HTML page or plain text). Fetched and indexed at setup time. |

### Embedding model selection

Go to **Settings → AI → Embedding Model**. Supported options:

| Option | Provider | Notes |
|--------|----------|-------|
| `nomic-embed-text` | Ollama (local) | Free, runs on CPU, ~270 MB |
| `mxbai-embed-large` | Ollama (local) | Higher accuracy, ~670 MB |
| `text-embedding-3-small` | OpenAI | Requires OpenAI API key |

```{note}
For fully on-premise deployments, use an Ollama embedding model. The local
options produce comparable retrieval quality to cloud models for most business
document types.
```

### Attaching a knowledge source to an agent

1. Open the agent form (**AI → Agents → Agents → (open agent)**).
2. Go to the **Knowledge** tab.
3. Click **Add a line** and select an existing knowledge source, or click
   **Create and edit** to define a new one.
4. Save the agent. The knowledge source index is built automatically in the
   background (progress visible in the chatter).

### When to use RAG vs. system prompt

| Use case | Recommendation |
|----------|---------------|
| Static instructions, persona, output format | System prompt |
| Company policies, product catalogues, FAQs (updated periodically) | RAG knowledge source |
| Real-time ERP data (orders, inventory, HR records) | Domain context injection (see [Domain Routing](domain-routing.md)) |

```{tip}
RAG is most effective when documents are well-structured (clear headings,
consistent terminology). Scanned PDFs without OCR produce poor retrieval quality.
```

---

## 6. Security & Access Control

### User groups

Linkup AI Agent defines the following security groups. Assign them at
**Settings → Users & Companies → Users → (open user) → Access Rights**.

| Group | Access |
|-------|--------|
| **AI User** | Can use the side panel chat. Cannot create or modify agents. |
| **AI Manager** | Can create, edit, and delete agents and knowledge sources. Can view usage logs. |
| **AI Admin** | Full access including provider settings, API key management, and audit logs. |

```{warning}
The **AI Admin** group grants access to API keys stored in `ir.config_parameter`.
Assign it only to system administrators.
```

### Restricting an agent to specific users

1. Open the agent form.
2. In the **Allowed Groups** field, select one or more security groups.
3. Save. The agent is now visible only to users in those groups.

If **Allowed Groups** is left empty, the agent is accessible to all users with
at least the **AI User** group.

### API key storage

Provider API keys (Anthropic, OpenAI) are stored as encrypted values in Odoo's
`ir.config_parameter` table. They are never written to server logs or returned
in API responses.

```{warning}
Do not hard-code API keys in system prompts or agent names — these fields are
visible to **AI User** level accounts and may appear in exported logs.
```

---

## 7. Multi-Model Setup

Running multiple agents with different providers lets you optimise for cost,
latency, and capability simultaneously.

### Example: Ollama for Sales, Claude for Finance

| Agent | Provider | Model | Rationale |
|-------|----------|-------|-----------|
| Sales Assistant | Ollama | `qwen3.5:9b` | Fast, free, handles routine queries |
| Finance Analyst | Claude | `claude-sonnet-4-6` | Complex reasoning over large reports |
| HR Helper | Ollama | `qwen3.5:9b` | Sensitive data stays on-premise |

To configure this:

1. Ensure both `lu_ai_ollama` and `lu_ai_claude` are installed.
2. Configure both providers as described in sections 1–3 above.
3. Create a separate agent for each use case and select the appropriate model.

### Switching an agent's provider

Open the agent form and change the **LLM Model** dropdown. The change takes
effect immediately — existing conversations are not affected.

```{note}
Fallback behaviour (e.g., automatically switching from Ollama to Claude when
the local server is unavailable) and cross-domain routing logic are covered in
[Domain Routing](domain-routing.md).
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Connection refused" on Test Connection | Ollama not running or wrong port | Run `ollama serve`; verify Base URL |
| Model list is empty after enabling Ollama | Ollama running but no models pulled | Run `ollama pull <model>`, then **Refresh Models** |
| `num_ctx` increase causes slow responses | Model reloaded with larger context | Expected — first request after change reloads the model into VRAM |
| "OOM" error or Ollama crashes | `num_ctx` exceeds available VRAM | Reduce `num_ctx` or use a smaller model |
| "401 Unauthorized" (Claude) | Invalid or expired API key | Regenerate key at console.anthropic.com |
| "429 Too Many Requests" (Claude) | Rate limit or quota exceeded | Check usage limits at console.anthropic.com |
| RAG returns irrelevant chunks | Poor document structure or wrong embedding model | Re-index after improving document formatting; try a different embedding model |
| Agent not visible in side panel | Agent marked inactive or group restriction | Check **Active** checkbox and **Allowed Groups** on the agent form |
