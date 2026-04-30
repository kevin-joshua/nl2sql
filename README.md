# NL2SQL: Enterprise Multi-Tenant Analytics & Intelligence

**NL2SQL** is a guardrails-first, multi-tenant SaaS application that enables business stakeholders (from Field Officers to National Sales Managers) to extract FMCG sales insights using natural language. It leverages **Anthropic's Claude** orchestrated by **DSPy** for robust intent extraction, strict **Cube.js** data modeling for deterministic query execution, and **Row-Based Access Control (RBAC)** to ensure users only see data within their designated hierarchy.

---

## 1. Core Architecture & Philosophy

The system strictly adheres to a **"Guardrails-First"** architecture. 
**The AI never writes SQL directly.** Instead:
1. **Agentic DSPy Pipeline**: Understands complex user intent and breaks it down into standard metrics, dimensions, and filters.
2. **Deterministic Catalog Validation**: Verifies the AI's intent against a strict `catalog.yaml` to ensure no hallucinations occur.
3. **Semantic Query Execution (Cube.js)**: Translates the validated intent into efficient, cached, dialect-specific SQL while enforcing tenant isolation and hierarchical data security.

### Key Innovations:
- **True Multi-Tenancy**: Complete database schema isolation per client (e.g., Nestle, ITC) with dynamic routing.
- **DSPy & RLHF Optimization**: Moving beyond brittle static prompts, the system compiles and optimizes its own prompts through DSPy's MIPROv2, guided by a Reinforcement Learning from Human Feedback (RLHF) loop.
- **Proactive Intelligence**: An automated background scheduler mines user chat history to build "interest profiles," runs continuous statistical analyses on relevant KPIs, and generates personalized, narrative-driven business insights on a rich UI.

---

## 2. Technology Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS, Recharts.
- **Backend Orchestration**: FastAPI (Python), DSPy, LangChain.
- **Data & Semantic Layer**: Cube.js, PostgreSQL.
- **State & Context**: Redis (Session persistence and follow-up query context).
- **LLM**: Anthropic Claude (Haiku / Sonnet).

---

## 3. System Workflow

### The Conversational Query Flow:
1. User asks a question (e.g., *"Why did KitKat sales drop in the West zone last week?"*).
2. The Backend loads conversational context via Redis.
3. **DSPy Decomposer Agent** splits the compound query into sub-intents.
4. **DSPy Metrics Agent** maps raw language to specific database dimensions/KPIs.
5. **Semantic Validation** ensures the requested fields exist in `catalog.yaml`. Ambiguities trigger immediate clarification requests.
6. **Cube.js** executes the structured intent against the specific Tenant's isolated database schema.
7. Results are rendered via dynamically assigned Visual Specifications (Charts/Tables).

### The Proactive Intelligence Flow:
1. **Scheduler** runs every 6 hours in the background.
2. **Profile Mining**: Analyzes user chat logs to determine preferred KPIs and dimensions.
3. **Execution**: Issues heavy aggregate queries against the Data Warehouse.
4. **Detection**: Runs Z-score anomaly detection and trend regression models.
5. **Narration**: Generates rich LLM summaries detailing the business impact.
6. **Delivery**: Surfaces the insights on the user's dashboard with inline sparklines and feedback loops.

---

## 4. Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js & npm
- Python 3.10+
- Anthropic API key

### Local Development Setup

1. **Environment Variables**:
   Copy the example config and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and insert ANTHROPIC_API_KEY
   ```

2. **Run via Script (Windows)**:
   This will spin up Postgres, Cube, Redis, seed the data, and run the backend.
   ```bash
   .\start-dev.ps1
   ```

3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the App**: Navigate to `http://localhost:3000`

---

## 5. Development & Testing

- **RLHF Tuning**: Log in as `nestle_admin` and navigate to `/rlhf` to grade LLM responses. Run `python -m app.dspy_pipeline.training` to re-compile the DSPy model weights based on your grades.
- **Proactive Insights**: To manually force the 6-hour scheduler to run, click the **Generate ⚡** button on the Insights page (available to all users during dev).
- **Test Suite**: Run backend unit tests via `pytest` in the `/backend` directory.

---

## 6. Project Roadmap (What's Next)

While the core SaaS architecture is stable, the following features are actively being developed:

- [ ] **Agent Self-Correction**: Implementing an internal retry loop where the DSPy Postprocessing agent can critique and correct the Metrics agent before returning an error to the user.
- [ ] **Advanced Anomaly Models**: Upgrading the Intelligence Scheduler from simple Z-scores to Prophet/ARIMA for seasonality-aware detection.
- [ ] **Hot-Reloadable DSPy Weights**: Allowing the FastAPI server to ingest freshly compiled DSPy prompt weights without requiring a restart.
- [ ] **Proactive Alerts Integration**: Push notifications (Email/Slack) for critical intelligence insights.
- [ ] **Enhanced Visual Parsing**: Dynamic compound frontend rendering for complex comparative queries (e.g., dual-axis charting).
- [ ] **Voice-to-SQL**: Adding WebSpeech API capabilities to the Next.js frontend for mobile field operatives.

---

*See `docs/project_status.md` and `docs/architecture.md` for a deeper technical breakdown of the system components.*
