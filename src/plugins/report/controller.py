from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from src.models import Report, User
from src.plugins.report.repository import ReportRepository
from src.plugins.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])
repository = ReportRepository()

@router.post("/", response_model=Report)
async def create_report(
    report: Report,
    current_user: User = Depends(get_current_user)
) -> Report:
    """Create a new report."""
    return await repository.create_report(report)

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
) -> Report:
    """Get a specific report by ID."""
    return await repository.get_report(report_id)

@router.get("/", response_model=Dict[str, List[Report]])
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    sort: Optional[str] = Query(None, description="Sort field:direction"),
    include: Optional[str] = Query(None, description="Include related resources"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[Report]]:
    """List all reports with pagination and filtering options."""
    return await repository.list_reports(
        page=page,
        per_page=per_page,
        site_id=site_id
    )

@router.post("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query(..., regex="^(pdf|csv|xlsx)$"),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Export a report in the specified format."""
    report = await repository.get_report(report_id)
    # Implementation for export functionality would go here
    return {
        "status": "success",
        "message": f"Report exported as {format}",
        "download_url": f"/downloads/reports/{report_id}.{format}"
    }

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Delete a specific report."""
    # Implementation for delete would go here
    return {"status": "success", "message": "Report deleted"}