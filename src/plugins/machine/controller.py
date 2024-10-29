"""Machine controller. This module defines the API routes for the Machine plugin."""

from fastapi import APIRouter, HTTPException, Depends
from src.plugins.machine import schema as machine_schema
from src.plugins.machine import repository

router = APIRouter(prefix="/machines", tags=["Machines"])

@router.post("/", response_model=machine_schema.Machine)
def create_machine(machine: machine_schema.MachineCreate):
    return repository.create_machine(machine=machine)

@router.get("/{machine_id}", response_model=machine_schema.Machine)
def get_machine(machine_id: int):
    machine = repository.get_machine(machine_id=machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.get("/", response_model=list[machine_schema.Machine])
def list_machines():
    return repository.list_machines()

# get filtered machines by type
@router.get("/type/{machine_type}", response_model=list[machine_schema.Machine])
def list_machines_by_type(machine_type: str):
    return repository.list_machines_by_type(machine_type=machine_type)
