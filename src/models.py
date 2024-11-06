"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""
from re import A
from tkinter import E
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

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

class Database (BaseModel):
    machines: Dict[str, Machine] = {}
    taxonomy: Any = {}