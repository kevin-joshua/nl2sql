# NL2SQL - FMCG Analytics Documentation

## 1. Project Overview

NL2SQL is an intelligent, natural language interface for FMCG (Fast-Moving Consumer Goods) sales analytics. It allows users to ask questions in plain English (e.g., *"Show me total sales by region for the last 30 days"*) and receive real-time insights derived from a PostgreSQL data warehouse.

The system leverages:
- **LLMs (Anthropic Claude)** for intent extraction and natural language understanding.
- **Cube.js** as the semantic layer and query engine.
- **FastAPI** for the backend orchestration and API exposure.
- **PostgreSQL** as the underlying data store.

---

## 2. System Architecture

The application follows a pipeline architecture where a natural language query is transformed, validated, and executed against the data warehouse.

```mermaid
graph TD
    User[User Question] --> API[FastAPI Backend]
    API --> Extractor[Intent Extractor (LLM)]
    Extractor --> Normalizer[Intent Normalizer]
    Normalizer --> Validator[Intent Validator]
    Validator --> Builder[Cube Query Builder]
    Builder --> Cube[Cube.js Engine]
    Cube --> DB[(PostgreSQL)]
    Cube --> User
```

### High-Level Flow
1.  **Input**: User sends a natural language question.
2.  **Intent Extraction**: The LLM analyzes the question to extract user intent (metrics, dimensions, time ranges, filters).
3.  **Normalization**: Extracted terms are mapped to specific Cube.js schema identifiers (e.g., mapping "sales" to `fact_primary_sales.net_value`).
4.  **Validation**: The intent is validated against a generated semantic catalog (`catalog.yaml`) to ensure all metrics and dimensions exist.
5.  **Query Building**: The validated intent is converted into a Cube.js JSON query.
6.  **Execution**: The query is sent to the Cube.js API, which generates and executes SQL against PostgreSQL.
7.  **Response**: Data is returned to the user.

---

## 3. Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python**: Version 3.12 or higher.
- **Docker & Docker Compose**: For running the database and Cube.js services.
- **API Keys**: An Anthropic API key for the LLM service.

---

## 4. Installation & Setup

### 4.1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

### 4.2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4.3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.4. Configure Environment
Create a `.env` file in the project root with the following configuration:

```env
# Anthropic (LLM)
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL_ID=claude-sonnet-4-5

# Cube.js
CUBE_API_URL=http://localhost:4000/cubejs-api/v1
CUBE_API_SECRET=mysecretkey123

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 4.5. Start Infrastructure
Start the PostgreSQL database, Cube.js engine, and Redis using Docker Compose:

```bash
docker-compose up -d
```
*Wait approximately 30-60 seconds for the services to initialize.*

### 4.6. Start the Backend Application
Navigate to the `backend` directory and start the FastAPI server:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

---

## 5. Maintenance & Schema Updates (Prepping Stage)

This section describes the critical workflow required whenever the underlying Database Schema changes. **All 4 steps must be completed to ensure the system functions correctly.**

### Step 1: Generate Cube Schema
When the database schema changes, the Cube.js data model must be updated.
1.  Ensure the Docker services are running (`docker-compose up -d`).
2.  Access the **Cube.js Developer Playground** at `http://localhost:4000`.
3.  Use the schema generation feature in the playground to generate new YAML files reflecting the DB changes.
4.  Save these files in the `cube/model/cubes/` directory.

### Step 2: Regenerate Semantic Catalog
The backend relies on a local catalog (`catalog.yaml`) to validate user queries. This catalog must be synchronized with the new Cube schema.

Run the following command from the `backend` directory:
```bash
python -m app.utils.generate_catalog
```
*This script parses the YAML files in `cube/model/cubes/` and updates `backend/catalog/catalog.yaml`.*

### Step 3: Update LLM Prompt
The LLM needs to be aware of the new metrics and dimensions to correctly extract intents.
1.  Open `backend/app/prompts/intent_extraction.txt`.
2.  Update the **CATALOG** section with any new:
    *   **Metrics** (e.g., `new_metric -> description`)
    *   **Dimensions** (e.g., `new_dimension`)
3.  Update the **EXAMPLES** section to include a few natural language queries that use the new fields.

### Step 4: Update Normalizer Mappings
The `Intent Normalizer` maps natural language aliases to specific Cube.js identifiers.
1.  Open `backend/app/services/intent_normalizer.py`.
2.  Update `METRIC_MAP`: Add mappings for new metrics (define `PRIMARY` and `SECONDARY` scope paths if applicable).
3.  Update `DIMENSION_MAP`: Add mappings for new dimensions.

**Example Update in `intent_normalizer.py`**:
```python
"new_metric_name": {
    "PRIMARY": "fact_primary_sales.new_metric_col",
    "SECONDARY": "fact_secondary_sales.new_metric_col",
}
```

---

## 6. Application Flow & Components

### 6.1. Component Reference

| Component | Path | Description |
|-----------|------|-------------|
| **Main API** | `backend/app/main.py` | Entry point for the FastAPI application. |
| **Query Orchestrator** | `backend/app/services/query_orchestrator.py` | Manages the execution pipeline. |
| **Intent Extractor** | `backend/app/services/intent_extractor.py` | Calls LLM to parse natural language. |
| **Intent Normalizer** | `backend/app/services/intent_normalizer.py` | Maps semantic terms to Cube IDs. |
| **Intent Validator** | `backend/app/services/intent_validator.py` | Checks intent against `catalog.yaml`. See `backend/app/docs/INTENT_VALIDATION.md` for details. |
| **Catalog Generator** | `backend/app/utils/generate_catalog.py` | Script to sync catalog with Cube schema. |
| **Cube Model** | `cube/model/cubes/` | YAML files defining the data schema. |

### 6.2. Pipeline Detailed Flow

1.  **Intent Extraction**: The user's query is sent to Claude with the system prompt defined in `intent_extraction.txt`. The LLM returns a JSON object representing the user's intent.
2.  **Normalization**: The system takes the raw intent and translates it using `intent_normalizer.py`. For example, it resolves "volume" to `fact_secondary_sales.billed_qty` if the scope is Secondary Sales.
3.  **Validation**: The normalized intent is checked against `catalog.yaml`. If a metric or dimension is not found in the catalog, the request fails with a clear error message.
4.  **Query Building**: The validated intent is transformed into a structured Cube.js query (measures, dimensions, timeDimensions, filters).
5.  **Execution**: The query is executed via HTTP request to the Cube.js API.

---

## 7. API Reference

### Base URL
`http://localhost:8000`

### 7.1. Execute Query
**POST** `/query`

Executes a natural language query.

**Request Body:**
```json
{
  "query": "Show me total sales by region for last 30 days"
}
```

**Response:**
Returns the query result, including the generated Cube query and data points.

### 7.2. Clarification
**POST** `/clarify`

Used when the system needs more information to process a query (e.g., ambiguity resolution).

**Request Body:**
```json
{
  "request_id": "req_12345",
  "answers": {
    "scope": "SECONDARY"
  }
}
```

### 7.3. Catalog Endpoints
*   **GET** `/catalog/metrics`: List all available metrics.
*   **GET** `/catalog/dimensions`: List all available dimensions.
*   **GET** `/catalog/time-windows`: List supported time windows (e.g., `last_30_days`).

### 7.4. Health Check
*   **GET** `/health`: Check API status.

---
