from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional, List

from pydantic_mongo import PydanticObjectId
from sympy import Union

from src.plugins.report.schema import ReportDetail, ReportOverview

class Anomaly(BaseModel):
    total_anomalies: str = Field(..., description="Anomaly number")
    anomalies_by_group: Dict = Field(..., description="Anomalies by group")

class AnomalyResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful")
    data: Optional[List[Anomaly]] = Field(..., description="Anomalies data")
    message: Optional[str] = Field(None, description="Response message")
