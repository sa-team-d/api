from .define import get_machine_by_id, compute_kpi, login
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

machineId = '6740f1cfa8e3f95f42703128'


def test_compute():
    response = get_machine_by_id(ffmAuth.token, machineId)
    response = compute_kpi(
        ffmAuth.token,
        response['asset_id'],
        response['kpis_ids'][0],
        "2024-09-30 00:00:00",
        "2024-10-07 00:00:00",
        100,
        "sum"
    )
    print(response)
    assert 1
