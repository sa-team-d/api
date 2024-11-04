from typing import List, Dict, Any

class BaseRepository:
    def __init__(self):
        # Mock database storage
        self.users: Dict[str, User] = {}
        self.machines: Dict[str, Machine] = {}
        self.reports: Dict[str, Report] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.webhooks: Dict[str, Dict] = {}
        self.integrations: Dict[str, Dict] = {}

    async def paginate(self, items: List[Any], page: int = 1, per_page: int = 20) -> Dict:
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": items[start:end],
            "total": len(items),
            "page": page,
            "per_page": per_page
        }
