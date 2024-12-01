import os
import logging

from . import service
from typing import List, Optional
from datetime import datetime
from .schema import (
        SiteResponse
    )
from fastapi import APIRouter, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token


logger = logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/site", tags=["Site"])

@router.get("/{id}", status_code=200, response_model=SiteResponse, summary="Get site by id")
async def getSiteById(
    request: Request,
    id: int,
    user=Depends(verify_firebase_token)
):
    try:
        site = await service.getSiteById(request, id)
        if site:
            return SiteResponse(success=True, data=site)
        return SiteResponse(success=False, message=f"Site with id {id} not found")
    except Exception as e:
        logger.error(f"Error getting site: {e}")
        return  SiteResponse(success=False, data=None, message=f"Error getting site: {str(e)}")
    
@router.get("/{id}/associate", status_code=200, response_model=SiteResponse, summary="Associate kpi to site")
async def getSiteById(
    request: Request,
    id: int,
    kpi_id: str,
    user=Depends(verify_firebase_token)
):
    try:
        site = await service.associateKPItoSite(request, id, kpi_id)
        return SiteResponse(success=True, data=site)
    except Exception as e:
        logger.error(f"Error associating kpi to site: {e}")
        return  SiteResponse(success=False, data=None, message=f"Error associating kpi to the site: {str(e)}")
