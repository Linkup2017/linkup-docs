# Authentication

Linkup MCP Server supports two authentication methods depending on your AI client.

| Client | Method | Token lifetime |
|---|---|---|
| Claude Desktop | Static Bearer token (Odoo API key) | Never expires |
| claude.ai | OAuth 2.0 PKCE + dynamic client registration | 90 days |
| Any MCP client | Bearer token in `Authorization` header | Depends on method |

---

## Bearer Token (API Key)

The simplest method. Generate an Odoo API key and include it in every request.

**Generate a key**

1. Enable developer mode (**Settings → Activate the developer mode**).
2. Go to **Settings → Technical → API Keys**.
3. Click **New**, enter a description, and save. Copy the key — it is shown only once.

**Use the key**

Include the key in the `Authorization` request header:

```http
POST /mcp/message HTTP/1.1
Host: odoo.example.com
Authorization: Bearer <api-key>
Content-Type: application/json
```

In Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkup-odoo": {
      "url": "https://odoo.example.com/mcp/message",
      "headers": {
        "Authorization": "Bearer <api-key>"
      }
    }
  }
}
```

---

## OAuth 2.0 PKCE (claude.ai)

For browser-based AI clients, Linkup MCP Server implements the full OAuth 2.0 Authorization
Code flow with PKCE (Proof Key for Code Exchange) and dynamic client registration, as
required by the MCP 2025-03-26 specification.

### Discovery

The server publishes its OAuth metadata at the standard well-known URL:

```
GET /.well-known/oauth-authorization-server
```

Response example:

```json
{
  "issuer": "https://odoo.example.com",
  "authorization_endpoint": "https://odoo.example.com/oauth/authorize",
  "token_endpoint": "https://odoo.example.com/oauth/token",
  "registration_endpoint": "https://odoo.example.com/oauth/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code"],
  "code_challenge_methods_supported": ["S256"]
}
```

### Flow Overview

```{mermaid}
sequenceDiagram
    participant C as AI Client (claude.ai)
    participant O as Odoo MCP Server
    participant U as User (browser)

    C->>O: GET /.well-known/oauth-authorization-server
    O-->>C: OAuth metadata (endpoints)

    C->>O: POST /oauth/register (dynamic client registration)
    O-->>C: client_id + client_secret

    C->>U: Redirect to /oauth/authorize?code_challenge=...
    U->>O: GET /oauth/authorize (opens consent page)
    U->>O: User approves → POST consent
    O-->>U: Redirect to client with ?code=...

    C->>O: POST /oauth/token (code + code_verifier)
    O-->>C: access_token (Bearer, 90-day TTL)

    C->>O: POST /mcp/message (Authorization: Bearer <token>)
    O-->>C: MCP tool result
```

### Dynamic Client Registration

Clients that do not have a pre-registered `client_id` must register dynamically before
initiating the authorization flow.

**Request**

```http
POST /oauth/register HTTP/1.1
Content-Type: application/json

{
  "client_name": "claude.ai",
  "redirect_uris": ["https://claude.ai/oauth/callback"],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "client_secret_post"
}
```

**Response**

```json
{
  "client_id": "mcp_client_abc123",
  "client_secret": "s3cr3t...",
  "client_name": "claude.ai",
  "redirect_uris": ["https://claude.ai/oauth/callback"],
  "grant_types": ["authorization_code"]
}
```

:::{note}
Dynamic client registration is enabled by default. Restrict it to administrators only
in production by setting the **MCP → Registration policy** option in Odoo Settings.
:::

### Authorization Request

The client redirects the user to the authorization endpoint with a PKCE challenge:

```
GET /oauth/authorize
  ?response_type=code
  &client_id=mcp_client_abc123
  &redirect_uri=https://claude.ai/oauth/callback
  &code_challenge=<base64url(SHA-256(code_verifier))>
  &code_challenge_method=S256
  &state=<random-state>
```

The user sees the Odoo consent page and logs in if needed. After approval, Odoo redirects
to `redirect_uri` with `?code=<auth-code>&state=<state>`.

### Token Exchange

```http
POST /oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=<auth-code>
&redirect_uri=https://claude.ai/oauth/callback
&client_id=mcp_client_abc123
&client_secret=s3cr3t...
&code_verifier=<original-code-verifier>
```

**Response**

```json
{
  "access_token": "odoo_mcp_tok_...",
  "token_type": "Bearer",
  "expires_in": 7776000
}
```

The access token is valid for **90 days** (7 776 000 seconds).

---

## Session Tracking

Every MCP connection creates a server-sent events (SSE) session. The server tracks:

- Session ID (random UUID, returned in the `Mcp-Session-Id` response header)
- Authenticated user
- Connection start time
- Last activity timestamp

Sessions are accessible in Odoo at **Settings → Technical → MCP → Sessions**.

On reconnect, clients may include the `Mcp-Session-Id` header to replay missed events
via the SSE endpoint:

```http
GET /mcp/sse HTTP/1.1
Mcp-Session-Id: <session-id>
Authorization: Bearer <token>
```

---

## Audit Log

All tool calls are written to the MCP audit log regardless of success or failure.

**View the log**: **Settings → Technical → MCP → Audit Log**

Each entry records:

- Timestamp
- Authenticated user
- Tool name (e.g. `knowledge_read_article`)
- Input parameters (JSON)
- Response status
- Duration (ms)

The audit log cannot be deleted by regular users. It is retained for the period configured
under **Settings → Technical → MCP → Log Retention**.

---

## Security Best Practices

**Require HTTPS**
: The MCP endpoint must be served over HTTPS. Odoo will not start the MCP server on plain
  HTTP in production mode. Use a reverse proxy (nginx, Caddy) with a valid TLS certificate.

**Restrict client registration**
: In production, set the registration policy to **Admin only** so arbitrary clients cannot
  register without authorization. This prevents unauthorized tools from being listed.

**Rotate API keys regularly**
: For Claude Desktop connections (Bearer token), rotate the Odoo API key every 90 days or
  whenever team membership changes. Revoke old keys in **Settings → Technical → API Keys**.

**Scope access by Odoo user**
: The Bearer token (or OAuth token) authenticates as a specific Odoo user. Tools only
  expose data that the authenticated user can access via normal Odoo record rules and
  access rights. Create a dedicated *MCP Service User* with only the necessary groups
  rather than using an administrator account.

**Monitor the audit log**
: Review the audit log periodically for unexpected tool calls or high-volume requests that
  may indicate misuse.
