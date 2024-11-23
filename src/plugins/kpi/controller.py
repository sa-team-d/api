import os
from . import service
from typing import List
from datetime import datetime
from .schema import ComputedValue, KPIDetail, KPIOverview, CreateKPIBody
from fastapi import APIRouter, HTTPException, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token

API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/kpi", tags=["Kpi"])

def http_exception(status_code, detail, e):
    if DEBUG:
        detail = f"{detail} -> {e}"
    raise HTTPException(status_code=status_code, detail=detail)

# Compute kpi
@router.get("/compute",status_code=200, response_model=list[ComputedValue], summary="Compute the value of the kpi")
def computeKPI(
    machine_id: str,
    kpi_id: str,
    start_date: str,
    end_date: str,
    granularity_days: int,
    granularity_op: str,
    user=Depends(verify_firebase_token)
):
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        return  service.computeKPI(machine_id, kpi_id, start_date_obj, end_date_obj, granularity_days, granularity_op)
    except Exception as e:
        raise http_exception(400, "Error computing kpi", e)

@router.get("/",status_code=200, response_model=List[KPIOverview], summary="List kpis")
def listKPI(request: Request, user=Depends(verify_firebase_token)):
    try:
        return service.listKPIs(request)
    except Exception as e:
        raise http_exception(400, "Error listing kpis", e)
        

@router.get("/:id",status_code=200, response_model=KPIDetail, summary="Get kpi by id")
def getKPIById(
    request: Request,
    id: str,
    user=Depends(verify_firebase_token)
):
    try:
        return service.getKPIById(request, id)
    except Exception as e:
        raise http_exception(400, "Error getting kpi", e)

@router.post("/", status_code=200, response_model=KPIDetail, summary="Create kpi")
def createKPI(
    request: Request,
    item: CreateKPIBody,
    user=Depends(verify_firebase_token)
):
    try:
        service.createKPI(
            request,
            item.name,
            item.type,
            item.description,
            item.unite_of_measure,
            item.formula
        )
    except Exception as e:
        raise http_exception(400, "Error creating kpi", e)