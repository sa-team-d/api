from fastapi import APIRouter, HTTPException, Depends
from src.models import Report
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.models import User

import os
API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/report", tags=["Report"])

# create report
@router.post("/", status_code=201, response_model=Report, summary="Create a new report, save it to the database and return it")
async def create_report(name: str, site: str, kpi:str, frequency: str, user: User = Depends(verify_firebase_token)):
    if user.get("role") == "SMO":
        print("SMO Creating report")
        # create report for a specific site
        data = f"Prova Report SMO: {name} {site} {kpi} {frequency}"
        return Report(id=name, kpi_type=kpi, content=data, date="2021-10-10", uid=user.get("uid"))
    elif user.get("role") == "FFM":
        # create report for a specific site
        # create report for a specific site
        data = f"Prova Report FFM: {name} {site} {kpi} {frequency}"
        return Report(id=name, kpi_type=kpi, content=data, date="2021-10-10", uid=user.get("uid"))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create a report")

# get all reports from all sites
@router.get("/", status_code=200, response_model=list[Report], summary="Get all reports created by the user")
async def get_all_reports(site: str, user: User = Depends(verify_firebase_token)):
    raise HTTPException(status_code=404, detail="Not implemented")

# filter reports by site
@router.get("/filter", status_code=200, response_model=list[Report], summary="Get all reports for a specific site created by the user")
async def get_reports_by_site(site: str, user: User = Depends(verify_firebase_token_and_role("SMO"))):
    raise HTTPException(status_code=404, detail="Not implemented")
