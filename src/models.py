"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class MachineStatus(str, Enum):
    RUNNING = "running"
    IDLE = "idle"
    MAINTENANCE = "maintenance"

class UserRole_E(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    VIEWER = "viewer"
    SERVICE = "service"

class User(BaseModel):
    uid: str
    email: EmailStr
    role: UserRole_E
    permissions: List[str] = []
    settings: Dict = Field(default_factory=dict)

class UserRole(BaseModel):
    user_id: str
    roles: List[str]

class Machine(BaseModel):
    id: str
    name: str
    status: MachineStatus
    energy_consumption: float = Field(ge=0)
    performance_data: Dict[str, float]
    site_id: str
    description: Optional[str] = None
    tags: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "machine-001",
                "name": "Production Line 1",
                "status": "running",
                "energy_consumption": 45.6,
                "performance_data": {
                    "cycle_time": 120,
                    "downtime": 15,
                    "throughput": 100
                },
                "site_id": "site-001",
                "tags": ["production", "assembly"]
            }
        }

class Report(BaseModel):
    id: str
    type: str
    data: Dict
    generated_at: datetime
    site_id: str
    generated_by: str
    title: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "report-001",
                "type": "productivity",
                "data": {
                    "metrics": {},
                    "summary": {}
                },
                "generated_at": "2024-03-19T10:00:00Z",
                "site_id": "site-001",
                "generated_by": "user-001"
            }
        }

class Dashboard(BaseModel):
    production_rates: float = Field(ge=0)
    operational_status: str
    kpis: Dict[str, float]
    site_id: str
    layout: Optional[Dict] = None
    filters: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "production_rates": 85.5,
                "operational_status": "normal",
                "kpis": {
                    "oee": 78.5,
                    "availability": 92.0
                },
                "site_id": "site-001",
                "layout": {
                    "widgets": []
                }
            }
        }


class DashboardUpdate(BaseModel):
    production_rates: Optional[float] = Field(ge=0)
    operational_status: Optional[str]
    kpis: Optional[Dict[str, float]]
    layout: Optional[Dict] = None
    filters: Optional[Dict] = None