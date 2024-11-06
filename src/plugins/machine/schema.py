"""
Define the schema for the response. This is the data that will be returned by the API.
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, Optional

class MachineData(BaseModel):
    working_time: int
    idle_time: int
    offline_time: int
    consumption: float
    power: float
    cost: float
    consumption_working: float
    consumption_idle: float
    cycles: int
    good_cycles: int
    bad_cycles: int
    average_cycle_time: float

class Machine(BaseModel):
    id: str
    type: str
    data: MachineData

