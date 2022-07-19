import pytest
from pytest_tr_odoo.fixtures import env
from odoo.exceptions import ValidationError
from odoo import fields
from datetime import date, datetime, timedelta


@pytest.fixture
def billing_note(env):
    return env['account.billing.note']


@pytest.fixture
def payment_term(env):
    return env['account.payment.term'].create({
        'name': 'the 15th of the month, min 31 days from now',
        'line_ids': [
                (0, 0, {
                    'value': 'balance',
                    'days': 31,
                    'day_of_the_month': 15,
                    'option': 'day_after_invoice_date',
                }),
        ],
    })


@pytest.fixture
def partner(env, payment_term):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'property_payment_term_id': payment_term.id
    })


@pytest.fixture
def account_move(env, payment_term):
    return env['account.move'].create({})


@pytest.mark.parametrize('test_input,expected', [
    ({'amount_residual': 20}, 20),
    ({'amount_residual': 10}, 10),
])
def test__onchange_invoice_id(
        env,
        partner,
        billing_note,
        account_move,
        test_input,
        expected):
    account_move.amount_residual = test_input['amount_residual']
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [
            (0, 0, {
                'invoice_id': account_move.id
            })]
    })
    billing.line_ids._onchange_invoice_id()
    assert billing.line_ids.paid_amount == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'paid_amount': 20}, 'Error!\nThe paid amount over balance.'),
])
def test__onchange_paid_amount(
        env,
        partner,
        billing_note,
        account_move, test_input, expected
):
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [
            (0, 0, {
                'invoice_id': account_move.id,
                'paid_amount': test_input['paid_amount']
            })]
    })
    with pytest.raises(ValidationError) as excinfo:
        billing.line_ids._onchange_paid_amount()
    assert str(excinfo.value) == expected


def test_button_unbill(env, billing_note, account_move, partner):
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [
            (0, 0, {
                'invoice_id': account_move.id
            })]
    })
    account_move.update({
        'billing_note_ids': [(6, 0, [billing.id])],
    })
    for bill in billing.line_ids:
        bill.button_unbill()
        assert bill.is_billing == False
