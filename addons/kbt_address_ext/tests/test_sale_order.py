from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['sale.order']


@pytest.fixture
def sale_order_1(env):
    return env.ref('sale.sale_order_3')


@pytest.fixture
def partner_demo(env):
    return env.ref('base.res_partner_2')


def test__create_invoices(env, model, sale_order_1):
    sale_order_1.write({
        'x_address': 'test address'
    })
    sale_order_1.action_confirm()
    order_line = sale_order_1.mapped('order_line')
    for line in order_line:
        line.write({
            'qty_delivered': line.product_uom_qty
        })

    move_id = sale_order_1._create_invoices()
    assert sale_order_1.x_address == move_id.x_address


def test__onchange_partner_id(env, model, partner_demo, sale_order_1):
    sale_order_1.write({
        'partner_id': partner_demo.id
    })
    sale_order_1._onchange_partner_id()
    assert sale_order_1.x_partner_name == 'Deco Addict'
    assert sale_order_1.x_address == '77 Santa Barbara Rd  Pleasant Hill California United States 94523'
