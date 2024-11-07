"""KPI Controller.
This module contains the KPI API routes.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/kpi", tags=["KPI"])

@router.get("/", status_code=201, summary="Get all KPIs in the dataset")
async def get_all_kpis():
    pass

# create a new KPI
@router.post("/", status_code=201, summary="Create a new KPI")
async def create_kpi():
    pass

# update a KPI
@router.put("/{kpi_id}", status_code=201, summary="Update a KPI")
async def update_kpi():
    pass

# delete a KPI
@router.delete("/{kpi_id}", status_code=201, summary="Delete a KPI")
async def delete_kpi():
    pass
