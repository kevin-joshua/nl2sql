import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.app.services.catalog_manager import CatalogManager
from backend.app.services.intent_service import IntentService
from backend.app.services.cube_query_builder import build_cube_query
from backend.app.services.cube_client import execute_cube_query, CubeClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="NL2SQL API", version="1.0.0")

# Initialize CatalogManager
# The catalog is located at backend/catalog/catalog.yaml
# We assume this file is running from backend/app/main.py
CATALOG_PATH = Path(__file__).parent.parent / "catalog" / "catalog.yaml"
catalog_manager = CatalogManager(str(CATALOG_PATH))

# Initialize IntentService
intent_service = IntentService(catalog_manager)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    data: Any = None
    error: Any = None
    intent: Any = None
    sql_query: Any = None # Optional: return the generated Cube query for debugging


@app.post("/api/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest):
    """
    Process a natural language query and return the data.
    """
    logger.info(f"Received query: {request.query}")

    # 1. Process Intent
    intent_result = intent_service.process_query(request.query)

    if not intent_result.success:
        return QueryResponse(
            success=False,
            error=intent_result.error
        )

    # 2. Build Cube Query
    try:
        cube_query = build_cube_query(intent_result.intent)
    except Exception as e:
        logger.error(f"Failed to build Cube query: {e}")
        return QueryResponse(
            success=False,
            error={"message": f"Failed to build query: {str(e)}"},
            intent=intent_result.intent.model_dump()
        )

    # 3. Execute Cube Query
    try:
        cube_response = execute_cube_query(cube_query)
        return QueryResponse(
            success=True,
            data=cube_response.data,
            intent=intent_result.intent.model_dump(),
            sql_query=cube_query
        )
    except CubeClientError as e:
        logger.error(f"Cube execution failed: {e}")
        return QueryResponse(
            success=False,
            error={"message": f"Data retrieval failed: {str(e)}"},
            intent=intent_result.intent.model_dump(),
            sql_query=cube_query
        )
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        return QueryResponse(
            success=False,
            error={"message": "An unexpected error occurred."},
            intent=intent_result.intent.model_dump(),
            sql_query=cube_query
        )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
