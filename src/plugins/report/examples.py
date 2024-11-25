from datetime import datetime


reports_examples_to_insert = [
    {
        "kpi_name": "working_ratio",
        "content": "Working ratio shows improvement with 85% uptime this month across production lines",
        "date": datetime(2024, 3, 1, 9, 30),
        "user_uid": "k8SM6PwrJ4g663v5uZo8gfC7iND2",
        "asset_id": ["ast-06kbod797nnp", "ast-206phi0b9v6p"]  # Testing Machine 3, Laser Welding Machine 2
    },
    {
        "kpi_name": "consumption",
        "content": "Energy consumption decreased by 12% after optimization measures",
        "date": datetime(2024, 3, 5, 14, 15),
        "user_uid": "xM2kea8akaOKvYta26NMFBy8YnJ3",
        "asset_id": ["ast-yhccl1zjue2t"]  # Large Capacity Cutting Machine 1
    },
    {
        "kpi_name": "energy_efficiency", 
        "content": "Energy efficiency improved by 8% following maintenance schedule updates",
        "date": datetime(2024, 3, 8, 11, 45),
        "user_uid": "k8SM6PwrJ4g663v5uZo8gfC7iND2",
        "asset_id": ["ast-o8xtn5xa8y87", "ast-ha448od5d6bd"]  # Riveting Machine, Medium Capacity Cutting Machine 1
    },
    {
        "kpi_name": "cost_idle",
        "content": "Idle cost reduced by 15% through better shift management",
        "date": datetime(2024, 3, 10, 16, 20),
        "user_uid": "xM2kea8akaOKvYta26NMFBy8YnJ3",
        "asset_id": ["ast-xpimckaf3dlf"]  # Laser Cutter
    },
    {
        "kpi_name": "working_ratio",
        "content": "Working ratio dropped to 72% due to scheduled maintenance",
        "date": datetime(2024, 3, 12, 10, 0),
        "user_uid": "k8SM6PwrJ4g663v5uZo8gfC7iND2",
        "asset_id": ["ast-6votor3o4i9l"]  # Large Capacity Cutting Machine 2
    },
    {
        "kpi_name": "energy_efficiency",
        "content": "New equipment installation resulted in 20% better energy efficiency",
        "date": datetime(2024, 3, 15, 13, 30),
        "user_uid": "xM2kea8akaOKvYta26NMFBy8YnJ3",
        "asset_id": ["ast-5aggxyk5hb36", "ast-nrd4vl07sffd"]  # Medium Capacity Cutting Machine 2, Testing Machine 1
    },
    {
        "kpi_name": "consumption",
        "content": "Peak hour consumption optimization achieved 10% reduction",
        "date": datetime(2024, 3, 18, 9, 0),
        "user_uid": "k8SM6PwrJ4g663v5uZo8gfC7iND2",
        "asset_id": ["ast-pu7dfrxjf2ms", "ast-6nv7viesiao7"]  # Testing Machine 2, Low Capacity Cutting Machine 1
    },
    {
        "kpi_name": "cost_idle",
        "content": "Weekend idle time costs decreased by 25% with new scheduling",
        "date": datetime(2024, 3, 20, 15, 45),
        "user_uid": "xM2kea8akaOKvYta26NMFBy8YnJ3",
        "asset_id": ["ast-anxkweo01vv2", "ast-pwpbba0ewprp"]  # Medium Capacity Cutting Machine 3, Assembly Machine 1
    },
    {
        "kpi_name": "working_ratio",
        "content": "Achieved 90% working ratio after process optimization",
        "date": datetime(2024, 3, 22, 11, 15),
        "user_uid": "k8SM6PwrJ4g663v5uZo8gfC7iND3",
        "asset_id": ["ast-hnsa8phk2nay", "ast-upqd50xg79ir"]  # Laser Welding Machine 1, Assembly Machine 2
    },
    {
        "kpi_name": "energy_efficiency",
        "content": "Monthly energy efficiency targets exceeded by 5%",
        "date": datetime(2024, 3, 25, 14, 0),
        "user_uid": "xM2kea8akaOKvYta26NMFBy8YnJ3",
        "asset_id": ["ast-sfio4727eub0", "ast-206phi0b9v6p", "ast-06kbod797nnp"]  # Assembly Machine 3, Laser Welding Machine 2, Testing Machine 3
    }
]