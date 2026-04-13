# Purchase (`lu_mcp_purchase`)

**6 tools** for Odoo purchase orders and RFQs (Requests for Quotation).

Requires: `lu_mcp_server`, Odoo `purchase` app.

---

## Overview

These tools cover the purchase order lifecycle: search, read, create, update, confirm,
and log notes. RFQs in `draft` or `sent` state can be edited; confirmed Purchase Orders
(`purchase`) are locked.

**Order states**: `draft` (RFQ), `sent` (RFQ Sent), `purchase` (Purchase Order),
`done` (Locked), `cancel` (Cancelled).

---

## Tools

### `purchase_search_orders`

Search purchase orders and RFQs.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Keyword search in order name or vendor name. |
| `state` | string | No | Filter by state: `draft`, `sent`, `purchase`, `done`, `cancel`. |
| `partner_id` | integer | No | Filter by vendor. |
| `user_id` | integer | No | Filter by purchase representative. |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Show all open RFQs from vendor #7."*

---

### `purchase_read_order`

Get full details of a purchase order or RFQ, including order lines.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Purchase order ID. |

**Example prompt**
> *"Show me the details of purchase order #33."*

---

### `purchase_create_order`

Create a new RFQ (Request for Quotation).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `partner_id` | integer | Yes | Vendor partner ID. |
| `date_order` | string | No | Order date (`YYYY-MM-DD`). Defaults to today. |
| `note` | string | No | Internal note (Markdown). |
| `order_line` | array | No | List of order lines (see below). |

**`order_line` items**

| Field | Type | Required | Description |
|---|---|---|---|
| `product_id` | integer | Yes | Product ID. |
| `product_qty` | number | No | Quantity (default 1). |
| `price_unit` | number | No | Unit price. |
| `name` | string | No | Line description override. |
| `date_planned` | string | No | Scheduled delivery date (`YYYY-MM-DD`). |

**Example prompt**
> *"Create an RFQ for vendor #7 with 10 units of product #12."*

---

### `purchase_update_order`

Update an RFQ (only allowed while in `draft` or `sent` state).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Purchase order ID. |
| `date_order` | string | No | New order date (`YYYY-MM-DD`). |
| `note` | string | No | New internal note (Markdown). |

**Example prompt**
> *"Update RFQ #33 — set the order date to 2026-10-01."*

---

### `purchase_confirm_order`

Confirm an RFQ, converting it to a Purchase Order (state `purchase`).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Purchase order ID to confirm. |

:::{warning}
Confirmation is **irreversible** via this tool. Once confirmed, the order is locked
as a Purchase Order. Use the Odoo UI to cancel if needed.
:::

**Example prompt**
> *"Confirm RFQ #33."*

---

### `purchase_log_note`

Post an internal note on a purchase order.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Purchase order ID. |
| `body` | string | Yes | Note body (Markdown). |

**Example prompt**
> *"Add a note to purchase order #33: 'Vendor confirmed delivery in 2 weeks.'"*
