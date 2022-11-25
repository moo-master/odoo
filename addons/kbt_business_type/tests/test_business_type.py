from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['business.type']


def test__onchange_is_unearn_revenue(env, model):
    business_type = model.new({
        'x_revenue_account_id': 1,
        'is_unearn_revenue': False
    })
    business_type._onchange_is_unearn_revenue()
    assert not business_type.x_revenue_account_id
