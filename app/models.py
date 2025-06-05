from pydantic import BaseModel, Field
from typing import List, Literal

class IngestRequest(BaseModel):
    ids: List[int] = Field(..., description="List of IDs to process")
    priority: Literal["HIGH", "MEDIUM", "LOW"]

    @property
    def valid_ids(self) -> bool:
        return all(1 <= id_ <= 10**9 + 7 for id_ in self.ids)

    model_config = {
        "json_schema_extra": {
            "example": {
                "ids": [1, 2, 3, 4, 5],
                "priority": "HIGH"
            }
        }
    }
