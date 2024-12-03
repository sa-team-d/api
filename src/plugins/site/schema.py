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
    
class KPIOverview(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str

class SiteOverviewWithKPIs(Site):
    kpis: List[KPIOverview]
    
class SiteResponse(BaseModel):
    success: bool
    data: Optional[Site | List[Site]] = None
    message: Optional[str] = None