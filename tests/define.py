import requests as r
import os
from configparser import ConfigParser

def get_pytest_env_vars():
    # Initialize parser
    config = ConfigParser()
    
    # Read pytest.ini file
    config.read('pytest.ini')
    
    # Get env section and convert to dict
    env_vars = {}
    config = config['pytest']
    if 'env' in config:
        envs = config['env'].strip().split('\n')
        # envs = [env.split('=') for env in envs]
        for item in envs:
            key, value = item.split('=')
            env_vars[key] = value.strip()
            
    return env_vars

baseUrl = os.environ.get('BASE_URL', None)
api_version = os.environ.get('API_VERSION', None)
firebaseRestApi = os.environ.get('FIREBASE_REST_API',None)
firebaseWebApiKey = os.environ.get('FIREBASE_WEB_API_KEY', None)

if not baseUrl:
    env_vars = get_pytest_env_vars()
    baseUrl = env_vars['BASE_URL']
    api_version = env_vars['API_VERSION']
    firebaseRestApi = env_vars['FIREBASE_REST_API']
    firebaseWebApiKey = env_vars['FIREBASE_WEB_API_KEY']



def login(email: str, pwd: str):
    body = {
        "email": email,
        "password": pwd,
        "returnSecureToken": True
    }

    response = r.post(f'{firebaseRestApi}:signInWithPassword?key={firebaseWebApiKey}', json=body)
    return response.json()

class FFMAuth:
    uid: str
    email: str
    pwd: str
    token: str


ffmAuth = FFMAuth()
ffmAuth.email = 'ffm@example.com'
ffmAuth.pwd = 'passwordffm'
response = login(ffmAuth.email, ffmAuth.pwd)
ffmAuth.uid = response['localId']
ffmAuth.token = response['idToken']


    

def get_machine_by_id(headers: str, id: str):
   
    response = r.get(f'{baseUrl}{api_version}machine/{id}', headers=headers)
    return response.json()

def compute_kpi(
    headers: str,
    machine_id: str,
    kpi_id: str,
    start_date: str,
    end_date: str,
    granularity_days: int,
    granularity_op: str
):

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



if __name__ == "__main__":
    print(f"Token:\n\n {ffmAuth.token}\n\n")