import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
import time
from datetime import datetime

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_ingest_invalid_ids():
    response = client.post(
        "/ingest",
        json={"ids": [0, 2, 3], "priority": "HIGH"}  # 0 is invalid
    )
    assert response.status_code == 400

def test_ingest_valid_request():
    response = client.post(
        "/ingest",
        json={"ids": [1, 2, 3, 4, 5], "priority": "HIGH"}
    )
    assert response.status_code == 200
    assert "ingestion_id" in response.json()

def test_status_invalid_id():
    response = client.get("/status/invalid_id")
    assert response.status_code == 404

def test_priority_ordering():
    # Submit medium priority first
    response1 = client.post(
        "/ingest",
        json={"ids": [1, 2, 3], "priority": "MEDIUM"}
    )
    ingestion_id1 = response1.json()["ingestion_id"]
    
    # Submit high priority second
    response2 = client.post(
        "/ingest",
        json={"ids": [4, 5, 6], "priority": "HIGH"}
    )
    ingestion_id2 = response2.json()["ingestion_id"]
    
    # Wait for processing to start
    time.sleep(2)
    
    # Check status of both requests
    status1 = client.get(f"/status/{ingestion_id1}")
    status2 = client.get(f"/status/{ingestion_id2}")
    
    # High priority should be processed first
    assert status2.json()["status"] in ["triggered", "completed"]
    if status1.json()["status"] == "completed":
        assert status2.json()["status"] == "completed"

def test_batch_processing_time():
    start_time = datetime.now()
    
    response = client.post(
        "/ingest",
        json={"ids": [1, 2, 3], "priority": "HIGH"}
    )
    ingestion_id = response.json()["ingestion_id"]
    
    # Wait for processing to complete
    status = "triggered"
    while status != "completed":
        response = client.get(f"/status/{ingestion_id}")
        status = response.json()["status"]
        time.sleep(1)
        
        # Ensure we don't wait forever
        if (datetime.now() - start_time).total_seconds() > 30:
            pytest.fail("Processing took too long")
    
    # Processing should take at least 5 seconds
    processing_time = (datetime.now() - start_time).total_seconds()
    assert processing_time >= 5

def test_batch_size():
    response = client.post(
        "/ingest",
        json={"ids": [1, 2, 3, 4, 5, 6, 7], "priority": "HIGH"}
    )
    ingestion_id = response.json()["ingestion_id"]
    
    response = client.get(f"/status/{ingestion_id}")
    batches = response.json()["batches"]
    
    # Check that batches contain maximum 3 IDs
    for batch in batches:
        assert len(batch["ids"]) <= 3

def test_status_transitions():
    response = client.post(
        "/ingest",
        json={"ids": [1, 2, 3], "priority": "HIGH"}
    )
    ingestion_id = response.json()["ingestion_id"]
    
    # Initial status should be yet_to_start or triggered
    response = client.get(f"/status/{ingestion_id}")
    initial_status = response.json()["status"]
    assert initial_status in ["yet_to_start", "triggered"]
    
    # Wait for completion
    while initial_status != "completed":
        response = client.get(f"/status/{ingestion_id}")
        initial_status = response.json()["status"]
        time.sleep(1)
    
    # Final status should be completed
    assert initial_status == "completed"
