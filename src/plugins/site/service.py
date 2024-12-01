from fastapi import Request
from . import repository

async def associateKPItoSite(request: Request, site_id, kpi_id):
    return await repository.associateKPItoSite(site_id, kpi_id, request)

async def getSiteById(request: Request, site_id):
    return await repository.getSiteById(site_id, request)