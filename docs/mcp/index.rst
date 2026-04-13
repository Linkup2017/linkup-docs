MCP Server
==========

**Linkup MCP Server** embeds a `Model Context Protocol <https://modelcontextprotocol.io>`_
(MCP 2025-03-26 Streamable HTTP) server directly inside Odoo 19. AI clients such as
Claude Desktop, claude.ai, and any MCP-compatible tool can read and write Odoo data
through 74 tools — no external middleware required.

.. tip::

   New here? Follow the :doc:`quickstart` guide to connect Claude Desktop to your
   Odoo instance in under 10 minutes.

----

Modules
-------

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Module
     - Tools
     - Description
   * - ``lu_mcp_server``
     - —
     - Core MCP server: HTTP endpoint, OAuth 2.0 PKCE, session tracking, audit log,
       shared HTML↔Markdown utilities, plugin registry
   * - ``lu_mcp_knowledge``
     - 9
     - CRUD for Odoo Knowledge articles — create, read, update, move, delete, search,
       hierarchy tree
   * - ``lu_mcp_project``
     - 7
     - Project and task management — create tasks, sub-tasks, search, update,
       link Knowledge articles
   * - ``lu_mcp_survey``
     - 6
     - Survey creation and response analytics — add questions (8 types),
       generate surveys from Knowledge articles
   * - ``lu_mcp_helpdesk``
     - 12
     - Full helpdesk ticket lifecycle — create, reply, escalate, close, SLA
       status, customer history
   * - ``lu_mcp_calendar``
     - 5
     - Calendar event management — create, read, update, delete events, attendee filtering
   * - ``lu_mcp_contact``
     - 6
     - Odoo ``res.partner`` CRUD — search, create, update, list company children,
       log internal notes
   * - ``lu_mcp_crm``
     - 8
     - CRM pipeline — leads, opportunities, stages, pipeline summary,
       convert lead to opportunity
   * - ``lu_mcp_purchase``
     - 6
     - Purchase orders / RFQ — create, search, update, confirm, log notes
   * - ``lu_mcp_sale``
     - 6
     - Sales quotations and orders — create, search, update, confirm, log notes
   * - ``lu_mcp_timesheet``
     - 6
     - Timesheet entries — log time, update, delete, list, summarize by project
   * - ``lu_mcp_server_website``
     - —
     - Bridge module for Odoo Website environments (auto-installs with ``website``)

.. note::

   All plugin modules are **independently installable**. Install only the modules
   that match your Odoo apps. ``lu_mcp_server`` is the only mandatory dependency.

----

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   quickstart
   authentication
   architecture
   reference/index
