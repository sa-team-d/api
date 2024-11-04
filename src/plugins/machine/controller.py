"""Machine controller. This module defines the API routes for the Machine plugin."""
import json

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from src.plugins.machine import schema as machine_schema
from src.plugins.machine.repository import MachineRepository
# from src.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/machines", tags=["Machines"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
api_key_header = APIKeyHeader(name="X-API-Key")

@router.post("/", 
    response_model=machine_schema.Machine,
    status_code=201,
    summary="Create a new machine")
async def create_machine(
    machine: machine_schema.MachineCreate,
    token: str = Security(oauth2_scheme),
    repository: MachineRepository = Depends()
):
    return await repository.create_machine(machine=machine)

@router.get("/{machine_id}", 
    response_model=machine_schema.Machine,
    summary="Get machine by ID")
async def get_machine(
    machine_id: int = Path(..., title="The ID of the machine"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields"),
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    return await repository.get_machine(machine_id=machine_id)

@router.put("/{machine_id}",
    response_model=machine_schema.Machine,
    summary="Update machine")
async def update_machine(
    machine_id: int,
    machine: machine_schema.MachineUpdate,
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    return await repository.update_machine(machine_id=machine_id, machine=machine)

@router.delete("/{machine_id}",
    status_code=204,
    summary="Delete machine")
async def delete_machine(
    machine_id: int,
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    await repository.delete_machine(machine_id=machine_id)

@router.get("/",
    response_model=machine_schema.MachineList,
    summary="List machines")
async def list_machines(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query(None, description="Sort field and order (field:asc|desc)"),
    filter: Optional[str] = Query(None, description="Filter criteria"),
    fields: Optional[List[str]] = Query(None, description="Fields to include"),
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    filter_dict = json.loads(filter) if filter else None
    params = machine_schema.PaginationParams(
        page=page,
        per_page=per_page,
        sort=sort,
        filter=filter_dict,
        fields=fields
    )
    return await repository.list_machines(params=params)

@router.get("/search",
    response_model=List[machine_schema.Machine],
    summary="Search machines")
async def search_machines(
    query: str = Query(..., min_length=1),
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    return await repository.search_machines(query=query)

@router.get("/status/{status}",
    response_model=List[machine_schema.Machine],
    summary="Get machines by status")
async def get_machines_by_status(
    status: str,
    repository: MachineRepository = Depends(),
    token: str = Security(oauth2_scheme)
):
    return await repository.get_machines_by_status(status=status)