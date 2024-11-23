"""
This module contains the repository layer for the machine plugin.
"""
import sys, os
from bson import ObjectId
sys.path.append(os.path.abspath("."))
from src.mock_database import mock_db
from .schema import MachineOverview, MachineDetail
from src.config.db_config import machines_collection
# list all machines
async def get_all():
    machines = machines_collection.find()
    return [MachineOverview(**machine) for machine in machines]

# get machine by ID
async def get_by_id(machine_id: str):
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
async def get_by_type(machine_type: str):
    machines = machines_collection.find({ "type": machine_type })
    return [MachineOverview(**machine) for machine in machines]

async def get_by_name(machine_name: str):
    machines = machines_collection.find({ "name": machine_name })
    return [MachineOverview(**machine) for machine in machines]
