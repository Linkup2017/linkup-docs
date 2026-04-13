# Helpdesk (`lu_mcp_helpdesk`)

**12 tools** for the full Odoo Helpdesk ticket lifecycle.

Requires: `lu_mcp_server`, Odoo `helpdesk` app.

---

## Overview

These tools cover everything from ticket creation to closure: list teams and stages,
search and read tickets, create and update tickets, reply (public or internal), escalate,
close, check SLA status, view customer history, and link Knowledge articles.

**Priority values**: `'0'` = Low, `'1'` = Medium, `'2'` = High, `'3'` = Urgent.

---

## Tools

### `helpdesk_list_teams`

List all helpdesk teams with open/unassigned/urgent ticket counts and SLA success rate.

| Parameter | Type | Required | Description |
|---|---|---|---|
| *(none)* | | | |

**Example prompt**
> *"Show all helpdesk teams and how many open tickets each has."*

---

### `helpdesk_list_stages`

List helpdesk ticket stages, optionally filtered to a team.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `team_id` | integer | No | Filter stages to a specific team. Omit for all stages. |

**Example prompt**
> *"What stages does the Support team (id=2) use?"*

---

### `helpdesk_search_tickets`

Search tickets with multiple filters.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Keyword search in ticket name or description. |
| `team_id` | integer | No | Filter by team. |
| `stage_id` | integer | No | Filter by stage. |
| `assignee_id` | integer | No | Filter by assignee (user ID). |
| `partner_id` | integer | No | Filter by customer partner. |
| `priority` | string | No | `'0'` Low, `'1'` Medium, `'2'` High, `'3'` Urgent. |
| `sla_failed` | boolean | No | If `true`, return only SLA-failed tickets. |
| `include_closed` | boolean | No | If `true`, include tickets in closed (folded) stages. Default `false`. |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Show me all urgent tickets in the Support team that have failed their SLA."*

---

### `helpdesk_read_ticket`

Get full details of a ticket: team, stage, priority, assignee, customer, SLA status,
timing metrics, and description.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Ticket ID. |

**Example prompt**
> *"Show me all details for ticket #305."*

---

### `helpdesk_create_ticket`

Create a new helpdesk ticket.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Ticket subject. |
| `team_id` | integer | No | Team to assign the ticket to. |
| `description` | string | No | Ticket description (Markdown). |
| `partner_id` | integer | No | Customer partner ID (links to existing contact). |
| `partner_email` | string | No | Customer email (used if `partner_id` not provided). |
| `partner_name` | string | No | Customer name (used if `partner_id` not provided). |
| `priority` | string | No | `'0'`–`'3'` (default `'0'` Low). |
| `assignee_id` | integer | No | User ID of the agent to assign. |
| `tag_ids` | array of integer | No | Tag IDs to apply. |

**Example prompt**
> *"Create a high-priority helpdesk ticket titled 'Login broken for user jsmith@acme.com' in the IT Support team."*

---

### `helpdesk_update_ticket`

Update an existing ticket's fields.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Ticket ID to update. |
| `name` | string | No | New subject. |
| `description` | string | No | New description (Markdown). |
| `stage_id` | integer | No | Move to a different stage. |
| `team_id` | integer | No | Move to a different team. |
| `assignee_id` | integer | No | Reassign to a different agent. |
| `priority` | string | No | New priority (`'0'`–`'3'`). |
| `tag_ids` | array of integer | No | Replace tag set (pass empty array to clear). |
| `kanban_state` | string | No | `normal`, `done`, or `blocked`. |

**Example prompt**
> *"Reassign ticket #305 to user #7 and set priority to Urgent."*

---

### `helpdesk_ticket_reply`

Post a reply or internal note on a ticket.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Ticket ID. |
| `body` | string | Yes | Reply body (Markdown). |
| `internal` | boolean | No | If `true`, post as internal note (not visible to customer). Default `false`. |

**Example prompt — customer reply**
> *"Reply to ticket #305: 'We have identified the issue and will deploy a fix by EOD tomorrow.'"*

**Example prompt — internal note**
> *"Add an internal note to ticket #305: 'Root cause was a misconfigured nginx rule on server A.'"*

---

### `helpdesk_ticket_close`

Close a ticket by moving it to the first closed (folded) stage. Optionally posts a
resolution message.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Ticket ID. |
| `body` | string | No | Resolution summary to post as a customer message (Markdown). |

**Example prompt**
> *"Close ticket #305 with the message: 'Issue resolved. The fix has been deployed.'"*

---

### `helpdesk_ticket_escalate`

Raise the priority of a ticket by one level and optionally reassign it.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Ticket ID. |
| `priority` | string | No | Target priority (`'0'`–`'3'`). If omitted, increments by one (max `'3'` Urgent). |
| `team_id` | integer | No | Move to escalation team. |
| `assignee_id` | integer | No | Assign to escalation agent. |

**Example prompt**
> *"Escalate ticket #305 to the Tier 2 team (id=4) and assign to agent #9."*

---

### `helpdesk_get_sla_status`

Get SLA policies for a team, or detailed SLA compliance status for a specific ticket.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `team_id` | integer | No | List SLA policies for this team. |
| `ticket_id` | integer | No | Get per-policy SLA status for a specific ticket. |

Pass either `team_id` (to see configured policies) or `ticket_id` (to see compliance).

**Example prompt**
> *"What is the SLA status for ticket #305?"*

---

### `helpdesk_customer_history`

Get ticket history and satisfaction ratings for a customer.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `partner_id` | integer | No | Customer partner ID. At least one of `partner_id` or `email` required. |
| `email` | string | No | Customer email address. |
| `limit` | integer | No | Maximum tickets to return (default 20, max 80). |

**Example prompt**
> *"Show the helpdesk history for customer john@acme.com."*

---

### `helpdesk_link_knowledge_article`

Link a Knowledge article to a ticket by appending its URL to the ticket description.

Requires: Odoo `knowledge` app installed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ticket_id` | integer | Yes | Helpdesk ticket ID. |
| `article_id` | integer | Yes | Knowledge article ID to link. |

**Example prompt**
> *"Link Knowledge article #77 (Troubleshooting Guide) to ticket #305."*

:::{note}
This tool is only registered when the `knowledge` Odoo app is installed.
:::
