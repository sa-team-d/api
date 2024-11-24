import os
import logging

from . import service
from typing import List, Optional
from datetime import datetime
from .schema import (
        ComputedValue, KPIDetail, KPIOverview, CreateKPIBody, KPIResponse
    )
from fastapi import APIRouter, HTTPException, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token


logger = logging.getLogger(__name__)
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/kpi", tags=["Kpi"])


# Compute kpi
@router.get("/compute",status_code=200, response_model=KPIResponse, summary="Compute the value of the kpi")
def computeKPI(
    request: Request,
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
        try:
            res = service.computeKPI(request, machine_id, kpi_id, start_date_obj, end_date_obj, granularity_days, granularity_op)
            return KPIResponse(success=True, data=res, message="KPI computed successfully")
        except Exception as e:
            return KPIResponse(success=False, data=None, message=f"Error computing kpi: {e}")
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error computing kpi: {e}")

@router.get("/",status_code=200, response_model=KPIResponse, summary="List kpis")
def listKPI(request: Request, user=Depends(verify_firebase_token)):
    try:
        all_kpi: List[KPIOverview] = service.listKPIs(request)
        return KPIResponse(success=True, data=all_kpi, message="KPIs listed successfully")
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error listing kpis: {e}")
        


@router.post("/", status_code=200, response_model=KPIResponse, summary="Create kpi")
def createKPI(
    request: Request,
    item: CreateKPIBody,
    user=Depends(verify_firebase_token)
):
    try:
        exist = service.getKPIByName(request, item.name)
        if exist:
            return KPIResponse(success=False, data=None, message="KPI already exists")
        
        result: Optional[KPIDetail] = service.createKPI(
            request,
            item.name,
            item.type,
            item.description,
            item.unite_of_measure,
            item.formula
        )
        return KPIResponse(success=True, data=result, message="KPI created successfully")
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error creating kpi: {e}")
    
@router.delete("/:id", status_code=200, response_model=KPIResponse, summary="Delete kpi")
def deleteKPI(
    request: Request,
    id: str,
    user=Depends(verify_firebase_token)
):
    try:
        success = service.deleteKPIByID(request, id)
        return KPIResponse(
            success=success,
            message="KPI deleted successfully" if success else "KPI not found",
            data=None
        )
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error deleting kpi: {e}")

@router.delete("/:name", status_code=200, response_model=KPIResponse, summary="Delete kpi by name")
def deleteKPIByName(
    request: Request,
    name: str,
    user=Depends(verify_firebase_token)
):
    try:
        success = service.deleteKPIByName(request, name)
        return KPIResponse(
            success=success,
            message="KPI deleted successfully" if success else "KPI not found",
            data=None
        )
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error deleting kpi: {e}")


@router.get("/:name", status_code=200, response_model=KPIResponse, summary="Get kpi by name")
def getKPIByName(
    request: Request,
    name: str,
    user=Depends(verify_firebase_token)
):
    try:
        logger.info(f"Getting kpi with name {name}")
        kpi = service.getKPIByName(request, name)
        if kpi:
            return KPIResponse(success=True, data=kpi)
        return KPIResponse(success=False, message=f"KPI with name {name} not found")
    except Exception as e:
        return KPIResponse(success=False, data=None, message=f"Error getting kpi: {e}")

@router.get("/:id", status_code=200, response_model=KPIResponse, summary="Get kpi by id")
def getKPIById(
    request: Request,
    id: str,
    user=Depends(verify_firebase_token)
):
    try:
        kpi = service.getKPIById(request, id)
        if kpi:
            return KPIResponse(success=True, data=kpi)
        return KPIResponse(success=False, message=f"KPI with id {id} not found")
    except Exception as e:
        return  KPIResponse(success=False, data=None, message=f"Error getting kpi: {e}")