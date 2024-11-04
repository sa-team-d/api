"""
This module contains the repository layer for the machine plugin.
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import HTTPException
from src.plugins.machine.schema import MachineCreate, Machine, MachineUpdate
from src.repository import BaseRepository
from src.core.pagination import PaginationParams

class MachineRepository(BaseRepository):
    def __init__(self):
        self.machines: Dict[int, Machine] = {}

    async def create_machine(self, machine: MachineCreate) -> Machine:
        machine_id = len(self.machines) + 1
        machine_data = Machine(
            id=machine_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **machine.dict()
        )
        self.machines[machine_id] = machine_data
        return machine_data

    async def get_machine(self, machine_id: int) -> Machine:
        machine = self.machines.get(machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine

    async def update_machine(self, machine_id: int, machine: MachineUpdate) -> Machine:
        existing = await self.get_machine(machine_id)
        update_data = machine.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(existing, field, value)
        
        existing.updated_at = datetime.utcnow()
        self.machines[machine_id] = existing
        return existing

    async def delete_machine(self, machine_id: int) -> None:
        if machine_id not in self.machines:
            raise HTTPException(status_code=404, detail="Machine not found")
        del self.machines[machine_id]

    async def list_machines(self, params: PaginationParams) -> Dict[str, Any]:
        machines = list(self.machines.values())

        # Apply filters
        if params.filter:
            for field, value in params.filter.items():
                machines = [m for m in machines if getattr(m, field, None) == value]

        # Apply sorting
        if params.sort:
            field, order = params.sort.split(':')
            reverse = order.lower() == 'desc'
            machines.sort(key=lambda x: getattr(x, field), reverse=reverse)

        # Apply field selection
        if params.fields:
            machines = [{field: getattr(m, field) for field in params.fields} 
                       for m in machines]

        total = len(machines)
        start = (params.page - 1) * params.per_page
        end = start + params.per_page

        return {
            "items": machines[start:end],
            "total": total,
            "page": params.page,
            "per_page": params.per_page,
            "pages": (total + params.per_page - 1) // params.per_page
        }

    async def search_machines(self, query: str) -> List[Machine]:
        """Search machines by name or description"""
        query = query.lower()
        return [
            machine for machine in self.machines.values()
            if query in machine.name.lower() or 
               (machine.description and query in machine.description.lower())
        ]

    async def get_machines_by_status(self, status: str) -> List[Machine]:
        """Get machines by status"""
        return [m for m in self.machines.values() if m.status == status]