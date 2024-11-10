from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from src.models import Report, User
from src.plugins.report.repository import ReportRepository
from src.plugins.auth.firebase import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])
repository = ReportRepository()

# create report
@router.post("/", status_code=201, summary="Create a new report")
async def create_report(user: User = Depends(get_current_user)):
    pass

# get all reports
@router.get("/", response_model=List[Report], status_code=201, summary="Get all reports")
async def get_all_reports(user: User = Depends(get_current_user)):
    pass

# get report by ID
@router.get("/{report_id}", response_model=Report, status_code=201, summary="Get report by ID")
async def get_report_by_id(report_id: str, user: User = Depends(get_current_user)):
    pass

# get report by time
@router.get("/time", response_model=List[Report], status_code=201, summary="Get report by time")
async def get_report_by_time(start_time: str, end_time: str, user: User = Depends(get_current_user)):
    pass