import sys
sys.path.append("..")

from define import get_machine_by_id, compute_kpi, login, FFMAuth
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



ffmAuth = FFMAuth()
ffmAuth.email = 'ffm@example.com'
ffmAuth.pwd = 'passwordffm'
response = login(ffmAuth.email, ffmAuth.pwd)
ffmAuth.uid = response['localId']
ffmAuth.token = response['idToken']

machineId = '6740f1cfa8e3f95f4270312f'


def test_compute():
    response = get_machine_by_id(ffmAuth.token, machineId)

    if response.get("detail", None) == "Not Found":
        assert 0

    response = compute_kpi(
        ffmAuth.token,
        response['_id'],
        response['kpis_ids'][0],
        "2024-09-30 00:00:00",
        "2024-10-07 00:00:00",
        100,
        "sum",
    )
    
    if isinstance(response, list):
        assert 1
    else:
        assert 0
