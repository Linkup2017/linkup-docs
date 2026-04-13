# Knowledge (`lu_mcp_knowledge`)

**9 tools** for Odoo Knowledge article CRUD.

Requires: `lu_mcp_server`, Odoo `knowledge` app.

---

## Overview

These tools let an AI client browse the Knowledge article hierarchy, read and search
articles, and create, update, move, or soft-delete articles. Article bodies are
exchanged as Markdown — the plugin converts to/from Odoo HTML automatically.

---

## Tools

### `knowledge_list_workspaces`

List all top-level workspace articles.

| Parameter | Type | Required | Description |
|---|---|---|---|
| *(none)* | | | |

**Example prompt**
> *"Show me all Knowledge workspaces."*

---

### `knowledge_list_articles`

List direct children of a parent article, or root articles of a category.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `parent_id` | integer | No | ID of the parent article. Omit to list root articles. |
| `category` | string | No | `workspace`, `private`, or `shared`. Used when `parent_id` is omitted. |

**Example prompt**
> *"List the articles inside the HR Policies workspace (id=42)."*

---

### `knowledge_read_article`

Read the full content (title + body) of an article. Body is returned as Markdown.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | Numeric ID of the article to read. |

**Example prompt**
> *"Read Knowledge article #105."*

---

### `knowledge_search_articles`

Search articles by keyword. Searches both title and body content.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | Search keyword or phrase. |
| `limit` | integer | No | Maximum results (default 20, max 80). |

**Example prompt**
> *"Find Knowledge articles about 'onboarding'."*

---

### `knowledge_get_article_tree`

Show the article hierarchy tree starting from a given article.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | Root article ID for the tree view. |
| `depth` | integer | No | How many levels to expand (1–4, default 2). |

**Example prompt**
> *"Show the article tree under workspace #10, 3 levels deep."*

---

### `knowledge_create_article`

Create a new Knowledge article.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Article title. |
| `body_markdown` | string | No | Article body in Markdown. |
| `parent_id` | integer | No | Parent article ID. Omit to create a private article. |
| `icon` | string | No | Emoji icon (e.g. `📝`). |

**Example prompt**
> *"Create a Knowledge article titled 'Q3 OKRs' under workspace #10 with the following content: ..."*

:::{note}
Articles created without a `parent_id` are placed in the **private** category.
To create a workspace article, supply the workspace article's ID as `parent_id`.
:::

---

### `knowledge_update_article`

Update an existing article. Use `body_markdown` to replace the entire body, or
`content_updates` for partial edits. The two are mutually exclusive.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | ID of the article to update. |
| `name` | string | No | New title. Omit to keep existing. |
| `body_markdown` | string | No | Replace the entire body with this Markdown. |
| `content_updates` | array | No | List of partial update operations (see below). |
| `icon` | string | No | New emoji icon. |

**`content_updates` operations**

Each item is an object with:

| Field | Values | Description |
|---|---|---|
| `type` | `append` | Add content at the end of the article. |
| `type` | `prepend` | Add content at the beginning. |
| `type` | `replace_section` | Replace a named Markdown section heading and its content. |
| `type` | `insert_after` | Insert content after a named Markdown section heading. |
| `content` | string | Markdown text to insert or replace with. |
| `target` | string | Required for `replace_section` and `insert_after`. The exact section heading text. |

**Example prompt — append**
> *"Append a new section '## Action Items' with a task list to article #105."*

```json
{
  "article_id": 105,
  "content_updates": [
    {
      "type": "append",
      "content": "## Action Items\n\n- [ ] Follow up with Legal\n- [ ] Review budget"
    }
  ]
}
```

**Example prompt — replace section**
> *"Replace the 'Status' section in article #105 with 'Completed'."*

```json
{
  "article_id": 105,
  "content_updates": [
    {
      "type": "replace_section",
      "target": "Status",
      "content": "## Status\n\nCompleted"
    }
  ]
}
```

---

### `knowledge_move_article`

Move an article to a different location in the Knowledge hierarchy.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | ID of the article to move. |
| `parent_id` | integer | No | New parent article ID. Omit to move to the workspace root. |
| `category` | string | No | Target category: `workspace`, `private`, or `shared` (default `workspace`). |

**Example prompt**
> *"Move article #88 to the root of the workspace."*

---

### `knowledge_delete_article`

Send an article to trash (soft delete). Trashed articles can be recovered within 30 days.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | ID of the article to trash. |

**Example prompt**
> *"Delete Knowledge article #88."*

:::{warning}
`knowledge_delete_article` performs a **soft delete** (moves to trash). The article is
recoverable from the Odoo Knowledge trash for up to 30 days. This is not a permanent
deletion.
:::
