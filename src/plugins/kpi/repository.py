from src import mock_database as database
from src.models import KPIGroup, Kpi, Value

async def get_kpi_names():
    return database.mock_db.get("kpi_groups")

async def get_kpi_by_name(name: str):
    kpis = [Kpi(
        kpi_type="working_time",
        machine_id="ast-yhccl1zjue2t",
        data=[
            Value(
                machine_id="ast-yhccl1zjue2t",
                sum=0.0,
                avg=0.0,
                min=0.0,
                max=0.0,
                var=0.0
            ),
        ],
        config={}
    ),
    Kpi(
        kpi_type="consumption",
        machine_id="ast-yhccl1zjue2t",
        data=[
            Value(
                machine_id="ast-yhccl1zjue2t",
                sum=0.0661055170374786,
                avg=0.0023213179492811795,
                min=0.0,
                max=0.0661055170374786,
                var=0.0
            ),
        ],
        config={}
    ),]
    return kpis

async def add_kpi(name: str, description: str, group: str):
    return Kpi(
        kpi_type="working_time",
        machine_id="ast-yhccl1zjue2t",
        data=[
            Value(
                machine_id="ast-yhccl1zjue2t",
                sum=0.0,
                avg=0.0,
                min=0.0,
                max=0.0,
                var=0.0
            ),
        ],
        config={}
    )