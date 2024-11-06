"""Machine controller. This module defines the API routes for the Machine plugin."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Security
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.machine.repository import get_all, get_by_id, get_by_type
from src.plugins.machine.schema import Machine, MachineData

router = APIRouter(prefix="/api/v1/machine", tags=["Machine"])

# list all machines
@router.get("/all",status_code=201, response_model=List[Machine], summary="Get all machines in the dataset")
async def get_all_machines(user=Depends(verify_firebase_token)):
    try:
        machines = await get_all()
        return machines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get machine by ID
@router.get("/{machine_id}", response_model=Machine, status_code=201, summary="Get machine by ID")
async def get_machine_by_id(
    machine_id: str = Path(..., title="The ID of the machine"),
    user=Depends(verify_firebase_token)
):
    try:
        machine = await get_by_id(machine_id)
        return machine
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get all machine with a specific type
@router.get("/type/{machine_type}", response_model=List[Machine], summary="Get all machines with a specific type")
async def get_machines_by_type(
    machine_type: str,
    user=Depends(verify_firebase_token)
):
    try:
        machines = await get_by_type(machine_type=machine_type)
        return machines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))