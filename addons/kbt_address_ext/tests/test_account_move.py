from pytest_tr_odoo.fixtures import env
from odoo import fields, Command
import pytest


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def customer_invoice(env, model):
    return model.create({
        'move_type': 'out_invoice',
        'partner_id': env.ref('base.res_partner_2').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref('account.account_payment_term_immediate').id,
        'invoice_date': fields.Date.today(),
        'invoice_line_ids': [
            Command.create({'product_id': env.ref('product.consu_delivery_02').id, 'quantity': 5}),
            Command.create({'product_id': env.ref('product.consu_delivery_03').id, 'quantity': 5}),
        ],
    })


def test_create_new_field(customer_invoice):
    customer_invoice.write({
        'x_address': 'test address'
    })
    assert customer_invoice.x_address
