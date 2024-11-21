from typing import List
from sympy import sympify, zoo
from src.config.db_config import kpis_collection
from .schema import KPI, Configuration, ComputedValue, KPIOverview

def computeKPI(
    machine_id, 
    kpi_name, 
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
    kpi_obj = getKPIByName(kpi_name)
    print(kpi_name)
    if kpi_obj.data == None:
        res = computeCompositeKPI(
            machine_id, 
            kpi_name, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op
        )
    else:
        res = computeAtomicKPI(
            machine_id, 
            kpi_name, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op
        )
    return res

def computeCompositeKPI(
    machine_id, 
    kpi_name, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op
) -> List[ComputedValue]:
    kpi_obj = getKPIByName(kpi_name)
    children = kpi_obj.config.children
    formula = kpi_obj.config.formula
    values = []
    for child in children:
        kpi_dep = getKPIById(child)
        value = computeKPI(
            machine_id, 
            kpi_dep.name, 
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
    machine_id, 
    kpi, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op
) -> List[ComputedValue]:
    pipeline = [
        {
            "$match": {
                "name": kpi
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
    
def getKPIByName(name: str) -> KPI:
    kpi = kpis_collection.find_one({"name": name})
    return KPI(**kpi)

def getKPIById(id: str) -> KPI:
    kpi = kpis_collection.find_one({"_id": id})
    return KPI(**kpi)

def listKPIs() -> List[KPI]:
    kpis = kpis_collection.find({}, {
        "_id": 1,
        "name": 1,
        "type": 1,
        "description": 1,
        "unite_of_measure": 1,
    })
    kpis = [KPIOverview(**kpi) for kpi in kpis]
    return kpis

def createKPI(
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
    kpi = kpis_collection.insert_one(kpi.dict(by_alias=True))
    return KPI(**kpi)