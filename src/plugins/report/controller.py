from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from sympy import content

from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.user.schema import User
from src.utils import get_collection

from .schema import Report, ReportResponse
from . import repository as repo
from openai import OpenAI

import os
API_VERSION = os.getenv("VERSION")
debug_mode = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/report", tags=["Report"])

with open("./src/plugins/report/report.txt", "r") as f:
    report_mock = f.read()

# create report
@router.post("/", status_code=201, response_model=Report, summary="Create a new report, save it to the database and return it")
async def create_report(request: Request, name: str, site: str, kpi_names:str , frequency: str, start_date:str, end_date:str, user: User = Depends(verify_firebase_token)):

    # 1. Get corrispondent kpi data from the kpi service
    # 2. Compute the report with the kpi data as input

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You generate systematic reports for kpis."},
            {"role": "user", "content": "I would like to generate a report for the kpi: " + kpi_names + " for the site: " + site + " for the frequency: " + frequency}
        ]
    )
    # 1.save the report on google drive
    # 2.save the report url to the database
    # 3.return the report url
    
    return Report(kpi_name=kpi_names, content=str(completion.choices[0].message.content), user_uid=user.uid, asset_id=[site])

# get all reports from all sites
@router.get("/", status_code=200, response_model=ReportResponse, summary="Get all reports created by the user")
async def get_all_reports(request: Request, user: User = Depends(verify_firebase_token)):
    try:
        reports = await repo.reports_by_user_uid(request, user.uid)
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# filter reports by site
@router.get("/filter", status_code=200, response_model=ReportResponse, summary="Get all reports for a specific machine created by the logged user")
async def get_reports_by_machine_id(request: Request, machine_id: str, user: User = Depends(verify_firebase_token)):
    try:
        if machine_id:
            reports = await repo.reports_by_machine_id(request, machine_id, user.uid)
        else:
            return ReportResponse(success=False, data=None, message="No filter provided")
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))
