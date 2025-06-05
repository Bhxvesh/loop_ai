import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ingestion_flow():
    response = client.post("/ingest", json={
        "ids": [1, 2, 3, 4, 5],
        "priority": "HIGH"
    })
    assert response.status_code == 200
    ingestion_id = response.json()["ingestion_id"]

    # Wait to allow first batch processing
    time.sleep(6)

    status_response = client.get(f"/status/{ingestion_id}")
    assert status_response.status_code == 200
    result = status_response.json()

    assert result["ingestion_id"] == ingestion_id
    assert result["status"] in ["triggered", "completed"]
    assert isinstance(result["batches"], list)
