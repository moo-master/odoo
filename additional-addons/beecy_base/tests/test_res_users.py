import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.users']


def test_create(model):
    user_id = model.create({
        'name': 'Test',
        'login': 'Test',
    })
    assert user_id.name == 'Test'
    assert user_id.login == 'Test'
