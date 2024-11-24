"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""
from pydantic import BaseModel, EmailStr
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
    kpi_list: list['Kpi']
    

class Kpi(BaseModel):
    id: str
    kpi_type: str
    data: list[Value]
    machine_id: str
    config : dict
