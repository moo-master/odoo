from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['stock.picking']


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def product_demo(env):
    product = env.ref('sale.advance_product_0')
    return product


@pytest.fixture
def company_demo(env):
    company = env.ref('stock.res_company_1')
    return company


@pytest.fixture
def warehouse(env):
    warehouse = env.ref('stock.warehouse0')
    return warehouse


@pytest.fixture
def stock_picking_type(env, company_demo, warehouse):
    stock = env['stock.picking.type'].create({
        'name': 'test',
        'sequence_code': 'test',
        'code': 'incoming',
        # 'company_id': company_demo.id,
        'warehouse_id': warehouse.id,
    })
    return stock


def test_create_field(env, model, stock_picking_type):
    res = model.create({
        'picking_type_id': stock_picking_type.id,
        'x_is_interface': False,
    })
    assert res
