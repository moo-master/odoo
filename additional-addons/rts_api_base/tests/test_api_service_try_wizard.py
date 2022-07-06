import pytest
from pytest_tr_odoo.fixtures import env
from .fixtures import *


@pytest.fixture
def try_wizard(env, service, route):
    return env['api.service.try.wizard'].create({
        'service_id': service.id,
        'route_id': route.id,
    })


def test_action_confirm(monkeypatch, mocker, env, try_wizard):
    Service = env['api.service']
    monkeypatch.setattr(type(Service), 'requests',
                        lambda a, b, path_params, headers, params, data: True)
    spy = mocker.spy(type(Service), 'requests')
    try_wizard.action_confirm()
    spy.assert_called_once_with(
        Service,
        try_wizard.route_id.reference,
        False,
        {},
        {},
        {}
    )
