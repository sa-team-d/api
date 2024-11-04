"""
Define the schema for the response. This is the data that will be returned by the API.
"""
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Base schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"




# Machine schemas
class MachineBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    tags: List[str] = []

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class Machine(MachineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    configuration: Optional[Dict[str, Any]] = None

    class Config:
        from_mode = True

class MachineList(BaseModel):
    items: List[Machine]
    total: int
    page: int
    per_page: int
    pages: int