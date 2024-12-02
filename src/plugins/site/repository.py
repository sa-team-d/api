from .schema import Site
from bson import ObjectId
from fastapi import Request
from pymongo.collection import Collection
from src.utils import get_collection

async def getSiteByKpi(
    site_id: int,
    kpi_id: ObjectId,
    request: Request | None = None,
    sites_collection: Collection[Site] | None = None
) -> Site:
    sites_collection = get_collection(request, sites_collection, "sites")
    site = await sites_collection.find_one({
        "site_id": site_id,
        "kpis_ids": {
             "$in": [ObjectId(kpi_id)]
        }
    })
    return Site(**site)

async def getSiteById(
    site_id: int,
    request: Request | None = None,
    sites_collection: Collection[Site] | None = None
):
    sites_collection = get_collection(request, sites_collection, "sites")
    site = await sites_collection.find_one({
        "site_id": site_id
    })
    return Site(**site)
    
async def associateKPItoSite(
    site_id,
    kpi_id,
    request: Request | None = None,
    sites_collection: Collection[Site] | None = None
):
    sites_collection = get_collection(request, sites_collection, "sites")
    site = await getSiteById(site_id, request)
    if ObjectId(kpi_id) not in site.kpis_ids:
        result = await sites_collection.update_one(
            { "site_id": site_id },
            { "$push": { "kpis_ids": ObjectId(kpi_id) } }
        )
        if result.matched_count > 0 and result.modified_count > 0:
            site = await getSiteById(site_id, request)
    return site

async def removeKPIfromSites(
    kpi_id,
    request: Request | None = None,
    sites_collection: Collection[Site] | None = None
):
    sites_collection = get_collection(request, sites_collection, "sites")
    result = await sites_collection.update_one({},{ "$pull": {"kpis_ids": ObjectId(kpi_id)}})
    if result.matched_count > 0 and result.modified_count > 0:
        print("Element removed successfully.")
    else:
        print("No matching document found.")
    