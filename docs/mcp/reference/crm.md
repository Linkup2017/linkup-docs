# CRM (`lu_mcp_crm`)

**8 tools** for Odoo CRM lead and opportunity management.

Requires: `lu_mcp_server`, Odoo `crm` app.

---

## Overview

These tools cover the CRM pipeline: browse stages, search leads and opportunities,
view the pipeline summary table, read full record details, create and update leads,
convert a lead to an opportunity, and post internal notes.

---

## Tools

### `crm_list_stages`

List all CRM pipeline stages in sequence order.

| Parameter | Type | Required | Description |
|---|---|---|---|
| *(none)* | | | |

**Example prompt**
> *"What are the CRM pipeline stages?"*

---

### `crm_list_pipeline`

Show the CRM pipeline as a summary table grouped by stage (count + expected revenue per
stage). Use `crm_search_leads` to get individual records.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | integer | No | Filter by salesperson. |
| `stage_id` | integer | No | Filter to a specific stage. |

Returns a Markdown table:

```
| Stage | Count | Expected Revenue |
|-------|------:|-----------------:|
| New   |     4 |         $12,000  |
| Qualified | 2 |         $35,000  |
```

**Example prompt**
> *"Give me a summary of the CRM pipeline for salesperson #5."*

---

### `crm_search_leads`

Search CRM leads and opportunities as individual records.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Keyword search in name or description. |
| `type` | string | No | `'lead'` or `'opportunity'`. |
| `stage_id` | integer | No | Filter by stage. |
| `user_id` | integer | No | Filter by salesperson. |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Find all opportunities in the 'Proposal' stage."*

---

### `crm_read_lead`

Get full details of a CRM lead or opportunity.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Lead or opportunity ID. |

**Example prompt**
> *"Show me the details for lead #88."*

---

### `crm_create_lead`

Create a new CRM lead.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Lead title. |
| `partner_id` | integer | No | Customer partner ID. |
| `type` | string | No | `'lead'` (default) or `'opportunity'`. |
| `stage_id` | integer | No | Initial pipeline stage. |
| `user_id` | integer | No | Salesperson user ID. |
| `expected_revenue` | number | No | Expected revenue amount. |
| `description` | string | No | Lead description (Markdown). |

**Example prompt**
> *"Create an opportunity titled 'Enterprise contract — Acme Corp' with expected revenue $50,000, assigned to salesperson #3."*

---

### `crm_update_lead`

Update an existing lead or opportunity.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Lead/opportunity ID. |
| `stage_id` | integer | No | New stage. |
| `user_id` | integer | No | New salesperson. |
| `probability` | number | No | Win probability (0–100). |
| `expected_revenue` | number | No | Updated expected revenue. |
| `date_deadline` | string | No | New deadline (`YYYY-MM-DD`). |
| `description` | string | No | New description (Markdown). |

**Example prompt**
> *"Update lead #88 — move to 'Won' stage and set probability to 100."*

---

### `crm_convert_to_opportunity`

Convert a lead into an opportunity. Sets the type to `opportunity` and optionally
links a customer partner.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Lead ID to convert. |
| `partner_id` | integer | No | Customer partner ID to link. |

**Example prompt**
> *"Convert lead #88 to an opportunity and link it to partner #15 (Acme Corp)."*

:::{note}
If the lead is already an opportunity, the tool returns a message indicating no
action was taken.
:::

---

### `crm_log_note`

Post an internal note on a lead or opportunity (not visible to the customer).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Lead/opportunity ID. |
| `body` | string | Yes | Note body (Markdown). |

**Example prompt**
> *"Add an internal note to opportunity #88: 'Called the procurement lead — decision expected by end of month.'"*
