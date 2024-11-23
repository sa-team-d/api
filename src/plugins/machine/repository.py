"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
from bson import ObjectId
sys.path.append(os.path.abspath("."))
from src.mock_database import mock_db
from .schema import MachineOverview, MachineDetail

from fastapi import Request

# list all machines
async def get_all(request: Request):
    machines_collection = request.app.mongodb.get_collection("machines")
    machines = machines_collection.find()
    return [MachineOverview(**machine) for machine in machines]

# get machine by ID
async def get_by_id(request: Request, machine_id: str):
    machines_collection = request.app.mongodb.get_collection("machines")
    machines = machines_collection.aggregate(
    [
        {
            "$match":
            {
                "_id": ObjectId(machine_id)
            }
        },
        {
            "$lookup": {
                "from": "kpis",
                "localField": "kpis_ids",
                "foreignField": "_id",
                "as": "kpis"
            }
        }
    ])
    machines = list(machines)
    if len(machines) == 0:
        raise Exception("Machine not found")
    machine = machines[0]
    return MachineDetail(**machine)

# get all machine with a specific type
async def get_by_type(request: Request, machine_type: str):
    machines_collection = request.app.mongodb.get_collection("machines")
    machines = machines_collection.find({ "type": machine_type })
    return [MachineOverview(**machine) for machine in machines]

async def get_by_name(request: Request, machine_name: str):
    machines_collection = request.app.mongodb.get_collection("machines")
    machines = machines_collection.find({ "name": machine_name })
    return [MachineOverview(**machine) for machine in machines]
