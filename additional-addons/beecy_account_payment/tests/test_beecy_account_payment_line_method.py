import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.payment.line.method']


@pytest.fixture
def payment_method_inbound(env):
    return env.ref('account.account_payment_method_manual_in')


@pytest.fixture
def payment_method_outbound(env):
    return env.ref('account.account_payment_method_manual_out')


@pytest.mark.parametrize('test_input,expected', [
    ({'payment_type': 'inbound'}, [('payment_type', '=', 'inbound')]),
    ({'payment_type': 'outbound'}, [('payment_type', '=', 'outbound')]),
])
def test__domain_payment_method_id(
        model,
        test_input,
        expected):
    res = model.with_context(
        {'default_payment_type': test_input.get('payment_type')}
    )._domain_payment_method_id()
    assert res == expected


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
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


@pytest.fixture
def journal_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def product1(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def payment_method_sale(env):
    res = env['account.payment.method'].search(
        [('payment_type', '=', 'outbound')], limit=1)
    return res


@pytest.fixture
def payment_cash(env, journal_sale, payment_method_sale):
    return env['account.payment.method.line'].create({
        'journal_id': journal_sale.id,
        'name': 'Manual',
        'payment_method_id': payment_method_sale.id,
    })


def test__onchange_methods_ids(env,
                               partner_demo,
                               payment_term_30days,
                               journal_sale,
                               product1,
                               wht3,
                               payment_cash,
                               journal_cash):
    acc_move = env['account.move'].create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'quantity': 1,
            'price_unit': 100,
            'wht_type_id': wht3.id
        })],
    })

    acc_p = env['beecy.account.payment'].create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_move.id
        })],
        'payment_line_method_ids': [(0, 0, {
            'payment_method_line_id': payment_cash.id,
            'amount_total': 100,
        })]
    })
    amount_total = sum(acc_p.payment_line_method_ids.mapped('amount_total'))
    acc_p.payment_line_method_ids._onchange_methods_ids()
    assert amount_total == 100
