AI Agent
========

**Linkup AI Agent** is a hybrid LLM-powered AI assistant that runs directly
inside your Odoo 19.0 Enterprise instance. It supports both local inference via
`Ollama <https://ollama.com>`_ and cloud inference via Anthropic Claude —
letting you assign a different LLM provider to each agent for cost and
performance flexibility.

Modules
-------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Module
     - Description
     - Apps Store
   * - ``lu_ai_ollama``
     - Ollama connector — model management, health checks, streaming
     - |check|
   * - ``lu_ai_claude``
     - Anthropic Claude connector (Opus / Sonnet / Haiku)
     - |check|
   * - ``lu_ai_sidepanel``
     - Chat UI — web client integration, message threading
     - |check|
   * - ``lu_ai_rag``
     - File-server RAG — local Ollama embeddings, zero external data transfer
     - |check|
   * - ``lu_ai_orchestrator``
     - Orchestrator — domain routing, system prompts, context injection
     - |check|
   * - ``lu_ai_workflow``
     - Workflow engine — multi-step automation, triggers, conditions
     - |check|
   * - ``lu_ai_proactive``
     - Proactive alerts — scheduled checks, threshold notifications
     - |check|
   * - ``lu_ai_admin``
     - Admin dashboard — usage analytics, model monitoring
     - |check|   
   * - ``lu_ai_edge``
     - Enterprise extension — advanced hooks, custom step types
     - Enterprise

Domain Extension Modules
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 35 50 15

   * - Module
     - Description
     - Base
   * - ``lu_ai_rag_crm``
     - CRM domain RAG partitioning
     - rag
   * - ``lu_ai_rag_finance``
     - Finance domain RAG partitioning
     - rag
   * - ``lu_ai_rag_helpdesk``
     - Helpdesk domain RAG partitioning
     - rag
   * - ``lu_ai_rag_hr``
     - HR domain RAG partitioning
     - rag
   * - ``lu_ai_rag_inventory``
     - Inventory domain RAG partitioning
     - rag
   * - ``lu_ai_rag_procurement``
     - Procurement domain RAG partitioning
     - rag
   * - ``lu_ai_rag_sales``
     - Sales domain RAG partitioning
     - rag
   * - ``lu_ai_orchestrator_account``
     - Finance/Accounting domain agent (invoices, payments, budgets)
     - orchestrator
   * - ``lu_ai_orchestrator_crm``
     - CRM domain agent (leads, opportunities, pipeline)
     - orchestrator
   * - ``lu_ai_orchestrator_helpdesk``
     - Helpdesk domain agent (tickets, SLA, customer support)
     - orchestrator
   * - ``lu_ai_orchestrator_hr``
     - HR domain agent (employees, attendance, payroll, leaves)
     - orchestrator
   * - ``lu_ai_orchestrator_sale``
     - Sales domain agent (sale orders, quotations, revenue)
     - orchestrator
   * - ``lu_ai_orchestrator_stock``
     - Inventory domain agent (stock, transfers, purchase orders)
     - orchestrator
   * - ``lu_ai_proactive_crm``
     - CRM proactive alerts — lead stagnation detection, at-risk scoring
     - proactive
   * - ``lu_ai_proactive_helpdesk``
     - Helpdesk proactive alerts — SLA breach detection, ticket nudge
     - proactive
   * - ``lu_ai_proactive_stock``
     - Stock proactive alerts — shortage detection, autonomous PO suggestion
     - proactive

.. |check| unicode:: U+2705

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   architecture
   quickstart
   configuration
   domain-routing
   workflows
   proactive-alerts
