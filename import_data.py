import pandas as pd
from model.model import KPI, Configuration, Value
from src.config.db_config import kpis_collection

csv_path = 'dataset/smart_app_data.csv'    
    
def import_data(df):
    kpi_list=[]
    for _, row in df.iterrows():
        machine_id = row['asset_id']
        machine_name = row['name']
        data_datetime = row['time']
        kpi_name = row['kpi']

        value = Value(
            sum=row.get('sum'),
            avg=row.get('avg'),
            min=row.get('min'),
            max=row.get('max'),
            datetime=data_datetime,
            machine_id=machine_id
        )
        kpi = next((k for k in kpi_list if k.name == kpi_name), None)
        if not kpi:
            kpi = KPI(
                name=kpi_name,
                data=[value],
                type=None,
                config=Configuration(children=[], formula=None)
            )
            kpi_list.append(kpi)
        else:
            kpi.data.append(value)

    for kpi in kpi_list:
        kpis_collection.insert_one(kpi.dict(by_alias=True))

df = pd.read_csv(csv_path)
import_data(df)
print("Data imported successfully.")