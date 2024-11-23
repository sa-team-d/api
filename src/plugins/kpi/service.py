from fastapi import Request
from . import repository
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
    return False
    
async def computeKPI(
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
    return await repository.computeKPI(request, machine_id, kpi_id, start_date, end_date, granularity_days, granularity_op)

def getKPIByName(request: Request, name: str):
    kpi = repository.getKPIByName(request, name)
    return kpi

def getKPIById(request: Request, id: str):
    return repository.getKPIById(request, id)

def listKPIs(request: Request):
    return repository.listKPIs(request)

def createKPI(
    request: Request,
    name: str,
    type: str,
    description: str,
    unite_of_measure: str,
    formula: str
):
    expr = sympify(formula)
    kpis_in_formula = {str(symbol) for symbol in expr.free_symbols}   
    existing_kpis = repository.listKPIsByName(request, list(kpis_in_formula))

    existing_kpi_names = set()
    children = []
    for doc in existing_kpis:
        existing_kpi_names.add(doc.name)
        children.append(doc.id)

    missing_kpis = kpis_in_formula - existing_kpi_names
    if missing_kpis:
        print(f"The following KPIs are missing from the database: {missing_kpis}")
        raise ValueError("Missing KPIs")
    repository.createKPI(request, name, type, description, unite_of_measure, children, formula)