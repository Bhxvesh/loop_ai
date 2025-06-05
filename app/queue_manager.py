import uuid
from datetime import datetime
from app.store import batch_status_store

# Job queue to process batches in order
job_queue = []

# Priority weights for ordering: lower is higher priority
priority_weight = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

def enqueue_batches(data, ingestion_id):
    now = datetime.utcnow().timestamp()
    batches = []

    for i in range(0, len(data.ids), 3):
        batch_ids = data.ids[i:i + 3]
        batch_id = str(uuid.uuid4())

        # Store batch status info
        batch_status_store[batch_id] = {
            "ingestion_id": ingestion_id,
            "ids": batch_ids,
            "status": "yet_to_start",
            "priority": data.priority,
            "created_time": now
        }

        # Enqueue batch in job queue
        job_queue.append({
            "batch_id": batch_id,
            "priority": priority_weight[data.priority],
            "created_time": now
        })

        # Append to ingestion record
        batches.append({
            "batch_id": batch_id,
            "ids": batch_ids,
            "status": "yet_to_start"
        })

    return batches

def sort_job_queue():
    job_queue.sort(key=lambda x: (x["priority"], x["created_time"]))
