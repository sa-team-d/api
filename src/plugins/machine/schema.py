"""
Define the schema for the response. This is the data that will be returned by the API.
"""
from pydantic import BaseModel
from typing import List, Optional

class MachineCreate(BaseModel):
    name: str
    type: str

class Machine(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    tags: List[str] = []

    class Config:
        orm_mode: bool = True