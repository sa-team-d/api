from typing import List
from sympy import sympify, zoo
from .schema import KPI, Configuration, ComputedValue, KPIOverview, KPIDetail
from bson import ObjectId

from fastapi import Request

def computeKPI(
    request: Request,
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op
) -> List[ComputedValue]:
    '''
    machine_id: id of the machine
    kpi: kpi name
    start_date
    end_date
    granularity_days: number of days to subaggregate data
    granularity_operation: sum, avg, min, max
    '''
    kpi_obj = getKPIById(request, kpi_id)
    if kpi_obj.config.formula != None:
        res = computeCompositeKPI(
            request,
            machine_id, 
            kpi_id, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op
        )
    else:
        res = computeAtomicKPI(
            request,
            machine_id, 
            kpi_id, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op
        )
    return res

def computeCompositeKPI(
    request: Request,
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op
) -> List[ComputedValue]:
    kpi_obj = getKPIById(request, kpi_id)
    children = kpi_obj.config.children
    formula = kpi_obj.config.formula
    values = []
    for child in children:
        kpi_dep = getKPIById(request, child)
        value = computeKPI(
            request,
            machine_id,
            kpi_dep.id, 
            start_date,
            end_date,
            granularity_days, 
            granularity_op
        )
        values.append({ kpi_dep.name: value })
    value = values[0]
    key = next(iter(value.keys()))
    results = []
    for index in range(len(value[key])):
        symbol_dict = {}
        for v in values:
            k = next(iter(v.keys()))
            symbol_dict[k] = v[k][index].value
        parsed_expression = sympify(formula)
        result = parsed_expression.subs(symbol_dict)
        if result == zoo:
            raise Exception('invalid math operation')
        results.append(ComputedValue(value=result))
    return results

def computeAtomicKPI(
    request: Request,
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op
) -> List[ComputedValue]:
    kpis_collection = request.app.mongodb.get_collection("kpis")
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(kpi_id)
            }
        },
        {
            "$unwind": {
                "path": "$data"
            }
        },
        {
            "$match": {
                "data.machine_id": machine_id,
                "data.datetime": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "documents": {
                    "$push": "$$ROOT"
                }
            }
        },
        {
            "$unwind": {
                "path": "$documents",
                "includeArrayIndex": "index"
            }
        },
        {
            "$addFields": {
                "groupIndex": {
                    "$floor": {
                        "$divide": ["$index", granularity_days]
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$groupIndex",
                "value": {
                    f"${granularity_op}": f"$documents.data.{granularity_op}"
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "value": 1
            }
        }
    ]
    return [ComputedValue(**kpi) for kpi in list(kpis_collection.aggregate(pipeline))]
    
def getKPIByName(request: Request, name: str) -> KPI:
    kpis_collection = request.app.mongodb.get_collection("kpis")
    kpi = kpis_collection.find_one({"name": name})
    return KPI(**kpi)

def getKPIById(request: Request, id: str) -> KPIDetail:
    kpis_collection = request.app.mongodb.get_collection("kpis")
    kpi = kpis_collection.find_one({"_id": ObjectId(id)})
    return KPIDetail(**kpi)

def listKPIs(request: Request) -> List[KPIOverview]:
    kpis_collection = request.app.mongodb.get_collection("kpis")
    kpis = kpis_collection.find({}, {
        "_id": 1,
        "name": 1,
        "type": 1,
        "description": 1,
        "unite_of_measure": 1,
    })
    kpis = [KPIOverview(**kpi) for kpi in kpis]
    return kpis

def listKPIsByName(request: Request, names: List[str]) -> List[KPIOverview]:
    kpis_collection = request.app.mongodb.get_collection("kpis")
    kpis = kpis_collection.find(
        { "name": { "$in": names } }, 
        {
        "_id": 1,
        "name": 1,
        "type": 1,
        "description": 1,
        "unite_of_measure": 1,
        }
    )
    kpis = [KPIOverview(**kpi) for kpi in kpis]
    return kpis

def createKPI(
    request: Request,
    name: str,
    type: str,
    description: str,
    unite_of_measure: str,
    children: List[str], 
    formula: str
) -> KPI:
    kpi = KPI(
        name=name,
        type=type,
        description=description,
        unite_of_measure=unite_of_measure,
        config=Configuration(
            children=children, 
            formula=formula
        )
    )
    kpis_collection = request.app.mongodb.get_collection("kpis")
    kpi = kpis_collection.insert_one(kpi.dict(by_alias=True))
    return KPI(**kpi)