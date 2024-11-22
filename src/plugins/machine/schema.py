from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List

class Machine(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    category: str = Field(...)
    name: str = Field(...)
    asset_id: str = Field(...)
    kpis_ids: List[PydanticObjectId] = Field(...)