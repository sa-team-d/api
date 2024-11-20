"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""
from platform import machine
from re import A
from tkinter import E
from typing import List
from pydantic import BaseModel, Field, EmailStr
from pydantic_mongo import PydanticObjectId
from typing import Dict, Optional, Any
from datetime import date, datetime
from enum import Enum

class User(BaseModel):
    uid: str # The user's ID firebase
    email: EmailStr
    site : int # if ffm, else none
    name: str
    phone_number: str

class Report (BaseModel):
    id: str
    kpi_type: str
    content: str
    date: datetime
    uid: str

class Value(BaseModel):
    machine_id: str
    sum: float
    avg : float
    min: float
    max: float
    var: float

class Alarm(BaseModel):
    text: str
    date: datetime
    threshold: float
    formula: str
    machine_id: str
    #uid: str # we need to ensure that only the uid get the alarm

class KPIGroup(BaseModel):
    name: str
    kpi_list: list['KPI']

class Machine(BaseModel):
    id: str
    category: str
    name: str
    kpi_list: list['KPI']
    
class ComputedValue(BaseModel):
    value: float = Field(...)

class Kpi(BaseModel):
    kpi_type: str
    data: list[Value]
    machine_id: str
    config : dict

class Value(BaseModel):
    sum: Optional[float] = None
    avg: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    datetime: Optional[datetime]
    machine_id: str

class Configuration(BaseModel):
    children: List[PydanticObjectId] = Field(...)
    formula: Optional[str]
    alarms: list[Alarm]

class KPI(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str = Field(...)
    type: Optional[str] = None
    description: Optional[str] = None
    unite_of_measure: Optional[str] = None
    data: Optional[List['Value']] = None
    config: Configuration = Field(...)