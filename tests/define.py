import requests as r
import os

baseUrl = os.environ['BASE_URL']
api_version = os.environ['API_VERSION']
firebaseRestApi = os.environ['FIREBASE_REST_API']
firebaseWebApiKey = os.environ['FIREBASE_WEB_API_KEY']

class FFMAuth:
    uid: str
    email: str
    pwd: str
    token: str

def login(email: str, pwd: str):
    body = {
        "email": email,
        "password": pwd,
        "returnSecureToken": True
    }

    response = r.post(f'{firebaseRestApi}:signInWithPassword?key={firebaseWebApiKey}', json=body)
    return response.json()
    

def get_machine_by_id(token: str, id: str):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = r.get(f'{baseUrl}{api_version}machine/{id}', headers=headers)
    return response.json()

def compute_kpi(
    token: str,
    machine_id: str,
    kpi_id: str,
    start_date: str,
    end_date: str,
    granularity_days: int,
    granularity_op: str
):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        "machine_id": machine_id,
        "kpi_id": kpi_id,
        "start_date": start_date,
        "end_date": end_date,
        "granularity_days": granularity_days,
        "granularity_op": granularity_op,
    }
    response = r.get(f'{baseUrl}{api_version}kpi/compute', params=params, headers=headers)
    return response.json()