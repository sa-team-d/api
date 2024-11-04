from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    PRODUCTIVITY = "productivity"
    ENERGY = "energy"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"

class ReportFilter(BaseModel):
    start_date: datetime
    end_date: datetime
    site_id: Optional[str] = None
    machine_id: Optional[str] = None
    kpi_ids: Optional[List[str]] = None

class ReportBase(BaseModel):
    type: ReportType
    title: str
    description: Optional[str] = None
    filters: ReportFilter
    config: Optional[Dict] = Field(default_factory=dict)
    site_id: str

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: str
    generated_at: datetime
    generated_by: str
    data: Dict
    status: str = "completed"
    download_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "report-123",
                "type": "productivity",
                "title": "Monthly Productivity Report",
                "description": "Productivity analysis for March 2024",
                "filters": {
                    "start_date": "2024-03-01T00:00:00Z",
                    "end_date": "2024-03-31T23:59:59Z",
                    "site_id": "site-001"
                },
                "generated_at": "2024-03-31T23:59:59Z",
                "generated_by": "user-123",
                "data": {
                    "metrics": {},
                    "charts": {},
                    "summary": {}
                },
                "status": "completed",
                "download_url": "/downloads/reports/report-123.pdf"
            }
        }