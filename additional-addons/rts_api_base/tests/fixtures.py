import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def route(env):
    return env['api.service.route'].create({
        'name': 'Fresh',
        'key': 'fresh',
        'method': 'get',
        'path': 'get/{id}'
    })


@pytest.fixture
def service(env, route):
    return env['api.service'].create({
        'name': 'Consultant',
        'key': 'cons',
        'base_url': 'http://alisa.name',
        'route_ids': [(4, route.id)]
    })


@pytest.fixture
def log(env, service, route):
    return env['api.logs'].create({
        'service_id': service.id,
        'route_id': route.id,
        'request_url': 'https://test.com/v1',
        'request_header': '{"content-type": "application/json"}',
        'request_body': '{"Cheese": "Hungary"}',
        'response_status_code': '200',
        'response_body': '{"Cheese": "Supervisor"}'
    })
