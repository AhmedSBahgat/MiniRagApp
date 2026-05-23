from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class DataChunk(BaseModel):

    id: Optional[ObjectId] = Field(default=None, alias="_id")

    chunk_text: str = Field(..., min_length=1)

    chunk_metadata: dict

    chunk_order: int = Field(..., ge=0)

    chunk_project_id: ObjectId

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
