from typing import List, Dict, Optional
from fastapi import HTTPException
from datetime import datetime
from src.models import Dashboard, DashboardUpdate
from src.core.pagination import PaginationParams
from src.core.filtering import FilterParams
from src.repository import BaseRepository

class DashboardRepository(BaseRepository):
    async def create_dashboard(self, dashboard: Dashboard) -> Dashboard:
        if dashboard.site_id in self.dashboards:
            raise HTTPException(
                status_code=400, 
                detail={"code": "DASHBOARD_EXISTS", "message": "Dashboard already exists"}
            )
        dashboard.created_at = datetime.utcnow()
        self.dashboards[dashboard.id] = dashboard
        return dashboard

    async def get_dashboard(self, dashboard_id: str) -> Dashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=404,
                detail={"code": "DASHBOARD_NOT_FOUND", "message": "Dashboard not found"}
            )
        return dashboard

    async def update_dashboard(self, dashboard_id: str, update_data: DashboardUpdate) -> Dashboard:
        dashboard = await self.get_dashboard(dashboard_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(dashboard, field, value)
        
        dashboard.updated_at = datetime.utcnow()
        self.dashboards[dashboard_id] = dashboard
        return dashboard

    async def delete_dashboard(self, dashboard_id: str) -> None:
        if dashboard_id not in self.dashboards:
            raise HTTPException(
                status_code=404,
                detail={"code": "DASHBOARD_NOT_FOUND", "message": "Dashboard not found"}
            )
        del self.dashboards[dashboard_id]

    async def list_dashboards(
        self,
        pagination: PaginationParams,
        filters: Optional[FilterParams] = None,
        sort: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict:
        dashboards = list(self.dashboards.values())

        # Apply filters
        if filters:
            dashboards = [d for d in dashboards if self._apply_filters(d, filters)]

        # Apply sorting
        if sort:
            field, order = sort.split(':')
            reverse = order.lower() == 'desc'
            dashboards.sort(key=lambda x: getattr(x, field), reverse=reverse)

        # Apply pagination
        total = len(dashboards)
        start_idx = (pagination.page - 1) * pagination.per_page
        end_idx = start_idx + pagination.per_page
        page_items = dashboards[start_idx:end_idx]

        # Select fields if specified
        if fields:
            page_items = [
                {field: getattr(item, field) for field in fields}
                for item in page_items
            ]

        return {
            "status": "success",
            "data": {
                "items": page_items,
                "metadata": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": total,
                    "pages": (total + pagination.per_page - 1) // pagination.per_page
                }
            }
        }

    def _apply_filters(self, dashboard: Dashboard, filters: FilterParams) -> bool:
        for field, value in filters.items():
            if not hasattr(dashboard, field):
                continue
            if getattr(dashboard, field) != value:
                return False
        return True