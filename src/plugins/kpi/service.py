import re
from fastapi import Request

from src.plugins.kpi.schema import KPIOverview
from . import repository
from .schema import ComputedValue, RowReport, KPIReport
from src.plugins.site import repository as siteRepository
from src.plugins.user import repository as userRepository
from src.plugins.machine import repository as machineRepository
from sympy import sympify
import math
import numpy as np

def checkValidOps(op):
    if op == 'sum':
        return True
    if op == 'avg':
        return True
    if op == 'min':
        return True
    if op == 'max':
        return True
    if op == 'std':
        return True
    return False

def applyAggregationOpToMachinesKpi(op, kpi_for_machines):
    if op == 'sum':
        return [
            {
                "value": sum(d.value for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'avg':
        return [
            {
                "value": sum(d.value for d in elements) / len(elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'min':
        return [
            {
                "value": min(d.value for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'max':
        return [
            {
                "value": max(d.value for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'std':
        return [
            {
                "value": float(np.std([d.value for d in elements]))
            }
            for elements in zip(*kpi_for_machines)
        ]
    raise Exception('Not valid op')

async def computeKPIForReport(
    request: Request,
    site_id, 
    start_date,
    end_date,
    granularity_days,
    granularity_op,
    kpi_names: list[str] = [],
):
    site = await siteRepository.getSiteByIdPopulatedKPI(site_id, request=request)
    result = RowReport(
        start_date=start_date,
        end_date=end_date,
        op=granularity_op,
        kpis=[]
    )
    for kpi in site.kpis:
        if kpi.name not in kpi_names:
            continue
        kpi_result = await computeKPIBySite(request, site_id, kpi.id, None, start_date, end_date, granularity_days, granularity_op)
        if len(kpi_result) != 1: raise Exception("No kpi result found")
        result.kpis.append(KPIReport(
            name = kpi.name,
            value = kpi_result[0].value,
        ))
    return result

async def computeKPIBySite(
    request: Request,
    site_id,
    kpi_id,
    category,
    start_date,
    end_date,
    granularity_days,
    granularity_op,
):
    if not checkValidOps(granularity_op):
        raise Exception('Not valid op')
    machines_ids = []
    if category:
        machines = await machineRepository.list_by_category(category, site_id, request)
        machines_ids = [machine.id for machine in machines]
    else:
        site = await siteRepository.getSiteByKpi(site_id, kpi_id, request)
        machines_ids = site.machines_ids
    kpi_for_machines = []
    for machine_id in machines_ids:
        kpi_for_machines.append(
            await computeKPIByMachine(
                request,
                machine_id,
                kpi_id,
                start_date,
                end_date,
                granularity_days,
                granularity_op,
            )
        )
    if len(kpi_for_machines) == 0: return None
    results = applyAggregationOpToMachinesKpi(granularity_op, kpi_for_machines)
    return [ComputedValue(**result) for result in results]

async def computeKPIByMachine(
    request: Request,
    machine_id,
    kpi_id,
    start_date,
    end_date,
    granularity_days,
    granularity_op
):
    if not checkValidOps(granularity_op):
        raise Exception('Not valid op')
    res = await repository.computeKPIByMachine(machine_id, kpi_id, start_date, end_date, granularity_days, granularity_op, request=request)
    if len(res) == 0:
        raise Exception('There are not data for this kpi: ', kpi_id)
    return res

async def getKPIByName(request: Request, name: str):
    return await repository.getKPIByName(name, request=request)

async def getKPIById(request: Request, id: str):
    return await  repository.getKPIById(id, request=request)

async def listKPIs(site: int, request: Request) -> list[KPIOverview]:
    return await repository.listKPIs(site, request=request)

async def createKPI(
    request: Request,
    name: str,
    type: str,
    description: str,
    unite_of_measure: str,
    formula: str,
    uid: str
):
    expr = sympify(formula)
    kpis_in_formula = {str(symbol) for symbol in expr.free_symbols}
    existing_kpis = await repository.listKPIsByName(list(kpis_in_formula), request=request)

    existing_kpi_names = set()
    children = []
    for doc in existing_kpis:
        existing_kpi_names.add(doc.name)
        children.append(doc.id)

    missing_kpis = kpis_in_formula - existing_kpi_names
    if missing_kpis:
        print(f"The following KPIs are missing from the database: {missing_kpis}")
        raise ValueError("Missing KPIs")
    kpi = await repository.createKPI(name, type, description, unite_of_measure, children, formula, request=request)
    user = await userRepository.get_user_by_uid(uid, request=request)
    
    await siteRepository.associateKPItoSite(user.site, kpi.id, request=request)
    return kpi

async def deleteKPIByID(request: Request, id: str):
    await siteRepository.removeKPIfromSites(id, request=request)
    await machineRepository.removeKPIfromMachines(id, request=request)
    
    return await repository.deleteKPIByID(id, request=request)

async def getKPIByName(request: Request, name: str):
    return await repository.getKPIByName(name, request=request)