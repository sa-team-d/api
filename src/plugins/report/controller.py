from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request

from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.user.schema import User
from src.utils import get_collection

from .schema import Report, ReportResponse
from . import repository as repo

import os
API_VERSION = os.getenv("VERSION")
debug_mode = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/report", tags=["Report"])

with open("./src/plugins/report/report.txt", "r") as f:
    report_mock = f.read()

# create report
@router.post("/", status_code=201, response_model=Report, summary="Create a new report, save it to the database and return it")
async def create_report(request: Request, name: str, site: str, kpi_name:str, frequency: str, user: User = Depends(verify_firebase_token)):
    # This enpoint will be implemented in the next milestone
    pass
    # if user.get("role") == "SMO":
    #     if debug_mode: print("SMO Creating report")
    #     return Report(id=name, kpi_type=kpi, content=report_mock, date="2021-10-10", uid=user.get("uid"))
    # elif user.get("role") == "FFM":
    #     if debug_mode: print("FFM Creating report")
    #     return Report(id=name, kpi_type=kpi, content=report_mock, date="2021-10-10", uid=user.get("uid"))
    # else:
    #     raise HTTPException(status_code=403, detail="You do not have permission to create a report")

# get all reports from all sites
@router.get("/", status_code=200, response_model=ReportResponse, summary="Get all reports created by the user")
async def get_all_reports(request: Request, user: User = Depends(verify_firebase_token)):
    try:
        reports = await repo.reports_by_user_uid(request, user.get("uid"))
        print(f"User __D_D_D_:  {user.get('uid')}")
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# filter reports by site
@router.get("/filter", status_code=200, response_model=ReportResponse, summary="Get all reports for a specific machine created by the logged user")
async def get_reports_by_machine_id(request: Request, machine_id: str, user: User = Depends(verify_firebase_token)):
    try:
        print(f"User: {user.get('uid')}")
        if machine_id:
            reports = await repo.reports_by_machine_id(request, machine_id, user.get("uid"))
        else:
            return ReportResponse(success=False, data=None, message="No filter provided")
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))
