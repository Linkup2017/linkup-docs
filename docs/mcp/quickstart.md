# Quick Start

Connect Claude Desktop or claude.ai to your Odoo instance in under 10 minutes.

Linkup MCP Server embeds a [Model Context Protocol](https://modelcontextprotocol.io)
(MCP 2025-03-26 Streamable HTTP) server directly inside Odoo 19. Once connected,
AI clients can read and write Odoo data — create tasks, search contacts, manage tickets,
log time — without any external middleware.

---

## Prerequisites

Odoo 19.0
: A running instance with administrator access and HTTPS enabled.

Linkup MCP Server (`lu_mcp_server`)
: The core module must be installed first. Plugin modules are optional but required for
  specific tool sets (e.g. `lu_mcp_knowledge` for Knowledge tools).

AI client
: Claude Desktop (any version) **or** a claude.ai account with MCP support.

:::{tip}
Claude Desktop uses a static API key and does **not** require OAuth.  
claude.ai uses OAuth 2.0 PKCE (the browser-based flow described in Step 3).
:::

---

## Step 1 — Install the Modules

1. Go to the **Apps** menu in your Odoo instance.
2. Search for **"Linkup MCP"**.
3. Install **Linkup MCP Server** (`lu_mcp_server`) first — this is the only mandatory module.
4. Install the plugin modules for the Odoo apps you want to expose:

   | Module | Odoo App | Tools |
   |---|---|---|
   | `lu_mcp_knowledge` | Knowledge | 9 |
   | `lu_mcp_project` | Project | 7 |
   | `lu_mcp_helpdesk` | Helpdesk | 12 |
   | `lu_mcp_crm` | CRM | 8 |
   | `lu_mcp_contact` | Contacts | 6 |
   | `lu_mcp_calendar` | Calendar | 5 |
   | `lu_mcp_sale` | Sales | 6 |
   | `lu_mcp_purchase` | Purchase | 6 |
   | `lu_mcp_timesheet` | Timesheets | 6 |
   | `lu_mcp_survey` | Surveys | 6 |

:::{note}
Each plugin module is independently installable. Only install modules for Odoo apps that
are already installed in your instance. `lu_mcp_server` is the only required dependency.
:::

---

## Step 2 — Connect Claude Desktop

Claude Desktop connects using a static Bearer token (no browser OAuth required).

**2a. Generate an API key**

1. In Odoo, go to **Settings → Technical → API Keys** (developer mode must be enabled).
2. Click **New**, set a description (e.g. `Claude Desktop MCP`), and save.
3. Copy the generated key — it will not be shown again.

**2b. Edit your Claude Desktop config**

Open `claude_desktop_config.json` (location varies by OS):

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add an entry under `mcpServers`:

```json
{
  "mcpServers": {
    "linkup-odoo": {
      "url": "https://<your-odoo-host>/mcp/message",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

Replace `<your-odoo-host>` with your Odoo domain (e.g. `odoo.example.com`) and
`<your-api-key>` with the key generated in Step 2a.

**2c. Restart Claude Desktop**

Restart the app. In a new conversation, you should see the Linkup tools appear in the
tool picker. Test with a simple prompt:

> *"List all Knowledge workspaces in Odoo."*

---

## Step 3 — Connect claude.ai (OAuth 2.0)

claude.ai uses OAuth 2.0 PKCE with dynamic client registration. The flow runs entirely
in the browser — no config files to edit.

1. In claude.ai, go to **Settings → Integrations → Add Integration**.
2. Enter the MCP endpoint URL:
   ```
   https://<your-odoo-host>/mcp/message
   ```
3. Click **Connect**. Your browser opens the Odoo OAuth consent page.
4. Log in with your Odoo credentials (if not already logged in).
5. Review the requested permissions and click **Authorize**.
6. You are redirected back to claude.ai. The integration status should show **Connected**.

:::{tip}
The OAuth access token is valid for **90 days**. After expiry, repeat this step to
re-authorize. No config files or API keys are needed for claude.ai.
:::

---

## Step 4 — First Tool Calls

Try these example prompts to verify the connection:

**List Knowledge workspaces**
> *"Show me all workspace articles in Odoo Knowledge."*

**Search for a contact**
> *"Find the contact record for Acme Corp in Odoo."*

**Create a project task**
> *"Create a task called 'Review Q2 budget' in the Finance project and assign it to me."*

**Check open helpdesk tickets**
> *"Show me all open helpdesk tickets assigned to me, sorted by priority."*

**Log time on a task**
> *"Log 2 hours on task #42 with the note 'Initial investigation'."*

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No tools appear in Claude Desktop | Wrong endpoint URL or invalid Bearer token | Double-check the `url` and `Authorization` header in `claude_desktop_config.json`; confirm the module is installed |
| `401 Unauthorized` | API key not found or expired | Regenerate the API key in **Settings → Technical → API Keys** |
| OAuth redirect fails (blank page or error) | Odoo not accessible over HTTPS from browser | MCP Server requires HTTPS; confirm your instance has a valid TLS certificate |
| `403 Forbidden` on a specific tool | Odoo user lacks access to the underlying model | Grant the user the appropriate Odoo group (e.g. Project User for project tools) |
| Tools listed but return empty results | Plugin module installed but no data or wrong company | Check that you are in the correct Odoo company and the app has existing records |
| `lu_mcp_website` conflicts on install | `website` module detected, bridge not installed | Install `lu_mcp_server_website` to resolve the conflict |

:::{note}
All MCP requests are logged in the Odoo audit log. Go to
**Settings → Technical → MCP → Audit Log** to inspect request history.
:::
