import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields
from datetime import date, datetime, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import re
from .fixtures import *


@pytest.fixture
def billing_note(env):
    return env['account.billing.note']


def test__onchange_partner_id(env, partner, payment_term, billing_note):
    partner2 = partner.copy()
    payment_term2 = payment_term.copy()
    partner2.property_payment_term_id = payment_term2.id
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today()
    })
    billing.partner_id = partner2.id
    billing._onchange_partner_id()
    assert billing.payment_term_id.id == payment_term2.id


def test__onchange_payment_term_id(env, billing_note, payment_term):
    billing_note.new({
        'bill_date': fields.Date.today(),
    })
    billing_note.payment_term_id = payment_term
    billing_note._onchange_payment_term_id()
    assert billing_note.payment_date == fields.Date.today(
    ) + timedelta(days=payment_term.line_ids[0].days)


@pytest.mark.parametrize('test_input,expected', [
    ({'day': 20}, (fields.Date.today() + timedelta(20))),
    ({'day': 10}, (fields.Date.today() + timedelta(10))),
    ({'day': 1, 'name': 'End of Following Month'}, (
        (fields.Date.today() + relativedelta(months=1)).replace(
            day=monthrange((fields.Date.today() + relativedelta(months=1)).year,
                           (fields.Date.today() + relativedelta(months=1)).month)[1]))),
])
def test__onchange_payment_term_id(
        env,
        partner,
        payment_term,
        billing_note,
        test_input,
        expected):
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today()
    })
    payment_term2 = payment_term.copy()
    if test_input['day'] == 1:
        payment_term2.name = test_input['name']

    payment_term2.line_ids.days = test_input['day']
    billing.payment_term_id = payment_term2.id
    billing._onchange_payment_term_id()
    assert billing.payment_date == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'line_ids': True}, 'BL-'),
    ({'line_ids': False},
        "Billing note must have at least one line to validate"),
])
def test_action_validate(
        env,
        partner,
        account_move,
        payment_term,
        billing_note_wizard,
        test_input,
        expected):
    if test_input.get('line_ids'):
        billing_note_wizard.line_ids.create({
            'billing_note_id': billing_note_wizard.id,
            'invoice_id': account_move.id,
        })
        billing_note_wizard.action_validate()
        assert re.match(
            expected.format(r'\d\d\d\d\d\d\d\d\d'),
            billing_note_wizard.name)
    else:
        with pytest.raises(ValidationError) as excinfo:
            billing_note_wizard.action_validate()
        assert str(excinfo.value) == expected


def test_print_billing_note(env, partner, payment_term, billing_note,):
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today()
    })
    validate = billing.action_print_billing_note()
    assert validate is None


@pytest.mark.parametrize('test_input,expected',
                         [({'payment_state': 'paid',
                            'billing_note': True,
                            'billing_no': False},
                           {'bill': 2,
                            'no_bill': 3}),
                             ({'payment_state': 'not_paid',
                               'billing_note': True,
                               'billing_no': False},
                              {'bill': 2,
                                 'no_bill': 3}),
                          ])
def test_action_filter(env,
                       billing_note_wizard,
                       account_move,
                       test_input, expected,
                       monkeypatch,
                       mocker):
    spy_action_showall = mocker.spy(type(billing_note_wizard),
                                    'prepare_invoice_filter')
    account_move2 = account_move.copy()
    account_move3 = account_move2.copy()
    account_move.state = 'posted'
    account_move2.state = 'posted'
    account_move3.state = 'posted'
    if test_input['billing_note']:
        account_move3.billing_note_ids = [(4, billing_note_wizard.id)]
        billing_note_wizard.action_filter()
        wizard = env['account.invoice.wizard'].search([
            ('billing_note_id', '=', billing_note_wizard.id)
        ])
        spy_action_showall.assert_any_call(billing_note_wizard)
        assert len(wizard.invoice_id) == expected['bill']
    if not test_input['billing_no']:
        account_move3.billing_note_ids = False
        billing_note_wizard.action_filter()
        wizard_no = env['account.invoice.wizard'].search([
            ('billing_note_id', '=', billing_note_wizard.id)
        ])
        spy_action_showall.assert_any_call(billing_note_wizard)
        assert len(wizard_no.invoice_id) == expected['no_bill']


@pytest.mark.parametrize('test_input,expected',
                         [({'payment_state': 'paid',
                            'billing_note': True,
                            'billing_no': False},
                           {'bill': 2,
                            'no_bill': 3}),
                             ({'payment_state': 'not_paid',
                               'billing_note': True,
                               'billing_no': False},
                              {'bill': 2,
                                 'no_bill': 3}),
                          ])
def test_action_showall(
        env,
        billing_note_wizard,
        account_move,
        test_input, expected,
        monkeypatch,
        mocker):
    spy_action_showall = mocker.spy(type(billing_note_wizard),
                                    'prepare_invoice_all')
    billing = billing_note_wizard.copy()
    account_move2 = account_move.copy()
    account_move3 = account_move2.copy()
    account_move.state = 'posted'
    account_move2.state = 'posted'
    account_move3.state = 'posted'
    if test_input['billing_note']:
        account_move3.billing_note_ids = [(4, billing.id)]
        billing_note_wizard.action_showall()
        spy_action_showall.assert_any_call(
            billing_note_wizard)
        assert len(billing_note_wizard.line_ids) == expected['bill']
    if not test_input['billing_no']:
        account_move3.billing_note_ids = False
        billing_note_wizard.action_showall()
        spy_action_showall.assert_any_call(
            billing_note_wizard)
        assert len(billing_note_wizard.line_ids) == expected['no_bill']


@pytest.mark.parametrize('test_input,expected',
                         [({'payment_state': 'paid',
                            'billing_note': True,
                            'billing_no': False},
                           {'bill': 2,
                            'no_bill': 2}),
                             ({'payment_state': 'not_paid',
                               'billing_note': True,
                               'billing_no': False},
                              {'bill': 2,
                                 'no_bill': 2}),
                          ])
def test_prepare_invoice(env,
                         billing_note_wizard,
                         account_move,
                         test_input, expected,
                         monkeypatch,
                         mocker):
    billing_note_wizard.line_ids.create({
        'billing_note_id': billing_note_wizard.id,
        'invoice_id': account_move.id,
    })
    billing = billing_note_wizard.copy()
    account_move2 = account_move.copy()
    account_move3 = account_move2.copy()
    account_move.state = 'posted'
    account_move2.state = 'posted'
    account_move3.state = 'posted'
    if test_input['billing_note']:
        account_move3.billing_note_ids = [(4, billing.id)]
        prepare_billing = billing_note_wizard._prepare_invoice()
        assert len(prepare_billing) == expected['bill']
    if not test_input['billing_no']:
        account_move3.billing_note_ids = False
        prepare_billing = billing_note_wizard._prepare_invoice()
        assert len(prepare_billing) == expected['no_bill']


@pytest.mark.parametrize('test_input,expected',
                         [({'payment_state': 'paid',
                            'billing_note': True,
                            'billing_no': False,
                            },
                           {'bill': 1,
                            'no_bill': 2,
                            'paid_amount': 500.0}),
                          ({'payment_state': 'not_paid',
                              'billing_note': True,
                            'billing_no': False, },
                             {'bill': 1,
                              'no_bill': 2,
                              'paid_amount': 500.0}),
                          ({'move_type': 'out_refund',
                              'payment_state': 'paid',
                              'billing_note': True,
                              'billing_no': False, },
                             {'bill': 1,
                              'no_bill': 2,
                              'paid_amount': -500.0}),
                          ])
def test_prepare_invoice_all(env,
                             billing_note_wizard,
                             account_move,
                             test_input, expected,
                             monkeypatch,
                             mocker):
    billing_note_wizard.line_ids.create({
        'billing_note_id': billing_note_wizard.id,
        'invoice_id': account_move.id,
    })
    if test_input.get('move_type'):
        account_move.move_type = test_input.get('move_type')
    billing = billing_note_wizard.copy()
    account_move.amount_residual = 500.0
    account_move2 = account_move.copy()
    account_move2.amount_residual = 500.0
    account_move3 = account_move2.copy()
    account_move.state = 'posted'
    account_move2.state = 'posted'
    account_move3.state = 'posted'
    if test_input['billing_note']:
        account_move3.billing_note_ids = [(4, billing.id)]
        prepare_billing = billing_note_wizard.prepare_invoice_all()
        assert prepare_billing[0][2].get(
            'paid_amount') == expected['paid_amount']
        assert len(prepare_billing) == expected['bill']
    if not test_input['billing_no']:
        account_move3.billing_note_ids = False
        prepare_billing = billing_note_wizard.prepare_invoice_all()
        assert len(prepare_billing) == expected['no_bill']


@pytest.mark.parametrize('test_input,expected',
                         [({
                             'billing_note': True,
                             'billing_no': False},
                           {'bill': 1,
                            'no_bill': 2}),
                             ({
                                 'billing_note': True,
                                 'billing_no': False},
                              {'bill': 1,
                               'no_bill': 2}),
                          ])
def test_prepare_invoice_filter(env,
                                billing_note_wizard,
                                account_move,
                                test_input, expected,
                                monkeypatch,
                                mocker):
    billing_note_wizard.line_ids.create({
        'billing_note_id': billing_note_wizard.id,
        'invoice_id': account_move.id,
    })
    billing = billing_note_wizard.copy()
    account_move2 = account_move.copy()
    account_move3 = account_move2.copy()
    account_move.state = 'posted'
    account_move2.state = 'posted'
    account_move3.state = 'posted'
    if test_input['billing_note']:
        account_move3.billing_note_ids = [(4, billing.id)]
        prepare_billing = billing_note_wizard.prepare_invoice_filter()
        assert len(prepare_billing) == expected['bill']
    if not test_input['billing_no']:
        account_move3.billing_note_ids = False
        prepare_billing = billing_note_wizard.prepare_invoice_filter()
        assert len(prepare_billing) == expected['no_bill']


def test_button_customer_confirm(partner, billing_note):
    bill_note = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
    })
    bill_note.button_customer_confirm()
    assert bill_note.state == 'waiting_payment'


def test_action_cancel_reject_reason_wizard(env, partner, billing_note,):
    invoice = env['account.move'].create({})
    bill_note = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [(0, 0, {'invoice_id': invoice.id})],
    })
    invoice.update({
        'billing_note_ids': [(6, 0, [bill_note.id])],
    })
    bill_note.action_cancel_reason()
    wizard = bill_note.action_cancel_reject_reason_wizard()
    assert wizard


def test_action_paid(env, partner, billing_note):
    product_a = env['product.product'].create({'name': 'product A'})
    invoice_id = env['account.move'].create({
        'partner_id': partner.id,
        'invoice_line_ids': [
            (0, 0,
             {'product_id': product_a.id,
              'name': product_a.name}
             )]
    })
    invoice_id2 = env['account.move'].create({
        'partner_id': partner.id,
        'invoice_line_ids': [
            (0, 0,
             {'product_id': product_a.id,
              'name': product_a.name}
             )]
    })
    billing = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [(0, 0,
                      {
                          'invoice_id': invoice_id.id
                      }),
                     (0, 0,
                      {
                          'invoice_id': invoice_id2.id
                      })
                     ]
    })
    billing.action_paid()
    assert billing.state == 'paid'


def test_amount_total_text(env, billing_note_wizard, account_move,):
    billing_note_wizard.line_ids.create({
        'billing_note_id': billing_note_wizard.id,
        'invoice_id': account_move.id,
    })
    th_bath = billing_note_wizard._amount_total_text(
        sum(billing_note_wizard.line_ids.mapped('balance')))
    assert th_bath == "ศูนย์บาทถ้วน"


def test_unlink(billing_note, partner):
    bills = billing_note
    for row in range(2):
        state = 'bill'
        if row == 0:
            state = 'draft'
        bills |= billing_note.create({
            'state': state,
            'partner_id': partner.id,
            'bill_date': fields.Date.today(),
            'payment_date': fields.Date.today()
        })
    res = bills.unlink()
    assert res


@pytest.mark.parametrize('test_input,expected',
                         [({
                             'balance1': 1.00,
                             'balance2': 2.00,
                         },
                             {'balance_amount': 3.00, }),
                             ({
                              'balance1': 1.00,
                              'balance2': -2.00,
                              },
                              {'balance_amount': -1.00, }),
                         ])
def test__compute_balance(env, partner, billing_note, test_input, expected,):
    invoice = env['account.move'].create({})
    invoice_copy = invoice.copy()
    bill_note = billing_note.create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [
            (0, 0, {'invoice_id': invoice.id, 'balance': test_input.get('balance1')}),
            (0, 0, {'invoice_id': invoice_copy.id, 'balance': test_input.get('balance2')})
        ],
    })
    bill_note._compute_balance()
    assert bill_note.balance_amount == expected.get('balance_amount')
