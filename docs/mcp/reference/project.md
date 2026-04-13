# Project (`lu_mcp_project`)

**7 tools** for Odoo Project task management.

Requires: `lu_mcp_server`, Odoo `project` app.

---

## Overview

These tools cover the full task lifecycle: browse projects and stages, search tasks,
read full task details, create and update tasks, and link Knowledge articles to tasks.
Sub-tasks are supported via the `parent_id` parameter on `project_create_task`.

---

## Tools

### `project_list_projects`

List all active Odoo projects.

| Parameter | Type | Required | Description |
|---|---|---|---|
| *(none)* | | | |

**Example prompt**
> *"What projects are active in Odoo?"*

---

### `project_list_stages`

List task stages, optionally filtered to a specific project.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | integer | No | Filter stages to a specific project. Omit for all stages. |

**Example prompt**
> *"What stages does project #5 use?"*

---

### `project_search_tasks`

Search tasks with optional filters.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Search keyword in task name or description. |
| `project_id` | integer | No | Filter by project. |
| `stage_id` | integer | No | Filter by stage. |
| `assignee_id` | integer | No | Filter by assignee (user ID). |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Find all open tasks in the Marketing project assigned to user #3."*

---

### `project_read_task`

Get full details of a task, including description, stage, assignees, deadline, and
any linked Knowledge articles.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | integer | Yes | Numeric task ID. |

**Example prompt**
> *"Show me the details of task #201."*

---

### `project_create_task`

Create a new task (or sub-task).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Task title. |
| `project_id` | integer | No | Project to assign the task to. |
| `parent_id` | integer | No | Parent task ID — creates a sub-task. |
| `description` | string | No | Task description (Markdown). |
| `assignee_id` | integer | No | User ID of the assignee. |
| `deadline` | string | No | Deadline date (`YYYY-MM-DD`). |

**Example prompt**
> *"Create a task 'Prepare Q3 report' in project #5 assigned to user #8, due 2026-09-30."*

---

### `project_update_task`

Update an existing task.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | integer | Yes | Task ID to update. |
| `name` | string | No | New task title. |
| `stage_id` | integer | No | Move to a different stage. |
| `assignee_id` | integer | No | Change the assignee. |
| `deadline` | string | No | New deadline (`YYYY-MM-DD`). |
| `description` | string | No | New description (Markdown). |

**Example prompt**
> *"Move task #201 to the 'Done' stage."*

---

### `project_link_knowledge_article`

Link a Knowledge article to a task. Requires the Odoo `knowledge` app to be installed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | integer | Yes | Task ID. |
| `article_id` | integer | Yes | Knowledge article ID to link. |

**Example prompt**
> *"Link Knowledge article #55 to task #201."*

:::{note}
This tool is only registered when the `knowledge` Odoo app is installed. If Knowledge
is not installed, the tool will not appear in `tools/list`.
:::
