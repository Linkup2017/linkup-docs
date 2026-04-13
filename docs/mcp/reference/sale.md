# Sales (`lu_mcp_sale`)

**6 tools** for Odoo sales quotations and orders.

Requires: `lu_mcp_server`, Odoo `sale` app.

---

## Overview

These tools cover the sales order lifecycle: search, read, create, update, confirm,
and log notes. Quotations (state `draft` or `sent`) can be edited; confirmed orders
(state `sale`) are locked for editing in Odoo.

**Order states**: `draft` (Quotation), `sent` (Quotation Sent), `sale` (Sales Order),
`done` (Locked), `cancel` (Cancelled).

---

## Tools

### `sale_search_orders`

Search sales quotations and orders.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Keyword search in order name or customer name. |
| `state` | string | No | Filter by state: `draft`, `sent`, `sale`, `done`, `cancel`. |
| `partner_id` | integer | No | Filter by customer. |
| `user_id` | integer | No | Filter by salesperson. |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Show all confirmed sales orders for customer #10."*

---

### `sale_read_order`

Get full details of a sales quotation or order, including order lines.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Sale order ID. |

**Example prompt**
> *"Show me the details of sales order #55."*

---

### `sale_create_order`

Create a new sales quotation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `partner_id` | integer | Yes | Customer partner ID. |
| `validity_date` | string | No | Quotation expiry date (`YYYY-MM-DD`). |
| `note` | string | No | Internal note (Markdown). |
| `order_line` | array | No | List of order lines (see below). |

**`order_line` items**

| Field | Type | Required | Description |
|---|---|---|---|
| `product_id` | integer | Yes | Product ID. |
| `product_uom_qty` | number | No | Quantity (default 1). |
| `price_unit` | number | No | Unit price (uses product default if omitted). |
| `name` | string | No | Line description override. |

**Example prompt**
> *"Create a quotation for customer #10 with 2 units of product #5."*

---

### `sale_update_order`

Update a quotation (only allowed while in `draft` or `sent` state).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Sale order ID. |
| `validity_date` | string | No | New expiry date (`YYYY-MM-DD`). |
| `note` | string | No | New internal note (Markdown). |

**Example prompt**
> *"Update quotation #55 — extend the validity date to 2026-10-31."*

---

### `sale_confirm_order`

Confirm a quotation, converting it to a Sales Order (state `sale`).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Sale order ID to confirm. |

:::{warning}
Confirmation is **irreversible** via this tool. Once confirmed, the order is locked
and line items cannot be changed through MCP tools. Use the Odoo UI to cancel if needed.
:::

**Example prompt**
> *"Confirm quotation #55."*

---

### `sale_log_note`

Post an internal note on a sales order (not visible to the customer).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Sale order ID. |
| `body` | string | Yes | Note body (Markdown). |

**Example prompt**
> *"Add a note to sales order #55: 'Customer requested delivery before end of quarter.'"*
