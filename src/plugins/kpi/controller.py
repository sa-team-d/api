from . import service
from datetime import datetime
from typing import List
from fastapi import APIRouter
import os
from src.models import Machine, ComputedValue, KPI

API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/machine", tags=["Machine"])

# list all machines
@router.get("/compute",status_code=200, response_model=list[ComputedValue], summary="Compute the value of the kpi")
def computeKPI(
    name: str, 
    kpi_name: str, 
    start_date: str,
    end_date: str,
    granularity_days: int,
    granularity_op: str
):
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        return service.computeKPI(name, kpi_name, start_date_obj, end_date_obj, granularity_days, granularity_op)
    except:
        print('error in filtering kpi')

@router.get("/",status_code=200, response_model=KPI, summary="Get kpi by name")
def getKPIByName(
    name: str
):
    try:
        return service.getKPIByName(name)
    except:
        print('error in getting kpi')

@router.get("/",status_code=200, response_model=KPI, summary="Get kpi by id") 
def getKPIById(
    id: str
):
    try:
        return service.getKPIById(id)
    except:
        print('error in getting kpi')

@router.get("/",status_code=200, response_model=KPI, summary="Create kpi")
def createKPI(
    name: str,
    formula: str
):
    try:
        service.createKPI(name, formula)
    except:
        print('error in creating kpi')