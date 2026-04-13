# Contacts (`lu_mcp_contact`)

**6 tools** for Odoo `res.partner` (contacts and companies) management.

Requires: `lu_mcp_server`, Odoo `contacts` app (base).

---

## Overview

These tools let an AI client search, read, create, and update Odoo contacts and companies,
list sub-contacts (individuals under a company), and post internal notes.

---

## Tools

### `contact_search_contacts`

Search contacts and companies.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Keyword search across name, email, and phone. |
| `is_company` | boolean | No | `true` for companies only, `false` for individuals only. |
| `customer_rank` | integer | No | Minimum customer rank (1 = is a customer). |
| `supplier_rank` | integer | No | Minimum supplier rank (1 = is a supplier). |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Search for all customers named 'Kim'."*

---

### `contact_read_contact`

Get full details of a contact or company: address, VAT, ranks, sub-contacts, tags, and
internal notes.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Partner ID. |

**Example prompt**
> *"Show me full details for contact #42."*

---

### `contact_create_contact`

Create a new contact or company.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Contact or company name. |
| `is_company` | boolean | No | `true` to create a company, `false` for an individual. |
| `parent_id` | integer | No | Parent company ID (creates the contact under a company). |
| `email` | string | No | Email address. |
| `phone` | string | No | Phone number. |
| `street` | string | No | Street address. |
| `city` | string | No | City. |
| `country_id` | integer | No | Country ID (Odoo `res.country` ID). |

**Example prompt**
> *"Create a company contact named 'Seoul Tech Co.' with email info@seoultech.kr."*

---

### `contact_update_contact`

Update an existing contact or company.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Partner ID. |
| `name` | string | No | New name. |
| `email` | string | No | New email. |
| `phone` | string | No | New phone number. |
| `street` | string | No | New street address. |
| `city` | string | No | New city. |
| `country_id` | integer | No | New country ID. |

**Example prompt**
> *"Update contact #42 — set email to new@example.com and city to Busan."*

---

### `contact_list_children`

List individual contacts (employees, contacts) under a company.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `parent_id` | integer | Yes | Company partner ID. |

**Example prompt**
> *"List all contacts under company #10 (Acme Corp)."*

---

### `contact_log_note`

Post an internal note on a contact record (not visible externally).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Partner ID. |
| `body` | string | Yes | Note body (Markdown). |

**Example prompt**
> *"Log a note on contact #42: 'Spoke at KCD 2026 — interested in enterprise plan.'"*
