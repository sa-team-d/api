"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
from bson import ObjectId
sys.path.append(os.path.abspath("."))
from src.mock_database import mock_db
from .schema import MachineOverview, MachineDetail
from src.utils import get_collection

from fastapi import Request
from pymongo.collection import Collection

# list all machines
async def get_all(request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "g8", "machines")

    machines = machines_collection.find()
    return [MachineOverview(**machine) async for machine in machines]

# get machine by ID
async def get_by_id(machine_id: str, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "g8", "machines")

    cursor = machines_collection.aggregate(
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
    machines = await cursor.to_list(length=1)

    if len(machines) == 0:
        raise Exception("Machine not found")
    machine = machines[0]
    return MachineDetail(**machine)

# get all machine with a specific type
async def get_by_type(machine_type: str, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "g8", "machines")

    machines = machines_collection.find({ "type": machine_type })
    return [MachineOverview(**machine) async for machine in machines]

async def get_by_name(machine_name: str, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "g8", "machines")

    machines = machines_collection.find({ "name": machine_name })
    return [MachineOverview(**machine) async for machine in machines]
