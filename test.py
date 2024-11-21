from src.plugin import controller

def working_ratio_definer():
  
    children = []
    kpi = 'working_time'
    res = controller.getKPIByName(kpi)
    children.append(res['_id'])

    kpi = 'offline_time'
    res = controller.getKPIByName(kpi)
    children.append(res['_id'])

    name = 'working_ratio'
    formula = 'working_time/offline_time'
    controller.createKPI(name, formula)
    
def energy_efficiency_definer():
    
    kpi = 'consumption'
    controller.getKPIByName(kpi)

    kpi = 'cycles'
    controller.getKPIByName(kpi)

    name = 'energy_efficiency'
    formula = 'consumption/cycles'
    controller.createKPI(name, formula)
    
def faulty_kpi_definer():
    
    name = 'faulty_kpi'
    formula = 'bug/cycles'
    controller.createKPI(name, formula)
    
def filterKPI_example(kpi):
    name = 'ast-yhccl1zjue2t'
    start_date = "2024-09-30 00:00:00"
    end_date = "2024-10-07 00:00:00"
    days = 7
    ops = 'sum'
    res = controller.filterKPI(name, kpi, start_date, end_date, days, ops)
    print(res)

if __name__ == '__main__':
    # faulty_kpi_definer()
    filterKPI_example('energy_efficiency')