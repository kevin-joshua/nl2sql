# NL2SQL Project Status

**Date:** April 2026

## 1. Executive Summary
The NL2SQL project has successfully transitioned from a single-tenant baseline to a **Multi-Tenant SaaS architecture** with **Row-Based Access Control (RBAC)**, advanced **DSPy-driven LLM optimization**, and an automated **Proactive Intelligence Pipeline**. The core focus of recent development has been to move away from static prompt engineering to a robust, evaluable DSPy-driven framework that automatically improves via Reinforcement Learning from Human Feedback (RLHF), alongside building proactive intelligence capabilities.

## 2. Current Architecture & Completed Features

### 2.1 Multi-Tenancy & RBAC
- **Tenant Isolation:** Implemented true multi-tenant database isolation. Each client (`client_nestle`, `client_itc`, `client_unilever`) gets their own isolated Postgres schema, while sharing a common `app_meta` schema for application state.
- **Dynamic Routing:** `CubeClient` dynamically selects the appropriate Postgres schema per query based on the active user's `client_id` and token properties.
- **Hierarchical RBAC:** Strict Role-Based Access Control implemented via Cube.js Data Modeling. Users are mapped to roles (NSM, ZSM, ASM, SO, Admin) and are strictly limited to viewing data within their sales hierarchy bounds (e.g., a ZSM only sees their specific Zone's data). 

### 2.2 The Agentic DSPy Pipeline
The system has been completely rewritten to replace legacy static prompts with an agentic DSPy pipeline, enabling automated prompt optimization and reasoning.
- **Decomposer Agent:** Breaks complex user requests into smaller sub-intents.
- **Metrics Agent:** Maps natural language to the deterministic `catalog.yaml` definitions of KPIs, dimensions, and filters.
- **Postprocessing Agent:** Refines extracted intents, resolves ambiguity, and triggers clarifications when user requests are fundamentally ambiguous.
- **GEPA Metric (Generative Eval & Parsing Accuracy):** A robust, programmatic evaluation metric used to automatically grade the DSPy pipeline against a dataset. It evaluates semantic correctness without relying entirely on an LLM-as-a-judge.
- **DSPy Training & Optimization:** Full integration of DSPy's `MIPROv2` and `BootstrapFewShot` optimizers. The pipeline automatically learns from explicit human feedback and audit logs to refine its few-shot examples and system prompts.

### 2.3 RLHF (Reinforcement Learning from Human Feedback)
- **Feedback Loop:** Fully functional admin RLHF interface where domain experts can review, correct, and grade LLM extractions.
- **Automated Re-compilation:** Corrected traces are fed directly back into the DSPy training loop, allowing the model to adapt specifically to client-specific FMCG jargon.

### 2.4 Proactive Intelligence (The "Intel" Scheduler)
- **Background Mining:** A background job (APScheduler) runs every 6 hours to mine chat history, determining what KPIs and dimensions specific users care about most.
- **Dynamic Watches:** The system automatically builds active "watch configurations" based on a user's interest profile.
- **Statistical Detection & Narratives:** Watches execute deterministic Cube queries, pass data through statistical models (Z-scores, Trends, Thresholds), and invoke Claude Haiku to generate rich, contextual business narratives.
- **Premium UI Integration:** Extracted insights are rendered on the frontend using rich components (Sparklines, Trend indicators, Impact gaps) with interactive feedback loops (Pin, Dismiss, Acted On, Follow up in Chat).

## 3. What's Left To Do (Roadmap)

### 3.1 Pipeline & Evaluation
- **Agent Self-Correction Loop:** Currently, the DSPy agents run in a linear pipeline. We need to implement an internal reflection layer where the Postprocessing agent can flag an extraction error and send it back to the Metrics agent for a retry before failing the HTTP request.
- **Continuous Deployment of DSPy Weights:** Automate the reloading of optimized DSPy programs without requiring a full server restart. Right now, running `python -m app.dspy_pipeline.training` optimizes the JSON weights, but the API needs a safe hot-reload mechanism.

### 3.2 Analytics & Intelligence
- **Advanced Anomaly Models:** The intelligence scheduler currently uses basic Z-scores. We need to implement Prophet or ARIMA for advanced seasonality-aware anomaly detection.
- **Cross-Tenant Benchmarking (Opt-In):** Allow anonymized benchmarking where users can see how their metrics compare to the aggregate industry baseline (requires careful legal/data privacy safeguards).
- **Proactive Alerts (Push Notifications):** Connect the Intel scheduler to an email or Slack integration to push critical insights out of the platform.

### 3.3 Frontend Enhancements
- **Dynamic Visualizations:** Improve the compound rendering state of the frontend. If the user asks a comparative question, the backend needs to instruct the UI to render stacked bar charts or dual-axis line charts instead of simple tables.
- **Voice-to-SQL:** Add WebSpeech API integration on the frontend to allow mobile field officers (SOs) to literally talk to the app to get data.

### 3.4 Production Hardening
- **Cube.js Pre-aggregations:** With multiple tenants scaling, Cube's Redis pre-aggregation engine needs to be tuned for the heavy, automated reads generated by the Intel Scheduler.
- **Rate Limiting & Cost Controls:** Implement user-level token limits for Claude API calls to prevent runaway usage during intensive chat sessions.
- **E2E Testing:** Increase coverage of Cypress / Playwright tests for the frontend.
