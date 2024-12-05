from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from pydantic_mongo import PydanticObjectId

from src.plugins.machine.schema import MachineOverview

class ReportAbstract(BaseModel):
    kpi_name: str = Field(..., description="Name of the KPI being reported")
    content: str = Field(..., description="Report content/description")
    date: datetime = Field(default_factory=datetime.now, description="Report creation date")
    user_uid: str = Field(..., description="User identifier who created the report")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "kpi_name": "Monthly Revenue",
                "content": "Revenue increased by 15% compared to last month",
                "date": "2024-03-20T10:00:00",
                "user_uid": "user123",
            }
        }


class Report(ReportAbstract):
    asset_id: List[str] = Field(..., description="Asset identifier(s) associated with the report")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "kpi_name": "Monthly Revenue",
                "content": "Revenue increased by 15% compared to last month",
                "date": "2024-03-20T10:00:00",
                "user_uid": "user123",
                "asset_id": ["ast-anxkweo01vv2"]
            }
        }

class ReportDetail(Report):
    id: PydanticObjectId = Field(alias="_id")

class ReportOverview(ReportAbstract):
    id: PydanticObjectId = Field(alias="_id")
    machines: Optional[List[MachineOverview]] = Field(default=None, description="List of machines associated with the report")

class ReportResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful")
    data: Optional[ReportDetail | ReportOverview | List[ReportDetail] | List[ReportOverview] | str] = Field(None, description="Response data containing report information")
    message: Optional[str] = Field(None, description="Response message")