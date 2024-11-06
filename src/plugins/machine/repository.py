"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
sys.path.append(os.path.abspath("."))
import json
from src.models import Machine, MachineData, Database

MOCK_DATABASE = "mock_database.json"

# TODO: Create a postgres database connection and replace the mock database with the real database
with open(MOCK_DATABASE) as f:
    data = json.load(f)

database = data.get("machines")
for machine_id, machine in database.items():
    database[machine_id] = Machine(id=machine.get("id"), type=machine.get("type"), data=MachineData(**machine.get("data")))

# list all machines
async def get_all():
    return list(database.values())

# get machine by ID
async def get_by_id(machine_id: str):
    machine = database.get(machine_id)
    if not machine:
        raise Exception("Machine not found")
    return machine

# get all machine with a specific type
async def get_by_type(machine_type: str):
    machines = [m for m in database.values() if m.type == machine_type]
    return machines

