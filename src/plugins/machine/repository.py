"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
sys.path.append(os.path.abspath("."))
from src.mock_database import mock_db
from src.models import Machine

# list all machines
async def get_all():
    return [
        Machine(
            id=m.id,
            category=m.category,
            name=m.name,
            kpi_list=m.kpi_list
        )
        for m in mock_db["machines"]
    ]

# get machine by ID
async def get_by_id(machine_id: str):
    machine = next((m for m in mock_db["machines"] if m.id == machine_id), None)
    if not machine:
        raise Exception("Machine not found")
    return machine

# get all machine with a specific type
async def get_by_type(machine_type: str):
    machines = [m for m in mock_db["machines"] if m.category == machine_type]
    return machines

async def get_by_name(machine_name: str):
    machines = [m for m in mock_db["machines"] if m.name == machine_name]
    return machines
