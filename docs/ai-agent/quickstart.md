# Quick Start

Get an AI assistant running in your Odoo instance in under 10 minutes.

## Prerequisites

- Odoo 17.0 or 18.0
- [Ollama](https://ollama.com) installed on your server (or accessible via network)
- At least one LLM model pulled (e.g., `ollama pull llama3.2`)

## Step 1: Install Modules

Install the following modules from the Odoo Apps Store:

1. **Link-Up AI Ollama** (`lu_ai_ollama`)
2. **Link-Up AI Orchestrator** (`lu_ai_orchestrator`)
3. **Link-Up AI UI** (`lu_ai_ui`)

```{tip}
Install `lu_ai_ollama` first — the other modules depend on it.
```

## Step 2: Configure Ollama Connection

1. Go to **Settings → Link-Up AI → Ollama Configuration**
2. Set the **Ollama URL** (default: `http://localhost:11434`)
3. Click **Test Connection** to verify

## Step 3: Select a Model

1. Go to **Settings → Link-Up AI → Models**
2. Click **Sync Models** to fetch available models from Ollama
3. Select your default model (recommended: `llama3.2` or `mistral`)

## Step 4: Start Chatting

Open any Odoo view and click the **AI Assistant** icon in the top-right corner.
Type your first message — the assistant is ready!

```{note}
Content for this page is a placeholder. Full content will be written in W3.
```
