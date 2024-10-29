"""
This module contains the repository layer for the machine plugin.
"""

from src.plugins.machine.schema import MachineCreate, Machine
from typing import List, Optional

# Mock "database"
mock_db = {}
next_id = 1

def create_machine(machine: MachineCreate) -> Machine:
    global next_id
    new_machine = Machine(id=next_id, name=machine.name, type=machine.type)
    mock_db[next_id] = new_machine
    next_id += 1
    return new_machine

def get_machine(machine_id: int) -> Optional[Machine]:
    return mock_db.get(machine_id)

def list_machines() -> List[Machine]:
    return list(mock_db.values())

# lista tutte le macchine nella categoria di un certo tipo
def list_machines_by_type(machine_type: str) -> List[Machine]:
    # con il database sql -> query
    return [machine for machine in mock_db.values() if machine.type == machine_type]