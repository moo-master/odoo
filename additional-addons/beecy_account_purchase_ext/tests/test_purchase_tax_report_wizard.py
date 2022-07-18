import pytest
from pytest_tr_odoo.fixtures import env
from unittest.mock import call


@pytest.fixture
def model(env):
    return env['purchase.tax.report.wizard']


@pytest.fixture
def account_move(env):
    return env['account.move']


@pytest.fixture
def product1(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def product2(env):
    product = env.ref('product.product_product_3')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def partner_1(env):
    partner = env.ref('base.res_partner_1')
    return partner


@pytest.fixture
def payment_term_30days(env):
    payment_term = env.ref('account.account_payment_term_30days')
    return payment_term


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.mark.parametrize('test_input,expected', [
    ({'company': True}, True),
    ({'company': False}, True),
])
def test_button_export_xlsx(
        env,
        model,
        account_move,
        partner_demo,
        payment_term_30days,
        journal_sale,
        product1,
        test_input,
        expected
):

    account_move.create({
        'move_type': 'out_invoice',
        'invoice_date': '2022-03-23',
        'company_id': env.company.id,
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    account_move.state = 'posted'
    purchase_tax = model.create({
        'company_ids': env.company.ids,
        'start_date': '2022-03-01',
    })
    if not test_input.get('company'):
        purchase_tax.write({'company_ids': False})
    res = purchase_tax.button_export_xlsx()
    assert res['name'] == 'Purchase Tax Report'
