from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Dict, List, Optional
from src.plugins.dashboard import schema
from src.plugins.auth.firebase import get_current_user, check_permissions
from src.models import User
from src.core.pagination import PaginationParams
from src.plugins.dashboard.repository import DashboardRepository

router = APIRouter(prefix="/api/v1", tags=["Dashboard"])

@router.get("/dashboards")
async def list_dashboards(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query(None, pattern="^[a-zA-Z_]+:(asc|desc)$"),
    filter: Optional[str] = Query(None),
    fields: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[schema.DashboardResponse]]:
    pagination = PaginationParams(page=page, per_page=per_page)
    filters = dict(item.split(":") for item in filter.split(",")) if filter else None
    fields_list = fields.split(",") if fields else None

    return await DashboardRepository().list_dashboards(
        pagination=pagination,
        filters=filters,
        sort=sort,
        fields=fields_list
    )

@router.post("/dashboards")
async def create_dashboard(
    dashboard: schema.DashboardCreate,
    current_user: User = Depends(get_current_user)
) -> schema.DashboardResponse:
    await check_permissions(current_user, ["dashboard:create"])
    return await DashboardRepository().create_dashboard(dashboard)

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str = Path(..., min_length=1),
    current_user: User = Depends(get_current_user)
) -> schema.DashboardResponse:
    return await DashboardRepository().get_dashboard(dashboard_id)

@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    dashboard: schema.DashboardUpdate,
    current_user: User = Depends(get_current_user)
) -> schema.DashboardResponse:
    await check_permissions(current_user, ["dashboard:update"])
    return await DashboardRepository().update_dashboard(dashboard_id, dashboard)

@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    await check_permissions(current_user, ["dashboard:delete"])
    await DashboardRepository().delete_dashboard(dashboard_id)
    return {"status": "success", "message": "Dashboard deleted"}

@router.post("/dashboards/{dashboard_id}/widgets")
async def add_widget(
    dashboard_id: str,
    widget: schema.DashboardWidget,
    current_user: User = Depends(get_current_user)
) -> Dict:
    await check_permissions(current_user, ["dashboard:update"])
    dashboard = await DashboardRepository().get_dashboard(dashboard_id)
    # Add widget implementation
    return {"status": "success", "data": widget}

@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def delete_widget(
    dashboard_id: str,
    widget_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    await check_permissions(current_user, ["dashboard:update"])
    dashboard = await DashboardRepository().get_dashboard(dashboard_id)
    # Delete widget implementation
    return {"status": "success", "message": "Widget deleted"}

@router.get("/dashboards/{dashboard_id}/widgets")
async def list_widgets(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    dashboard = await DashboardRepository().get_dashboard(dashboard_id)
    return {"status": "success", "data": dashboard.widgets}