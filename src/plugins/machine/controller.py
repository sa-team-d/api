"""Machine controller. This module defines the API routes for the Machine plugin."""
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Security
from fastapi.requests import Request

from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.machine.repository import get_all, get_by_id, get_by_type, get_by_name
from .schema import MachineOverview, MachineDetail, MachineResponse

import os
API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/machine", tags=["Machine"])

# list all machines
@router.get("/",status_code=200, response_model=MachineResponse, summary="Get all machines in the dataset")
async def get_all_machines(request:Request, user=Depends(verify_firebase_token)):
    try:
        machines = await get_all(request)

        return MachineResponse(success=True, data=machines, message="Machines listed successfully")
    except Exception as e:
        print(f"Error getting all machines: {e}")
        return MachineResponse(success=False, data=None, message=str(e))
        #raise HTTPException(status_code=500, detail=str(e))

# filter
@router.get("/filter", response_model=MachineResponse, status_code=201, summary="Filter machines by type or name")
async def filter_machines(request: Request, user=Depends(verify_firebase_token), machine_name: str = None, machine_type: str = None):
    try:
        if machine_name:
            machines = await get_by_name(request, machine_name)
        elif machine_type:
            machines = await get_by_type(request, machine_type)
        else:
            return MachineResponse(success=False, data=None, message="No filter provided")
        return MachineResponse(success=True, data=machines, message="Machines filtered successfully")
    except Exception as e:
        return MachineResponse(success=False, data=None, message=str(e))

# get machine by ID
@router.get("/{machine_id}", response_model=MachineResponse, status_code=200, summary="Get machine by ID")
async def get_machine_by_id(request: Request, machine_id: str):
    try:
        machine = await get_by_id(request,machine_id)

        return MachineResponse(success=True, data=machine, message="Machine retrieved successfully")
    except Exception as e:
        return MachineResponse(success=False, data=None, message=str(e))
        # raise HTTPException(status_code=500, detail=str(e))