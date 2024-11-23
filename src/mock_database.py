from src.models import Kpi, Value, Alarm, Report, KPIGroup
from datetime import datetime

mock_db = {
    # "machines": [
    #     Machine(
    #         id="ast-yhccl1zjue2t",
    #         category="cutting_machines",
    #         name="Large Capacity Cutting Machine 1",
    #         kpi_list=[]
    #     ),
    #     Machine(
    #         id="ast-yhccl1zjue2t",
    #         category="cutting_machines",
    #         name="Large Capacity Cutting Machine 2",
    #         kpi_list=[]
    #     ),
    # ],
    "alarms": [
        Alarm(
            text="High Power Consumption Alert",
            date=datetime.strptime("2024-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            threshold=0.05,
            formula="consumption > threshold",
            machine_id="ast-yhccl1zjue2t"
        )
    ],
    "reports": [
        Report(
            id="rep-001",
            kpi_type="daily_summary",
            content="Daily machine performance report",
            date=datetime.strptime("2024-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            uid="uid-001"
        )
    ],
    "configurations": [
    ],
    "kpi_groups": [
        KPIGroup(
            name="Energy Metrics",
            kpi_list=[]
        )
    ]
}