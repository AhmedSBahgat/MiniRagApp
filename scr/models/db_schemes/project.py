from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId


class Project(BaseModel):

    id: Optional[ObjectId] = Field(default=None, alias="_id")

    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value):

        if not value.isalnum() or value.isspace():
            raise ValueError(
                "project_id must be a non-empty string "
                "containing only alphanumeric characters "
                "and no spaces."
            )

        return value

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "project_id_index_1",
                "unique": True,
            }
        ]
