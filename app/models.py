from pydantic import BaseModel
from typing import List, Literal

class IngestRequest(BaseModel):
    ids: List[int]
    priority: Literal["HIGH", "MEDIUM", "LOW"]
