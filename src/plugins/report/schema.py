from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from pydantic_mongo import PydanticObjectId

from src.plugins.site.schema import SiteOverviewWithKPIs

class ReportAbstract(BaseModel):
    kpi_names: list[str] = Field(..., description="Names of the KPIs being reported")
    name: str = Field(..., description="Report name")
    start_date: datetime = Field(default_factory=datetime.now, description="Start date of the report")
    end_date: datetime = Field(default_factory=datetime.now, description="End date of the report")
    user_uid: str = Field(..., description="User identifier who created the report")
    url:str = Field(..., description="URL to the report")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "kpi_names": ["some kpi"],
                "name": "Monthly something",
                "start_date": "2024-03-01T00:00:00",
                "end_date": "2024-03-31T23:59:59",
                "user_uid": "user123",
                "url": "https://example.com/reports/monthly-revenue-report.pdf"
            }
        }


class Report(ReportAbstract):
    sites_id: List[int] = Field(..., description="Asset identifier(s) associated with the report")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "kpi_names": ["some kpi"],
                "name": "Monthly something",
                "start_date": "2024-03-01T00:00:00",
                "end_date": "2024-03-31T23:59:59",
                "user_uid": "user123",
                "url": "https://example.com/reports/monthly-revenue-report.pdf",
                "sites_id": ["12", "1"]
            }
        }

class ReportDetail(Report):
    id: PydanticObjectId = Field(alias="_id")

class ReportOverview(ReportAbstract):
    id: PydanticObjectId = Field(alias="_id")
    sites: Optional[List[SiteOverviewWithKPIs]] = Field(default=None, description="List of machines associated with the report")

class ReportResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful")
    data: Optional[ReportDetail | ReportOverview | List[ReportDetail] | List[ReportOverview] | str] = Field(None, description="Response data containing report information")
    message: Optional[str] = Field(None, description="Response message")