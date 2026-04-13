# Architecture

## System Overview

Linkup MCP Server is a set of Odoo 19 modules that embed a full
[Model Context Protocol](https://modelcontextprotocol.io) (MCP 2025-03-26 Streamable HTTP)
server directly into Odoo's HTTP stack. No external middleware, proxy, or sidecar process
is required.

```{mermaid}
flowchart TD
    subgraph Clients
        CD[Claude Desktop]
        CAI[claude.ai]
        MCP[Any MCP Client]
    end

    subgraph "Odoo 19 (WSGI)"
        EP["POST /mcp/message\n(Bearer auth)"]
        CTRL[MCPController]
        AUTH[ir.http Bearer auth]
        PLUGIN[lu.mcp.plugin\nRegistry]

        subgraph "Plugin Modules"
            PK[lu.mcp.plugin.knowledge]
            PP[lu.mcp.plugin.project]
            PH[lu.mcp.plugin.helpdesk]
            PC[lu.mcp.plugin.crm]
            PO[lu.mcp.plugin.contact]
            PE[lu.mcp.plugin.calendar]
            PS[lu.mcp.plugin.sale]
            PU[lu.mcp.plugin.purchase]
            PT[lu.mcp.plugin.timesheet]
            PV[lu.mcp.plugin.survey]
        end

        ORM[Odoo ORM / Database]
        AUDIT[MCP Audit Log]
    end

    CD -->|Bearer token| EP
    CAI -->|OAuth 2.0 Bearer| EP
    MCP -->|Bearer token| EP

    EP --> AUTH
    AUTH --> CTRL
    CTRL -->|_dispatch_tool| PLUGIN
    PLUGIN -->|execute_tool| PK & PP & PH & PC & PO & PE & PS & PU & PT & PV
    PK & PP & PH & PC & PO & PE & PS & PU & PT & PV --> ORM
    CTRL --> AUDIT
```

---

## Request Lifecycle

A single MCP tool call follows this path:

1. **Transport**: Client sends `POST /mcp/message` with a JSON-RPC 2.0 body and an
   `Authorization: Bearer <token>` header.

2. **Auth**: Odoo's built-in `ir.http` bearer auth validates the token against
   `res.users.apikeys` (API key) or the OAuth token table. The Odoo environment
   (`request.env.user`) is set to the authenticated user before the controller runs.

3. **Session**: `MCPController` reads the `mcp-session-id` request header. On
   `initialize`, a new UUID4 session is created and returned. Subsequent calls must
   include the session ID.

4. **Dispatch**: The controller calls `lu.mcp.plugin._dispatch_tool(tool_name, params)`.
   Longest-prefix matching finds the correct plugin namespace (e.g. `knowledge` for
   `knowledge_search_articles`).

5. **Execution**: The plugin's `execute_tool()` method dispatches to `_<local_name>(params)`
   (e.g. `_search_articles`). All tool methods run within a normal Odoo transaction with
   the authenticated user's access rights.

6. **Result**: The tool returns a Markdown string. The controller wraps it in a JSON-RPC
   2.0 response and writes an audit log entry.

7. **Response**: The response is sent as `Content-Type: application/json` with the
   `mcp-session-id` header included.

---

## Plugin Registry

The plugin registry uses Odoo's model inheritance to auto-discover plugins at server
startup — no registration calls or config files are needed.

### Defining a Plugin

Every plugin module inherits `lu.mcp.plugin` and sets `_mcp_namespace`:

```python
class MCPKnowledgePlugin(models.AbstractModel):
    _name = 'lu.mcp.plugin.knowledge'
    _inherit = 'lu.mcp.plugin'
    _description = 'MCP Knowledge Plugin'
    _mcp_namespace = 'knowledge'

    def _get_tools(self) -> list[dict]:
        return [
            {
                'name': 'search_articles',           # local name
                'description': '...',
                'inputSchema': {...},
            },
        ]

    def _search_articles(self, params: dict) -> str:
        # implementation
        ...
```

### Auto-Discovery

On first request after module load, `_get_namespace_map()` scans the Odoo model registry
for any model that has a non-empty `_mcp_namespace` attribute. The result is cached on
the registry object and lives for the same lifetime as a module install cycle.

Installing a new plugin module and restarting Odoo is sufficient for its tools to appear
in `tools/list` responses — no additional wiring required.

### Tool Naming

Tool names are automatically prefixed with the namespace using an underscore separator,
producing the final MCP tool name:

```
{namespace}_{local_name}
```

Examples: `knowledge_search_articles`, `project_create_task`, `helpdesk_ticket_reply`.

All tool names comply with the MCP name pattern `^[a-zA-Z0-9_-]{1,64}$`.

### Dispatch

`_dispatch_tool()` splits the tool name using longest-prefix matching. This prevents
a short namespace (e.g. `sale`) from accidentally capturing tools belonging to a longer
one (e.g. `sale_subscription`, if added in the future).

```python
# 'crm_convert_to_opportunity'
#  → namespace 'crm', local tool 'convert_to_opportunity'
#  → self.env['lu.mcp.plugin.crm'].execute_tool('convert_to_opportunity', params)
```

---

## Module Dependency Tree

```{mermaid}
graph TD
    BASE[base + web]
    CORE[lu_mcp_server]
    WEBSITE[lu_mcp_server_website]

    BASE --> CORE

    CORE --> K[lu_mcp_knowledge]
    CORE --> PR[lu_mcp_project]
    CORE --> H[lu_mcp_helpdesk]
    CORE --> CR[lu_mcp_crm]
    CORE --> CO[lu_mcp_contact]
    CORE --> CA[lu_mcp_calendar]
    CORE --> SA[lu_mcp_sale]
    CORE --> PU[lu_mcp_purchase]
    CORE --> T[lu_mcp_timesheet]
    CORE --> SV[lu_mcp_survey]
    CORE --> WEBSITE

    K -->|knowledge module| KN[knowledge]
    PR -->|project module| PJ[project]
    H -->|helpdesk module| HD[helpdesk]
    CR -->|crm module| CRM[crm]
    CO -->|contacts module| CNT[contacts]
    CA -->|calendar module| CAL[calendar]
    SA -->|sales module| SO[sale]
    PU -->|purchase module| PO[purchase]
    T -->|timesheets module| TS[hr_timesheet]
    SV -->|surveys module| SUR[survey]
    WEBSITE -->|website module| WEB[website]
```

`lu_mcp_server` depends only on `base` and `web`. Each plugin module adds a dependency
on the corresponding Odoo app. `lu_mcp_server_website` is a thin bridge module that
auto-installs when `website` is present, resolving controller routing conflicts.

---

## HTML ↔ Markdown Conversion

All plugins that accept or return rich text use shared utilities from
`lu_mcp_server.utils.convert`:

- `md_to_html(markdown: str) → str` — converts Markdown input from the AI client to
  Odoo-compatible HTML before writing to the database.
- `html_to_md(html: str) → str` — converts Odoo HTML field values to Markdown before
  returning them to the AI client.

This ensures that tool descriptions, notes, and article bodies are presented to the LLM
as clean Markdown rather than raw HTML.

---

## Shared Chatter Utility

Tools that post internal notes on Odoo records (e.g. `contact_log_note`,
`helpdesk_ticket_reply`) use `lu_mcp_server.utils.chatter.post_internal_note(record, body)`.
This utility converts the Markdown body to HTML and calls `record.message_post()` with
`subtype_xmlid='mail.mt_note'`, ensuring the note is internal (not sent to customers).

---

## MCP Protocol Implementation

| Feature | Implementation |
|---|---|
| Transport | Streamable HTTP (MCP 2025-03-26) |
| Encoding | JSON-RPC 2.0 over HTTP POST |
| Auth | Bearer token via Odoo `ir.http` |
| OAuth | PKCE + dynamic client registration |
| SSE replay | `GET /mcp/sse` with `mcp-session-id` header |
| CORS | `cors='*'` on the route (Odoo handles OPTIONS preflight) |
| Session | UUID4 per `initialize`, tracked in `lu.mcp.session` |
| Audit | Every call → `lu.mcp.audit.log` entry |
| Tool naming | `^[a-zA-Z0-9_-]{1,64}$`, underscore namespace separator |
