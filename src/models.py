"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""
from platform import machine
from re import A
from tkinter import E
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Optional, Any
from datetime import date, datetime
from enum import Enum

class Reports (BaseModel):
    id: str
    type: str
    content: str
    date: datetime

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

class Kpi(BaseModel):
    type: str
    data: list[Value]
    machine_id: str
    config : dict

class Config(BaseModel):
    children: list[Kpi]
    formula: str
    alarms: list[Alarm]

class KPIGroup(BaseModel):
    name: str
    kpi_list: list[Kpi]

class Configuration(BaseModel):
    children: list[Kpi]
    formula: str
    alarms: list[Alarm]

class Machine(BaseModel):
    id: str
    category: str
    name: str
    kpi_list: list[Kpi]