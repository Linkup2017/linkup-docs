# Surveys (`lu_mcp_survey`)

**6 tools** for Odoo survey creation and response analytics.

Requires: `lu_mcp_server`, Odoo `survey` app.

---

## Overview

These tools let an AI client list and read existing surveys, create new surveys, add
questions (9 question types), view aggregated responses, and generate a survey
automatically from a Knowledge article.

---

## Tools

### `survey_list_surveys`

List all surveys.

| Parameter | Type | Required | Description |
|---|---|---|---|
| *(none)* | | | |

**Example prompt**
> *"Show all available surveys."*

---

### `survey_read_survey`

Get full details of a survey, including its questions and options.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `survey_id` | integer | Yes | Survey ID. |

**Example prompt**
> *"Show me the questions in survey #10."*

---

### `survey_create_survey`

Create a new survey.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `title` | string | Yes | Survey title. |
| `description` | string | No | Survey description (Markdown). |

**Example prompt**
> *"Create a survey titled 'Employee Satisfaction Q3 2026'."*

---

### `survey_add_question`

Add a question to an existing survey.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `survey_id` | integer | Yes | Survey ID. |
| `title` | string | Yes | Question text. |
| `question_type` | string | No | Question type (default `simple_choice`). See below. |
| `is_required` | boolean | No | Whether the question is mandatory (default `false`). |
| `answers` | array of string | No | Answer choices for `simple_choice`, `multiple_choice`, `matrix`, or `scale`. |

**Question types**

| Type | Description |
|---|---|
| `text_box` | Long text (multi-line) |
| `char_box` | Short text (single line) |
| `numerical_box` | Numeric input |
| `date` | Date picker |
| `datetime` | Date and time picker |
| `simple_choice` | Single-select (radio buttons) |
| `multiple_choice` | Multi-select (checkboxes) |
| `matrix` | Grid of rows × columns |
| `scale` | Numeric scale (e.g. 1–5 rating) |

**Example prompt — multiple choice**
> *"Add a multiple-choice question 'Which features do you use?' to survey #10 with options: Chat, Workflows, Alerts, Reports."*

**Example prompt — scale**
> *"Add a scale question 'How satisfied are you overall?' to survey #10."*

---

### `survey_get_responses`

Get aggregated response analytics for a survey.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `survey_id` | integer | Yes | Survey ID. |

Returns total responses, completion rate, and per-question answer counts.

**Example prompt**
> *"Show the responses for survey #10."*

---

### `survey_generate_from_knowledge`

Generate a survey automatically from a Knowledge article. The LLM (Odoo AI) analyzes
the article content and creates relevant questions.

Requires: Odoo `knowledge` app and an AI provider configured in Odoo.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `article_id` | integer | Yes | Knowledge article ID to generate from. |
| `survey_title` | string | No | Title for the new survey. Defaults to the article title. |

**Example prompt**
> *"Generate a survey from Knowledge article #55 (Product Training Guide)."*
