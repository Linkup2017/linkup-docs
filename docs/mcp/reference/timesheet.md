# Timesheets (`lu_mcp_timesheet`)

**6 tools** for Odoo timesheet entry management.

Requires: `lu_mcp_server`, Odoo `hr_timesheet` app.

---

## Overview

These tools let an AI client list, read, log, update, delete timesheet entries, and
view a project-level summary. All entries are stored on `account.analytic.line` and
must be associated with a project.

---

## Tools

### `timesheet_list_timesheets`

List timesheet entries with optional filters.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | integer | No | Filter by project. |
| `task_id` | integer | No | Filter by task. |
| `employee_id` | integer | No | Filter by employee. |
| `date_from` | string | No | Start date (`YYYY-MM-DD`). |
| `date_to` | string | No | End date (`YYYY-MM-DD`). |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Show all timesheets for project #5 this week."*

---

### `timesheet_read_timesheet`

Get full details of a timesheet entry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Timesheet entry ID (`account.analytic.line` ID). |

**Example prompt**
> *"Show me timesheet entry #201."*

---

### `timesheet_log_time`

Log a new timesheet entry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | integer | Yes | Project to log time against. |
| `unit_amount` | number | Yes | Hours to log (e.g. `1.5` for 1h 30m). |
| `name` | string | Yes | Description of the work done. |
| `task_id` | integer | No | Task to associate the entry with. |
| `date` | string | No | Date (`YYYY-MM-DD`). Defaults to today. |
| `employee_id` | integer | No | Employee ID. Defaults to the authenticated user's employee. |

**Example prompt**
> *"Log 2 hours on project #5, task #42 — 'Code review and feedback'."*

---

### `timesheet_update_timesheet`

Update an existing timesheet entry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Timesheet entry ID. |
| `unit_amount` | number | No | New duration in hours. |
| `name` | string | No | New description. |
| `date` | string | No | New date (`YYYY-MM-DD`). |

**Example prompt**
> *"Update timesheet #201 — change hours from 2 to 2.5."*

---

### `timesheet_delete_timesheet`

Delete a timesheet entry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Timesheet entry ID. |

**Example prompt**
> *"Delete timesheet entry #201."*

---

### `timesheet_summary_by_project`

Show total hours logged per project, grouped by project and employee.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `date_from` | string | No | Start date (`YYYY-MM-DD`). |
| `date_to` | string | No | End date (`YYYY-MM-DD`). |
| `employee_id` | integer | No | Filter by employee. |

Returns a Markdown table with project, employee, and total hours.

**Example prompt**
> *"Summarize all timesheet hours logged this month, grouped by project."*
