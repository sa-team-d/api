from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, constr
from typing import Dict, Optional, List, Literal, Any

from datetime import datetime, timezone

class OperationalStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class KPICategory(str, Enum):
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"

class DashboardBase(BaseModel):
    production_rates: float = Field(ge=0, le=1000000, description="Production rate per hour")
    operational_status: OperationalStatus
    kpis: Dict[KPICategory, float] = Field(
        max_length=20,
        description="Key performance indicators"
    )
    site_id: constr(min_length=1, max_length=50)
    layout: Optional[Dict] = Field(default=None, max_length=5242880)  # 5MB limit
    filters: Optional[Dict] = Field(default=None, max_length=1024)

class DashboardCreate(DashboardBase):
    class Config:
        json_schema_extra = {
            "example": {
                "production_rates": 156.7,
                "operational_status": "running",
                "kpis": {"efficiency": 0.95},
                "site_id": "SITE_001"
            }
        }

class DashboardUpdate(DashboardBase):
    production_rates: Optional[float] = None
    operational_status: Optional[OperationalStatus] = None
    kpis: Optional[Dict[KPICategory, float]] = None
    site_id: Optional[str] = None

class DashboardResponse(DashboardBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Literal["success"] = "success"
    metadata: Dict[str, int] = Field(
        default_factory=lambda: {"version": 1}
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": "dash_123",
                    "production_rates": 156.7,
                    "operational_status": "running",
                    "kpis": {"efficiency": 0.95},
                    "site_id": "SITE_001",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
        }
        
        
        
        


class DashboardWidget(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the widget")
    type: str = Field(..., description="Type of the widget, e.g., chart, table, etc.")
    title: str = Field(..., description="Title of the widget")
    data_source: HttpUrl = Field(..., description="URL of the data source for the widget")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="Additional settings for the widget")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "widget_123",
                "type": "chart",
                "title": "Production Rate Chart",
                "data_source": "http://example.com/api/data/production_rate",
                "settings": {
                    "chart_type": "line",
                    "color": "blue"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }