from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['org.level']


def test_create_org_level(env, model):
    org_level = model.create({
        'level': 123456789,
        'description': "test",
    })
    org_level_line = env['org.level.line'].create([
        {'limit': 123,
         'org_level_id': org_level.id}
    ])
    assert org_level_line.limit == 123
