"""KPI Controller.
This module contains the KPI API routes.
"""
from fastapi import APIRouter, Depends
from src.models import KPIGroup, Kpi
from src.plugins.auth.firebase import verify_firebase_token

import os
API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/kpi", tags=["KPI"])

# name from all kpis
@router.get("/", status_code=200, response_model=list[KPIGroup], summary="Get all KPIs avaiable")
async def get_all_kpis(user = Depends(verify_firebase_token)):
    pass

# get all kpi with a name - select kpi.name
@router.get("/filter", status_code=200, response_model=list[Kpi], summary="Get all KPIs with a name")
async def get_kpis_by_group(kpi_name: str, start_date:str, end_date:str, user=Depends(verify_firebase_token), site_name: str = None):
    if user.role == "FFM":
        # get all kpis with the name from the site
        pass
    elif user.role == "SMO":
        # get all kpis with the name
        pass

# set threshold for a kpi
@router.post("/threshold/", status_code=201, summary="Set threshold for a KPI")
async def set_threshold(kpi_name: str, threshold: float):
    pass

# create a new kpi
@router.post("/", status_code=201, response_model=Kpi, summary="Create a new KPI")
async def create_kpi(name: str, description: str, group: str, user=Depends(verify_firebase_token)):
    pass
