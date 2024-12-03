"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
from typing import Optional
from bson import ObjectId
sys.path.append(os.path.abspath("."))
from .schema import MachineOverview, MachineDetail
from src.utils import get_collection
from src.custom_exceptions import MachineNotFoundException

from fastapi import Request
from pymongo.collection import Collection

# list all machines
async def get_all(request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "machines")

    cursor = machines_collection.find()
    machines = [MachineOverview(**machine) async for machine in cursor]

    if len(machines) == 0:
        raise MachineNotFoundException("No machines found")
    return machines

# list all machines
async def list_by_category(category: str, site_id: Optional[int], request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    sites_collection = get_collection(request, None, "sites")
    cursor = sites_collection.aggregate([
        {
            "$match":
            {
                "site_id": site_id
            }
        },
        {
            "$lookup":
            {
                "from": "machines",
                "localField": "machines_ids",
                "foreignField": "_id",
                "as": "machines"
            }
        },
        {
            "$unwind":
            {
                "path": "$machines"
            }
        },
        {
            "$match":
            {
                "machines.category": category
            }
        }
        ])
    machines = [MachineOverview(**site['machines']) for site in await cursor.to_list(None)]

    if len(machines) == 0:
        raise MachineNotFoundException("No machines found")
    return machines

# get machine by ID
async def get_by_id(machine_id: str, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "machines")

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
        raise MachineNotFoundException("Machine not found")
    machine = machines[0]
    return MachineDetail(**machine)

# get all machine with a specific type
async def get_by_type(machine_type: str, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "machines")

    cursor = machines_collection.find({ "type": machine_type })
    machines = [MachineOverview(**machine) async for machine in cursor]

    if len(machines) == 0:
        raise MachineNotFoundException("No machines found")
    return machines

async def get_by_name(machine_name: str, machine_type: Optional[str] = None, request: Request | None = None, machines_collection: Collection[MachineDetail] = None):
    machines_collection = get_collection(request, machines_collection, "machines")

    if machine_type:
        cursor = machines_collection.find({ "name": machine_name, "type": machine_type })
    else:
        cursor = machines_collection.find({ "name": machine_name })
    machines = [MachineOverview(**machine) async for machine in cursor]

    if len(machines) == 0:
        raise MachineNotFoundException("No machines found")
    return machines
