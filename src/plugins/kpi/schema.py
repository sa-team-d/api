from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime

class Value(BaseModel):
    sum: Optional[float] = None
    avg: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    datetime: Optional[datetime]
    machine_id: str

class Configuration(BaseModel):
    children: List[PydanticObjectId] = []
    formula: Optional[str]
    # alarms: list[Alarm]

class KPI(BaseModel):
    name: str = Field(...)
    type: Optional[str] = None
    description: Optional[str] = None
    unite_of_measure: Optional[str] = None
    data: Optional[List['Value']] = None
    config: Configuration = Field(...)
    
class ComputedValue(BaseModel):
    value: float = Field(...)
    
    


class KPIOverview(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str = Field(...)
    type: Optional[str] = None
    description: Optional[str] = None
    unite_of_measure: Optional[str] = None

class KPIDetail(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str = Field(...)
    type: Optional[str] = None
    description: Optional[str] = None
    unite_of_measure: Optional[str] = None
    config: Configuration = Field(...)
    
class CreateKPIBody(BaseModel):
    name: str
    type: str
    description: str
    unite_of_measure: str
    formula: str


class KPIResponse(BaseModel):
    success: bool
    data: Optional[KPIDetail | List[KPIOverview | ComputedValue]]  = None
    message: Optional[str] = None
