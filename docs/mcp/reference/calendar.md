# Calendar (`lu_mcp_calendar`)

**5 tools** for Odoo calendar event management.

Requires: `lu_mcp_server`, Odoo `calendar` app.

---

## Overview

These tools let an AI client list, read, create, update, and delete calendar events.
Recurring events are read-only — update and delete operations on recurring events are
blocked with an explanatory error.

---

## Date / Time Format

All datetime values use one of these formats:

| Format | Example |
|---|---|
| `YYYY-MM-DD HH:MM:SS` | `2026-09-15 09:00:00` |
| ISO 8601 | `2026-09-15T09:00:00` |
| `YYYY-MM-DD HH:MM` | `2026-09-15 09:00` |
| `YYYY-MM-DD` (all-day) | `2026-09-15` |

---

## Tools

### `calendar_list_events`

List calendar events within an optional date range, filtered by attendee.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `start_date` | string | No | Return events starting from this date/datetime. |
| `end_date` | string | No | Return events ending before this date/datetime. |
| `partner_id` | integer | No | Filter by attendee (partner ID). |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Show my calendar events for next week."*

---

### `calendar_read_event`

Get full details of a calendar event.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Calendar event ID. |

**Example prompt**
> *"Show the details of calendar event #123."*

---

### `calendar_create_event`

Create a new calendar event.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Event title. |
| `start` | string | Yes | Start datetime. |
| `stop` | string | Yes | End datetime. |
| `partner_ids` | array of integer | No | Attendee partner IDs. |
| `location` | string | No | Location string. |
| `description` | string | No | Event description (Markdown). |
| `allday` | boolean | No | `true` for an all-day event. |

**Example prompt**
> *"Create a calendar event 'Q3 Review' on 2026-09-30 from 10:00 to 12:00 and invite partners #5 and #8."*

---

### `calendar_update_event`

Update an existing calendar event.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Event ID. |
| `name` | string | No | New title. |
| `start` | string | No | New start datetime. |
| `stop` | string | No | New end datetime. |
| `location` | string | No | New location. |
| `description` | string | No | New description (Markdown). |

:::{warning}
Recurring events cannot be updated via this tool. If the event is part of a recurrence,
the tool returns an error: *"Recurring events are read-only via MCP. Edit in Odoo."*
:::

**Example prompt**
> *"Update event #123 — change the location to 'Conference Room B'."*

---

### `calendar_delete_event`

Delete a calendar event.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Event ID. |

:::{warning}
Recurring events cannot be deleted via this tool. If the event is part of a recurrence,
the tool returns an error and no changes are made.
:::

**Example prompt**
> *"Delete calendar event #123."*
