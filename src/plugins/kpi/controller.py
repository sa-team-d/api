"""KPI Controller.
This module contains the KPI API routes.
"""
import site
from fastapi import APIRouter, Depends

from src.models import KPIGroup, Kpi
from src.plugins.auth.firebase import verify_firebase_token

router = APIRouter(prefix="/api/v1/kpi", tags=["KPI"])

# name from all kpis
@router.get("/", status_code=201, response_class=list[KPIGroup], summary="Get all KPIs avaiable")
async def get_all_kpis(user = Depends(verify_firebase_token)):
    if user.role == "FFM":
        # get all kpis the site
        pass
    elif user.role == "SMO":
        # get all kpis with the name
        pass

# get all kpi with a name - select kpi.name
@router.post("/filter", status_code=201, response_class=list[Kpi], summary="Get all KPIs with a name")
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
