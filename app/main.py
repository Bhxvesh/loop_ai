import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.models import IngestRequest
from app.store import ingestion_store, batch_status_store
from app.queue_manager import enqueue_batches, sort_job_queue, job_queue
from app.processor import processing_lock, process_batch

app = FastAPI()

@app.post("/ingest")
async def ingest(data: IngestRequest, background_tasks: BackgroundTasks):
    ingestion_id = str(uuid.uuid4())
    batches = enqueue_batches(data, ingestion_id)

    # Store ingestion
    ingestion_store[ingestion_id] = {
        "ingestion_id": ingestion_id,
        "batches": batches
    }

    background_tasks.add_task(trigger_processing)

    return {"ingestion_id": ingestion_id}


@app.get("/status/{ingestion_id}")
async def get_status(ingestion_id: str):
    if ingestion_id not in ingestion_store:
        raise HTTPException(status_code=404, detail="Ingestion ID not found")

    ingestion = ingestion_store[ingestion_id]
    batch_statuses = []

    statuses = []
    for batch in ingestion["batches"]:
        status = batch_status_store[batch["batch_id"]]["status"]
        batch["status"] = status
        batch_statuses.append(batch)
        statuses.append(status)

    if all(s == "yet_to_start" for s in statuses):
        overall_status = "yet_to_start"
    elif all(s == "completed" for s in statuses):
        overall_status = "completed"
    else:
        overall_status = "triggered"

    return {
        "ingestion_id": ingestion_id,
        "status": overall_status,
        "batches": batch_statuses
    }


async def trigger_processing():
    async with processing_lock:
        sort_job_queue()
        while job_queue:
            job = job_queue.pop(0)
            await process_batch(job["batch_id"])
