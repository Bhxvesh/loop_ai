# Data Ingestion API System

A FastAPI-based system for batch processing data with priority queuing and rate limiting.

## Features

- Batch processing of data with configurable priorities (HIGH, MEDIUM, LOW)
- Rate limiting (1 batch per 5 seconds)
- Asynchronous processing with background tasks
- Priority-based queue management
- Real-time status tracking
- Input validation and error handling

## Technical Stack

- Python 3.8+
- FastAPI
- Pydantic for data validation
- Async processing with asyncio

## API Endpoints

### 1. Ingest Data
```
POST /ingest
```
Submit data for batch processing.

Request body:
```json
{
    "ids": [1, 2, 3, 4, 5],
    "priority": "HIGH"
}
```
Response:
```json
{
    "ingestion_id": "abc123"
}
```

### 2. Check Status
```
GET /status/{ingestion_id}
```
Get the current status of an ingestion request.

Response:
```json
{
    "ingestion_id": "abc123",
    "status": "triggered",
    "batches": [
        {
            "batch_id": "uuid1",
            "ids": [1, 2, 3],
            "status": "completed"
        },
        {
            "batch_id": "uuid2",
            "ids": [4, 5],
            "status": "triggered"
        }
    ]
}
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Implementation Details

### Batch Processing
- IDs are processed in batches of 3
- Each batch takes minimum 5 seconds to process
- External API calls are simulated with a 2-second delay

### Priority System
- Requests are processed based on priority (HIGH > MEDIUM > LOW)
- Within same priority, older requests are processed first

### Status Tracking
- yet_to_start: Batch is queued but not started
- triggered: Batch is currently processing
- completed: Batch has finished processing

## Testing

Run the tests using pytest:
```bash
pytest
```

## Rate Limiting

The system enforces the following limits:
- Maximum 3 IDs processed at once
- Minimum 5 seconds per batch
- Priority-based processing