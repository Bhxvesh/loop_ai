import asyncio
from app.store import batch_status_store

# Lock to ensure only one batch is processed at a time
processing_lock = asyncio.Lock()

async def process_batch(batch_id: str):
    # Update status to triggered
    batch_status_store[batch_id]["status"] = "triggered"

    # Simulate external API fetch (2 sec delay)
    await asyncio.sleep(2)

    # Enforce 5 sec processing window per batch
    await asyncio.sleep(3)

    # Update status to completed
    batch_status_store[batch_id]["status"] = "completed"
