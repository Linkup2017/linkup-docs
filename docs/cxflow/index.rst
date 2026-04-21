CxFlow
======

**Linkup CxFlow** is a Markdown-native project document management suite for
Odoo 19.0. It replaces scattered spreadsheets and Word files with a structured,
version-controlled document ecosystem — all inside your Odoo instance.

CxFlow covers the full software delivery lifecycle: requirements gathering,
process analysis, deliverable authoring, gate reviews, and final publishing —
with Git sync, a customer portal, and MCP-based AI integration.

Modules
-------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - ``lu_cxflow_docs``
     - Markdown document management — CPS, Deliverables, Reports, Notes
   * - ``lu_cxflow_registry``
     - 9 registry models for structured project metadata
   * - ``lu_cxflow_engine``
     - Rendering, validation & gate-checking engine
   * - ``lu_cxflow_portal``
     - GitBook-style document viewer (Portal + Public)
   * - ``lu_cxflow_publisher``
     - PDF / DOCX document publishing
   * - ``lu_cxflow_git_sync``
     - Bidirectional Git repository synchronization
   * - ``lu_cxflow_parse``
     - Odoo module source code parser
   * - ``lu_mcp_cxflow``
     - 12 MCP tools for AI-assisted document CRUD

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   architecture
   quickstart
   document-management
   registry
   engine
   portal-publishing
   git-sync
   source-parser
   mcp-integration
