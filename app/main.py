import uuid
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import IngestRequest
from app.store import ingestion_store, batch_status_store
from app.queue_manager import enqueue_batches, sort_job_queue, job_queue
from app.processor import processing_lock, process_batch

# Get port from environment variable for production
PORT = int(os.getenv("PORT", 8000))

app = FastAPI(
    title="Data Ingestion API",
    description="API system for batch processing data with priority queuing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest", 
         summary="Submit data for batch processing",
         response_description="Returns an ingestion ID for tracking")
async def ingest(data: IngestRequest, background_tasks: BackgroundTasks):
    # Validate ID range
    if not data.valid_ids:
        raise HTTPException(
            status_code=400,
            detail="IDs must be between 1 and 10^9+7"
        )
    
    ingestion_id = str(uuid.uuid4())
    batches = enqueue_batches(data, ingestion_id)

    # Store ingestion
    ingestion_store[ingestion_id] = {
        "ingestion_id": ingestion_id,
        "batches": batches
    }

    background_tasks.add_task(trigger_processing)

    return {"ingestion_id": ingestion_id}


@app.get("/status/{ingestion_id}",
         summary="Get status of an ingestion request",
         response_description="Returns the current status of the ingestion and its batches")
async def get_status(ingestion_id: str):
    if ingestion_id not in ingestion_store:
        raise HTTPException(
            status_code=404, 
            detail="Ingestion ID not found"
        )

    ingestion = ingestion_store[ingestion_id]
    batch_statuses = []

    statuses = []
    for batch in ingestion["batches"]:
        try:
            status = batch_status_store[batch["batch_id"]]["status"]
            batch["status"] = status
            batch_statuses.append(batch)
            statuses.append(status)
        except KeyError:
            raise HTTPException(
                status_code=500,
                detail=f"Batch {batch['batch_id']} status not found"
            )

    # Determine overall status based on batch statuses
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


# Root endpoint for health check
@app.get("/",
         summary="Root endpoint",
         response_description="Returns OK if the service is running")
async def root():
    return {"status": "OK", "message": "Data Ingestion API is running"}

# Health check endpoint
@app.get("/health",
         summary="Health check endpoint",
         response_description="Returns OK if the service is healthy")
async def health_check():
    return {"status": "OK"}
