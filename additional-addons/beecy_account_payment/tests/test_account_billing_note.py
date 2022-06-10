import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.billing.note']


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
def journal_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def billing_note(env,
                 model,
                 partner_demo,
                 payment_term_30days,
                 product1,):
    acc_m = env['account.move'].create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
    })
    acc_m.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'account_id': env.user.property_account_receivable_id.id
        })],
    })
    acc_m.state = 'posted'
    res = model.create({
        'partner_id': partner_demo.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [(0, 0,
                      {
                          'invoice_id': acc_m.id
                      }),
                     ]
    })
    res.action_validate()
    return res


def test_action_register_payment(
        env,
        billing_note,
):
    res = billing_note.action_register_payment()
    action = env.ref(
        'beecy_account_payment.beecy_action_account_payments')
    assert res['id'] == action.id


def test__compute_count_payment(env,
                                model,
                                payment_term_30days,
                                journal_cash,
                                partner_demo,
                                product1,):
    acc_m = env['account.move'].create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
    })
    acc_m.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'price_unit': 100,
            'account_id': env.user.property_account_receivable_id.id
        })],
    })
    acc_m.state = 'posted'
    acc_p = env['beecy.account.payment'].create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id,
        })]
    })
    res = model.create({
        'partner_id': partner_demo.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [(0, 0,
                      {
                          'invoice_id': acc_m.id
                      }),
                     ],
        'beecy_payment_ids': acc_p.ids,
    })
    res._compute_count_payment()
    assert res.count_payment == 1
