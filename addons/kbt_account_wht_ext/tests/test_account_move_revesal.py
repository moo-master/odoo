from pytest_tr_odoo.fixtures import env
import pytest
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.move.reversal']


@pytest.fixture
def product(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def account_type(env):
    return env['account.account.type'].create({
        'name': 'Test Type',
        'type': 'other',
        'internal_group': 'income',
    })


@pytest.fixture
def account_id(env, account_type):
    return env['account.account'].create({
        'code': '1',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'JV Sale',
        'type': 'sale',
        'code': 'SO',
        'company_id': env.company.id,
    })


@pytest.fixture
def invoice(env, partner_demo, product, account_id):
    inv = env['account.move'].create({
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_date': '2022-01-01',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 1000,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id,
        })],
    })
    return inv


def test_reverse_moves(
        env,
        model,
        invoice,
        journal):
    invoice.action_post()
    wizard_id = model.with_context(active_ids=invoice.ids).create({
        'journal_id': journal.id,
        'date_mode': 'custom',
        'reason': 'test',
        'move_ids': invoice,
    })
    res = wizard_id.reverse_moves()
    credit_note = env['account.move'].browse([res.get('res_id')])
    assert credit_note.x_invoice_id.id == invoice.id
