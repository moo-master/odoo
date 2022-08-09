from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env.ref('sale.sale_order_1')


def test_create(model):
    model.write({
        'x_is_interface': True
    })
    assert model.x_is_interface
