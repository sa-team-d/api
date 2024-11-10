from fastapi import APIRouter, HTTPException, Depends, Query
from src.models import Report
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.models import User

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

# create report
@router.post("/", status_code=201, response_model=Report, summary="Create a new report, save it to the database and return it")
async def create_report(name: str, site: str, kpi:list[str], frequency: str, user: User = Depends(verify_firebase_token)):
    if user.role == "SMO":
        print("SMO Creating report")
        # create report for a specific site
        pass
    elif user.role == "FFM":
        # create report for a specific site
        pass
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create a report")

# get all reports from all sites
@router.get("/", status_code=201, response_model=list[Report], summary="Get all reports created by the user")
async def get_all_reports(site: str, user: User = Depends(verify_firebase_token_and_role("SMO"))):
    # check uid creator of the report
    pass


# filter reports by site
@router.post("/site", status_code=201, response_model=list[Report], summary="Get all reports for a specific site created by the user")
async def get_reports_by_site(site: str, user: User = Depends(verify_firebase_token_and_role("SMO"))):
    # check uid creator of the report
    pass
