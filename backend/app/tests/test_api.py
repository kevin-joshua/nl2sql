from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.intent import Intent, IntentType
from backend.app.services.intent_service import IntentResult
from backend.app.services.cube_client import CubeResponse

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("backend.app.main.intent_service.process_query")
@patch("backend.app.main.execute_cube_query")
def test_process_query_success(mock_execute_cube, mock_process_query):
    # Mock IntentService response
    mock_intent = Intent(
        intent_type=IntentType.SNAPSHOT,
        metric="total_quantity"
    )
    mock_process_query.return_value = IntentResult(
        success=True,
        intent=mock_intent
    )

    # Mock CubeClient response
    mock_execute_cube.return_value = CubeResponse(
        data=[{"sales_fact.quantity": 100}],
        request_id="test-req-id"
    )

    response = client.post("/api/query", json={"query": "total sales"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["data"] == [{"sales_fact.quantity": 100}]
    assert json_response["intent"]["metric"] == "total_quantity"


@patch("backend.app.main.intent_service.process_query")
def test_process_query_intent_failure(mock_process_query):
    # Mock IntentService failure
    mock_process_query.return_value = IntentResult(
        success=False,
        error={"message": "I didn't understand that."}
    )

    response = client.post("/api/query", json={"query": "blah blah"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"]["message"] == "I didn't understand that."


@patch("backend.app.main.intent_service.process_query")
@patch("backend.app.main.execute_cube_query")
def test_process_query_cube_failure(mock_execute_cube, mock_process_query):
    # Mock IntentService response
    mock_intent = Intent(
        intent_type=IntentType.SNAPSHOT,
        metric="total_quantity"
    )
    mock_process_query.return_value = IntentResult(
        success=True,
        intent=mock_intent
    )

    # Mock CubeClient failure
    from backend.app.services.cube_client import CubeClientError
    mock_execute_cube.side_effect = CubeClientError("Cube down")

    response = client.post("/api/query", json={"query": "total sales"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is False
    assert "Cube down" in json_response["error"]["message"]
