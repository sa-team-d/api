from src.config.db_config import sites_collection
from .schema import Site
from bson import ObjectId
from fastapi import Request
from pymongo.collection import Collection
from src.utils import get_collection

async def getSiteByKpi(
    site_id,
    kpi_id,
    request: Request | None = None,
    sites_collection: Collection[Site] | None = None
) -> Site:
    sites_collection = get_collection(request, sites_collection, "sites")
    site = sites_collection.find_one({
        "site_id": site_id,
        "kpis_ids": {
             "$in": [ObjectId(kpi_id)]
        }
    })
    return Site(**site)