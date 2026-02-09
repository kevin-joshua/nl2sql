# NL2SQL: Natural Language to SQL Analytics for FMCG

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Cube.js](https://img.shields.io/badge/Cube.js-Latest-purple.svg)


---
## 🎯 Summary & Problem Statement

In the FMCG sector, business users (sales managers, marketing analysts) need quick access to sales data to make informed decisions. However, they often lack the technical skills to write complex SQL queries, creating a bottleneck where they must rely on data analysts for simple requests.

**NL2SQL bridges this gap** by providing a simple, safe, and powerful conversational interface. It leverages a "Guardrails First" philosophy:
*   **Accuracy**: Ensures queries map correctly to business metrics via a strict Catalog.
*   **Safety**: Prevents invalid or malicious queries from reaching the database.
*   **Explainability**: Provides clear feedback on how a query was interpreted.

---

## 🚀 Key Features

- **Natural Language Understanding**: Ask questions in plain English (e.g., "Show me sales by region").
- **Intent Extraction**: LLM-powered query parsing with state-of-the-art models (Claude).
- **Semantic Validation**: A rigorous catalog-based validation system ensures every query is strictly mapped to defined business metrics.
- **Clarification Flow**: Automatically detects ambiguity and asks follow-up questions (e.g., "Did you mean Primary or Secondary sales?").
- **Cube.js Integration**: Seamless connection to your data warehouse via the Cube.js semantic layer, handling complex joins and aggregations.
- **Data Visualization**: Automatic generation of appropriate charts (Table, Bar, Line, Pie).
- **Transparency**: Full visibility into the pipeline steps, from raw intent to final SQL.
- **Resiliency**: Tests designed to survive LLM drift and schema changes.

---

## 🏗️ Architecture

The system follows a pipeline architecture where data flows through distinct stages of processing, validation, and execution.

### 1. High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NL2SQL Pipeline                               │
│                                                                         │
│   "Show me sales by region"                                             │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│   │ Intent Extractor│ ──► │ Intent Validator│ ──► │Cube Query Builder│  │
│   │     (LLM)       │     │   (Catalog)     │     │   (Mapping)     │   │
│   └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                            │             │
│                                                            ▼             │
│                                                   ┌─────────────────┐    │
│                                                   │   Cube Client   │    │
│                                                   │    (HTTP)       │    │
│                                                   └─────────────────┘    │
│                                                            │             │
│                                                            ▼             │
│                                                   ┌─────────────────┐   │
│                                                   │   PostgreSQL    │   │
│                                                   │   (Data Store)  │   │
│                                                   └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2. Data Flow Steps

1.  **Intent Extraction (LLM)**: The user's query is sent to the LLM (Claude) with a prompt containing the business catalog. The LLM returns a structured JSON "Intent".
2.  **Normalization & Validation**:
    *   *Normalization*: Semantic terms are mapped to physical Cube IDs (e.g., "sales" -> `fact_secondary_sales.net_value`).
    *   *Validation*: The Intent is checked against the `catalog.yaml` and strict Pydantic models.
3.  **Query Generation**: The validated Intent is **deterministically** translated into a Cube Query JSON.
4.  **Execution (Cube)**: Cube.js generates the SQL, executes it against PostgreSQL, and handles caching.
5.  **Visualization**: The result set is analyzed to select the best chart type (e.g., Time Series -> Line Chart).

### 3. Core Design Decisions

*   **Decoupled Catalog**: The LLM sees a simplified "Business Catalog" (`catalog.yaml`), not the raw DB schema. This reduces hallucinations.
*   **Cube as Semantic Layer**: We do not generate SQL directly. We generate strict Cube queries. Cube handles the complex SQL generation, joins, and time zones.
*   **Stateful Interaction (Redis)**: The system uses Redis to store conversation state, allowing for clarification loops and follow-up questions.

---

## 📁 Project Structure

The codebase is organized to enforce separation of concerns:

```
nl2sql/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI Application entry point
│   │   ├── models/
│   │   │   └── intent.py           # Pydantic contract enforcing structural validity
│   │   ├── services/
│   │   │   ├── query_orchestrator.py # Core "Brain": Coordinates pipeline steps
│   │   │   ├── intent_extractor.py   # LLM Interface (Claude) -> Raw JSON
│   │   │   ├── intent_normalizer.py  # Maps semantic terms to Cube fields
│   │   │   ├── intent_validator.py   # Enforces strict Catalog rules
│   │   │   ├── cube_query_builder.py # Deterministic compiler (Intent -> Cube Query)
│   │   │   ├── cube_client.py        # HTTP Client for Cube API
│   │   │   ├── catalog_manager.py    # Loads/Serves catalog.yaml
│   │   │   └── data_visualizer.py    # Generates Plotly/JSON visualization configs
│   │   ├── pipeline/
│   │   │   └── state_store.py        # Redis state management for multi-turn chat
│   │   ├── prompts/
│   │   │   └── intent_extraction.txt # Few-shot prompt for LLM
│   │   └── utils/
│   │       └── generate_catalog.py   # Script to sync Catalog with Cube schema
│   ├── catalog/
│   │   └── catalog.yaml            # Single Source of Truth for Business Logic
│   └── tests/                      # Comprehensive Unit and E2E tests
├── cube/
│   ├── model/
│   │   └── cubes/                  # Cube.js Datamodeling (YAML)
│   └── data/                       # Seed data scripts
├── docker-compose.yml              # Infrastructure orchestration
└── requirements.txt
```

---

## 🏁 Getting Started

### Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose**
- **Redis** (Required for state management; docker-compose handles this).
- **Anthropic API Key** (for Claude LLM).

### 1. Installation

```bash
git clone https://github.com/yourusername/nl2sql.git
cd nl2sql

# Backend Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# LLM Provider
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL_ID=claude-3-sonnet-20240229

# Cube.js
CUBE_API_URL=http://localhost:4000/cubejs-api/v1
CUBE_API_SECRET=mysecretkey123

# State Store (Redis)
REDIS_URL=redis://localhost:6379/0

# App Settings
LOG_LEVEL=INFO
```

### 3. Start Infrastructure

Use Docker Compose to spin up PostgreSQL, Cube.js, and Redis.

```bash
docker-compose up -d

# Wait ~30s for services to initialize...

# Populate Database (One-time setup)
# Windows PowerShell:
Get-Content .\cube\data\02_populate_data.sql | docker exec -i nl2sql-postgres psql -U postgres -d sales_analytics
```

### 4. Run the API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 API Usage

### Execute Query

**POST** `/query`

```json
{
  "query": "Show me total secondary sales by zone for the last 30 days"
}
```

**Response**:
```json
{
  "query": "Show me total secondary sales by zone for last 30 days",
  "success": true,
  "stage": "completed",
  "validated_intent": {
    "intent_type": "distribution",
    "metric": "fact_secondary_sales.net_value",
    "group_by": ["fact_secondary_sales.zone"],
    "time_range": {"window": "last_30_days"}
  },
  "data": [
    {"fact_secondary_sales.zone": "North", "fact_secondary_sales.net_value": 150000},
    {"fact_secondary_sales.zone": "South", "fact_secondary_sales.net_value": 230000}
  ],
  "visualization": {
    "type": "bar",
    "chart_data": { ... }
  }
}
```

---

## 🔧 Supported Metrics & Dimensions

The system comes pre-configured with a standard FMCG data model (`catalog.yaml`).

| Category | Item | Description |
|----------|------|-------------|
| **Metrics** | `Primary Sales` | Sales from Company to Distributor |
| | `Secondary Sales` | Sales from Distributor to Retailer (Offtake) |
| | `Transaction Count` | Volume of individual invoices |
| **Dimensions** | `Geography` | Zone, State |
| | `Product` | Brand, Category |
| | `Partner` | Distributor Name, Warehouse Name |
| **Time** | `Windows` | Last 7/30/90 Days, MTD, QTD, YTD, All Time |

---

## 🧪 Testing Strategy

The project employs a robust testing strategy to ensure reliability against AI unpredictability.

### 1. Deterministic Tests
Unit tests validate that the core logic (Validator, Builder) behaves exactly as expected.
```bash
pytest app/tests/test_catalog_contract.py
pytest app/tests/test_intent_validator.py
```

### 2. End-to-End Pipeline Tests
Simulates real user queries to ensure the entire flow (LLM -> Cube -> Response) works.
```bash
pytest app/tests/test_query_orchestrator_e2e.py
```

---

## 🛣️ Future Work

*   **Automated Catalog Sync**: Build a watcher to automatically trigger catalog generation when Cube files change.
*   **Natural Language Answers**: Add a final LLM step to summarize the JSON data into a text paragraph.
*   **Multi-Tenant Support**: Enable context-aware catalog filtering based on the logged-in user.
*   **CI/CD Pipeline**: GitHub Actions for automated Docker builds and testing.