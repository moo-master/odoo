import pytest
from pytest_tr_odoo.fixtures import env
from unittest.mock import call
from odoo import fields


@pytest.fixture
def model(env):
    return env['beecy.account.payment']


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
def payment_term_45days(env):
    payment_term = env.ref('account.account_payment_term_45days')
    return payment_term


@pytest.fixture
def payment_term_2months(env):
    payment_term = env.ref('account.account_payment_term_2months')
    return payment_term


@pytest.fixture
def payment_term_end_following_month(env):
    payment_term = env.ref('account.account_payment_term_end_following_month')
    return payment_term


@pytest.fixture
def payment_term_advance_60days(env):
    payment_term = env.ref('account.account_payment_term_advance_60days')
    return payment_term


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def journal_purchase(env):
    return env['account.journal'].search([
        ('type', '=', 'purchase'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def journal_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def wht5(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 5%',
        'percent': 3.0,
    })


@pytest.fixture
def journal_bank(env):
    return env['account.journal'].search([
        ('type', '=', 'bank'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def journal_general(env):
    return env['account.journal'].search([
        ('type', '=', 'general'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def account_move(env):
    return env['account.move']


@pytest.fixture
def billing_note(env):
    return env['account.billing.note']


@pytest.fixture
def acc_move_wizard(env):
    return env['payment.account.move.wizard']


@pytest.fixture
def payment_demo(env,
                 model,
                 account_move,
                 partner_demo,
                 journal_cash,
                 product1,
                 payment_term_30days,
                 journal_sale,
                 wht3,
                 ):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'wht_type_id': wht3.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id,
        })]
    })

    return acc_p


def test_action_confirm(env,
                        payment_demo,
                        partner_demo,
                        account_move,
                        billing_note,
                        acc_move_wizard,
                        product1,
                        payment_term_30days,
                        journal_sale,
                        wht3
                        ):
    acc_move = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'wht_type_id': wht3.id
        })],
    })
    acc_move.state = 'posted'
    acc_bill_note = billing_note.create({
        'partner_id': partner_demo.id,
        'line_ids': [
            (0, 0,
             {
                 'invoice_id': acc_move.id
             })]
    })
    acc_bill_note.state = 'waiting_payment'
    wizard = acc_move_wizard.create({})
    wizard.with_context(
        {'payment_id': payment_demo.id}).action_confirm()
    assert len(payment_demo.payment_line_invoice_ids) == 2
