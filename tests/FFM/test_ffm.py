import sys

import pytest
sys.path.append("..")

from define import get_machine_by_id, compute_kpi, ffmAuth
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {ffmAuth.token}"}


def test_compute(auth_headers):

    machineId = '6740f1cfa8e3f95f4270312f'
    json_response = get_machine_by_id(auth_headers, machineId)

    machine = json_response['data']

    assert json_response['success'] == True

    response = compute_kpi(
        auth_headers,
        machine['_id'],
        machine['kpis_ids'][0],
        "2024-09-30 00:00:00",
        "2024-10-07 00:00:00",
        100,
        "sum",
    )
    
    if isinstance(response['data'], list):
        assert 1
    else:
        assert 0


