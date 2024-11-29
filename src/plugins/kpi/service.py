from fastapi import Request

from src.plugins.kpi.schema import KPIOverview
from . import repository
from .schema import ComputedValue
from src.plugins.site import repository as siteRepository
from sympy import sympify

def checkValidOps(op):
    if op == 'sum':
        return True
    if op == 'avg':
        return True
    if op == 'min':
        return True
    if op == 'max':
        return True
    raise Exception()
   
def applyAggregationOpToMachinesKpi(op, kpi_for_machines):
    if op == 'sum':
        return [
            {
                "value": sum(d["value"] for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'avg':
        return [
            {
                "value": sum(d["value"] for d in elements) / len(elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'min':
        return [
            {
                "value": min(d["value"] for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    if op == 'max':
        return [
            {
                "value": max(d["value"] for d in elements)
            }
            for elements in zip(*kpi_for_machines)
        ]
    raise Exception()

async def computeKPIBySite(
    site_id, 
    kpi_id,
    start_date,
    end_date,
    granularity_days,
    granularity_op
):
    if not checkValidOps(granularity_op):
        raise Exception('Not valid op')
    site = await siteRepository.getSiteByKpi(site_id, kpi_id)
    kpi_for_machines = []
    for machine_id in site.machines_ids:
        kpi_for_machines.append(
            computeKPIByMachine(
                machine_id,
                kpi_id,
                start_date,
                end_date,
                granularity_days,
                granularity_op 
            )
        )
    if len(kpi_for_machines) == 0: None
    results = applyAggregationOpToMachinesKpi(kpi_for_machines)
    return [ComputedValue(**result) for result in results]

async def computeKPIByMachine(
    machine_id, 
    kpi_id,
    start_date,
    end_date,
    granularity_days,
    granularity_op
):
    if not checkValidOps(granularity_op):
        raise Exception('Not valid op')
    return await repository.computeKPIByMachine(machine_id, kpi_id, start_date, end_date, granularity_days, granularity_op, request=request)

async def getKPIByName(request: Request, name: str):
    return await repository.getKPIByName(name, request=request)

async def getKPIById(request: Request, id: str):
    return await  repository.getKPIById(id, request=request)

async def listKPIs(request: Request) -> list[KPIOverview]:
    return await repository.listKPIs(request=request)

async def createKPI(
    request: Request,
    name: str,
    type: str,
    description: str,
    unite_of_measure: str,
    formula: str
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
    return await repository.createKPI(name, type, description, unite_of_measure, children, formula, request=request)

async def deleteKPIByID(request: Request, id: str):
    return await repository.deleteKPIByID(id, request=request)

async def deleteKPIByName(request: Request, name: str):
    return await repository.deleteKPIByName(name, request=request)

async def getKPIByName(request: Request, name: str):
    return await repository.getKPIByName(name, request=request)