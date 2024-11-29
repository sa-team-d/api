from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime


class Site(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    machines_ids: List[PydanticObjectId] = []
    kpis_ids: List[PydanticObjectId] = []
    site_id: int