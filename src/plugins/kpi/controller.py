"""KPI Controller.
This module contains the KPI API routes.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/kpi", tags=["KPI"])

@router.get("/", status_code=201, summary="Get all KPIs in the dataset")
async def get_all_kpis():
    pass

# get all kpi of a group
@router.get("/group/", status_code=201, summary="Get all KPIs of a group")
async def get_kpis_by_group(group_name: str):
    pass

# set threshold for a kpi
@router.put("/threshold/", status_code=201, summary="Set threshold for a KPI")
async def set_threshold(kpi_id: str, threshold: float):
    pass
