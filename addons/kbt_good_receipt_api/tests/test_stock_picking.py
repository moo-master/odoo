from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['stock.picking']


@pytest.fixture
def stock_picking(env):
    stock_picking = env.ref('stock.incomming_chicago_warehouse')
    return stock_picking


def test_create_field(env, model, stock_picking):
    stock_picking.write({
        'x_is_interface': True,
        'x_bill_date': '2022-01-01',
        'x_bill_reference': 'ref',
    })
    assert stock_picking.x_is_interface
