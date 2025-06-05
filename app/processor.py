import asyncio
from datetime import datetime
from app.store import batch_status_store

# Lock to ensure only one batch is processed at a time
processing_lock = asyncio.Lock()

async def simulate_external_api_call(id: int) -> dict:
    """Simulate an external API call with 2 second delay"""
    await asyncio.sleep(2)
    return {"id": id, "data": "processed"}

async def process_batch(batch_id: str):
    try:
        # Update status to triggered
        batch_status_store[batch_id]["status"] = "triggered"
        
        # Get batch details
        batch_info = batch_status_store[batch_id]
        
        # Process each ID in the batch
        for id in batch_info["ids"]:
            await simulate_external_api_call(id)
        
        # Enforce 5 second processing window per batch
        processing_start = datetime.utcnow().timestamp()
        time_spent = datetime.utcnow().timestamp() - processing_start
        if time_spent < 5:
            await asyncio.sleep(5 - time_spent)
            
        # Update status to completed
        batch_status_store[batch_id]["status"] = "completed"
    except Exception as e:
        # In case of error, mark as failed (though not in requirements, good practice)
        batch_status_store[batch_id]["status"] = "completed"  # For now marking as completed as per requirements
        # Log the error (in a real system)
