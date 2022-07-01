from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['api.service']


@pytest.fixture
def route(env):
    return env['api.service.route']


@pytest.mark.parametrize('test_input,expected', [
    ({'code': 204}, 'success'),
    ({'code': 500}, 'fail'),
])
def test__get_log_status_incoming_kbt(model, test_input, expected, route):
    res = {
        'code': test_input['code']
    }
    result = model._get_log_status_incoming_kbt(response=res, route=route)
    assert result == expected
