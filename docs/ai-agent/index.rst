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
   * - ``lu_ai_orchestrator``
     - Orchestrator — domain routing, system prompts, context injection
     - |check|
   * - ``lu_ai_sidepanel``
     - Chat UI — web client integration, message threading
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
   * - ``lu_ai_claude``
     - Anthropic Claude connector (Opus / Sonnet / Haiku)
     - |check|
   * - ``lu_ai_edge``
     - Enterprise extension — advanced hooks, custom step types
     - Enterprise

.. |check| unicode:: U+2705

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   quickstart
   configuration
   domain-routing
