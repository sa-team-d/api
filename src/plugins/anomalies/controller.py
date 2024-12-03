import os
import logging

from sqlalchemy import func

from . import service
from .schema import Anomaly, AnomalyResponse
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token

import pandas as pd
from firebase_admin import storage

logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

router = APIRouter(prefix=f"/api/{API_VERSION}/anomalies", tags=["Anomalies"])

# get anomalies
@router.post("/", status_code=200, response_model=AnomalyResponse, summary="Get all anomalies")
async def getAnomalies(
    request: Request,
    anomaly_type: Union[List[str], str] = 'energy',
    user=Depends(verify_firebase_token)
):
    """
    Get all anomalies for the specified KPIs.
    Args:
    - anomaly_type (Union[List[str], str], optional): The type of anomaly to detect. Possible anomaly values are ['energy', 'downtime', 'cycle_quality'].
    Returns:
    - AnomalyResponse: Anomaly response object containing the anomalies data.
    """
    results = []
    try:
        if isinstance(anomaly_type, list):
            for anomaly in anomaly_type:
                try:
                    function_name = f"analyze_{anomaly}_anomalies"
                    n, data = service.__getattribute__(function_name)()
                    for k,v in data.items():
                        data[k] = str(v)
                        print(type(v))
                    results.append(Anomaly(total_anomalies=str(n), anomalies_by_group=data))
                except Exception as e:
                    print(e)
                    results.append(Anomaly(total_anomalies="Not Avaiable", anomalies_by_group = {}))
        else:
            function_name = f"analyze_{anomaly_type}_anomalies"
            n, data = service.__getattribute__(function_name)()
            for k,v in data.items():
                data[k] = str(v)
            results.append(Anomaly(total_anomalies=str(n), anomalies_by_group=data))
        return AnomalyResponse(success=True, data=results, message="Anomalies detected successfully")
    except Exception as e:
        print(e)
        return AnomalyResponse(success=False, data=None, message=f"Error getting anomalies: {str(e)}")