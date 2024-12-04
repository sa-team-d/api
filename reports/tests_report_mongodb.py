from datetime import datetime, timedelta
from src.plugins.report.schema import Report

# Mock data for testing
mock_reports = [
    Report(
        kpi_name="Energy Efficiency",
        name="Monthly Energy Report - Site A",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        user_uid="xM2kea8akaOKvYta26NMFBy8YnJ3",
        url="https://reports.example.com/energy/site_a_jan.pdf",
        sites_id=[0, 2]
    ),
    Report(
        kpi_name="Production Output",
        name="Q1 Production Summary",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 3, 31),
        user_uid="xM2kea8akaOKvYta26NMFBy8YnJ3",
        url="https://reports.example.com/production/q1_summary.pdf",
        sites_id=[1, 2]
    ),
    Report(
        kpi_name="Maintenance Efficiency",
        name="Weekly Maintenance Report",
        start_date=datetime(2024, 2, 1),
        end_date=datetime(2024, 2, 7),
        user_uid="k8SM6PwrJ4g663v5uZo8gfC7iND2",
        url="https://reports.example.com/maintenance/week5.pdf",
        sites_id=[0, 1]
    ),
    Report(
        kpi_name="Resource Utilization",
        name="Daily Resource Report",
        start_date=datetime(2024, 2, 15),
        end_date=datetime(2024, 2, 15),
        user_uid="k8SM6PwrJ4g663v5uZo8gfC7iND2",
        url="https://reports.example.com/resources/day45.pdf",
        sites_id=[2]
    ),
    Report(
        kpi_name="Performance Metrics",
        name="Annual Performance Review",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        user_uid="k8SM6PwrJ4g663v5uZo8gfC7iND2",
        url="https://reports.example.com/performance/annual_2023.pdf",
        sites_id=[0,1,2]
    )
]
