from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from src.plugins.kpi.schema import KPIOverview

class MachineOverview(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    category: str = Field(...)
    name: str = Field(...)
    asset_id: str = Field(...)
    kpis_ids: List[PydanticObjectId] = Field(...)
    
class MachineDetail(MachineOverview):
    kpis: List[KPIOverview] = Field(...)


class MachineResponse(BaseModel):
    success: bool
    data: Optional[MachineDetail | List[MachineOverview]]  = None
    message: Optional[str] = None
