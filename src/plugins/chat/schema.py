from typing import List, Optional, Dict
from pandas import DataFrame
from pydantic import BaseModel, Field

class Analysis(BaseModel):
    cost_prediction: Dict = Field(..., description="Cost prediction")
    utilization: Dict = Field(..., description="Utilization analysis")
    energy_efficiency: Dict = Field(..., description="Energy efficiency analysis")

class ChatResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful")
    data: Optional[str | Analysis] = Field(..., description="Anomalies data")
    message: Optional[str] = Field(None, description="Response message")