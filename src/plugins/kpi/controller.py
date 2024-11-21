import os
from . import service
from typing import List
from datetime import datetime
from .schema import ComputedValue, KPI, KPIOverview, CreateKPIBody
from fastapi import APIRouter, HTTPException

API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/kpi", tags=["Machine"])

# Compute kpi
@router.get("/compute",status_code=200, response_model=list[ComputedValue], summary="Compute the value of the kpi")
def computeKPI(
    machine_id: str, 
    kpi_name: str, 
    start_date: str,
    end_date: str,
    granularity_days: int,
    granularity_op: str
):
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        return service.computeKPI(machine_id, kpi_name, start_date_obj, end_date_obj, granularity_days, granularity_op)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing kpi -> {e}")

@router.get("/",status_code=200, response_model=List[KPIOverview], summary="List kpis")
def listKPI():
    try:
        return service.listKPIs()
    except:
        raise HTTPException(status_code=400, detail="Error list kpi")

@router.get("/:id",status_code=200, response_model=KPI, summary="Get kpi by id") 
def getKPIById(
    id: str
):
    try:
        return service.getKPIById(id)
    except:
        raise HTTPException(status_code=400, detail="Error getting kpi")

@router.post("/", status_code=200, response_model=KPI, summary="Create kpi")
def createKPI(
    item: CreateKPIBody
):
    try:
        service.createKPI(
            item.name,
            item.type,
            item.description,
            item.unite_of_measure,
            item.formula
        )
    except:
        raise HTTPException(status_code=400, detail="Error creating kpi")