"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
sys.path.append(os.path.abspath("."))
from src.mock_database import mock_db

MOCK_DATABASE = "smart_app_data.csv"

machines = mock_db.get("machines")
#for machine_id, machine in database.items():
#    database[machine_id] = Machine(id=machine.get("id"), type=machine.get("category"), data=MachineData(**machine.get("data")))

# list all machines
async def get_all():
    print("Getting all machines")
    return machines

# get machine by ID
async def get_by_id(machine_id: str):
    machine = machines.get(machine_id)
    if not machine:
        raise Exception("Machine not found")
    return machine

# get all machine with a specific type
async def get_by_type(machine_type: str):
    machines = [m for m in machines.values() if m.category == machine_type]
    return machines

