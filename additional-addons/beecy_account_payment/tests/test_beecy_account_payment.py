import pytest
from pytest_tr_odoo.fixtures import env
from unittest.mock import call
from odoo import fields
from odoo.exceptions import ValidationError
from .fixtures import *


@pytest.fixture
def model(env):
    return env['beecy.account.payment']


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
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_type_receivable(env):
    return env.ref('account.data_account_type_receivable')


@pytest.fixture
def account_type_payable(env):
    return env.ref('account.data_account_type_payable')


@pytest.fixture
def account_type_credit_card(env):
    return env.ref('account.data_account_type_credit_card')


@pytest.fixture
def account_type_current_assets(env):
    return env.ref('account.data_account_type_current_assets')


@pytest.fixture
def account_type_non_current_assets(env):
    return env.ref('account.data_account_type_non_current_assets')


@pytest.fixture
def account_type_non_current_assets(env):
    return env.ref('account.data_account_type_non_current_assets')


@pytest.fixture
def account_type_liquidity(env):
    return env.ref('account.data_account_type_liquidity')


@pytest.fixture
def account_type_other_income(env):
    return env.ref('account.data_account_type_other_income')


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
def account_other_income_income(env):
    account_type = env.ref('account.data_account_type_other_income')
    return env['account.account'].create({
        'code': '4002',
        'name': 'Test Account Income',
        'user_type_id': account_type.id,
        'reconcile': True
    })


@pytest.fixture
def account_payable(env):
    account_type = env.ref('account.data_account_type_payable')
    return env['account.account'].create({
        'code': '5001',
        'name': 'Test Account Payable',
        'user_type_id': account_type.id,
        'reconcile': True
    })


@pytest.fixture
def account_move(env):
    return env['account.move']


@pytest.fixture
def billing_note(env):
    return env['account.billing.note']


@pytest.fixture
def acc_wht5(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT 5',
        'percent': 0.7,
        'sequence': 5,
    })


@pytest.fixture
def acc_wht6(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT 6',
        'percent': 0.7,
        'sequence': 6,
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'payment_type': 'outbound',
      'is_step': True,
      'step': 'two_step', },
     {'state': 'to_approve', 'spy': True}),
    ({'payment_type': 'outbound',
      'is_step': False, 'step': 'one_step'},
     {'state': 'waiting_payment', 'spy': True}),
    ({'payment_type': 'inbound',
      'is_step': True, 'step': 'one_step'},
     {'state': 'waiting_payment', 'spy': True}),
    ({'payment_type': 'inbound',
      'is_step': True, 'step': 'one_step',
      'sequence': 5},
     {'state': 'waiting_payment', 'spy': True}),
])
def test_action_confirm(env,
                        model,
                        monkeypatch,
                        mocker,
                        account_move,
                        partner_demo,
                        journal_cash,
                        product1,
                        payment_term_30days,
                        journal_sale,
                        acc_wht5,
                        acc_wht6,
                        test_input, expected):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'wht_type_id': acc_wht5.id,
        }),
            (0, 0, {
             'product_id': product1.id,
             'wht_type_id': acc_wht6.id,
             })
        ],
    })
    acc_p = model.create({
        'payment_type': test_input.get('payment_type'),
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })],
        'payment_line_wht_ids': [
            (0, 0, {
                'invoice_id': acc_m.id,
                'wht_type_id': acc_wht6.id,
                'percent': acc_wht6.percent,
            }),
            (0, 0, {
                'invoice_id': acc_m.id,
                'wht_type_id': acc_wht5.id,
                'percent': acc_wht5.percent,
            }),
        ]
    })
    if test_input.get('sequence'):
        acc_wht6.write({
            'sequence': test_input.get('sequence')
        })
        with pytest.raises(ValidationError) as excinfo:
            acc_p.action_confirm()
            expected = (
                "You can not select different WHT under the same category."
                " Right now your section 5 or section 6"
                " are under the same category.")
            assert excinfo.value.name == expected
    else:
        if test_input.get('payment_type') == 'outbound':
            env.company.is_module_beecy_account_payment_vendor_steps = test_input.get(
                'is_step')
            env.company.beecy_account_payment_vendor_steps = test_input.get(
                'step')

            if test_input.get('step') == 'two_step':
                spy_approve = mocker.spy(type(acc_p), 'action_to_approve')
                acc_p.action_confirm()
                assert acc_p.state == expected.get('state')
                assert spy_approve.called == expected.get('spy')
            else:
                spy_waiting = mocker.spy(type(acc_p), 'action_waiting_payment')
                acc_p.action_confirm()
                assert acc_p.state == expected.get('state')
                assert spy_waiting.called == expected.get('spy')
        else:
            env.company.is_module_beecy_account_payment_vendor_steps = True
            env.company.beecy_account_payment_vendor_steps = test_input.get(
                'step')
            spy_waiting = mocker.spy(type(acc_p), 'action_waiting_payment')
            acc_p.action_confirm()
            assert acc_p.state == expected.get('state')
            assert spy_waiting.called == expected.get('spy')


def test_action_to_approve(env,
                           model,
                           account_move,
                           partner_demo,
                           journal_cash,
                           product1,
                           payment_term_30days,
                           journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_to_approve()
    assert acc_p.state == 'to_approve'


def test_action_waiting_payment(env,
                                model,
                                account_move,
                                partner_demo,
                                journal_cash,
                                product1,
                                payment_term_30days,
                                journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_waiting_payment()
    assert acc_p.state == 'waiting_payment'


def test_action_to_paid(env,
                        model,
                        account_move,
                        partner_demo,
                        journal_cash,
                        product1,
                        payment_term_30days,
                        journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_to_paid()
    assert acc_p.state == 'paid'


def test_action_set_to_draft(env,
                             model,
                             account_move,
                             partner_demo,
                             journal_cash,
                             product1,
                             payment_term_30days,
                             journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_set_to_draft()
    assert acc_p.state == 'draft'


def test_action_cancel(env,
                       model,
                       account_move,
                       partner_demo,
                       journal_cash,
                       product1,
                       payment_term_30days,
                       journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_cancel()
    assert acc_p.state == 'cancel'


def test_action_reject(env,
                       model,
                       account_move,
                       partner_demo,
                       journal_cash,
                       product1,
                       payment_term_30days,
                       journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_reject()
    assert acc_p.state == 'reject'


@pytest.mark.parametrize('test_input,expected', [
    ({'amount_inv': True,
      'payment_type': 'outbound',
      'vendor_steps': 'two_step'}, 'paid'),
    ({'amount_inv': False,
      'payment_type': 'outbound',
      'vendor_steps': 'two_step'}, 'to_approve'),
    ({'amount_inv': False, 'payment_type': 'outbound',
      'vendor_steps': 'two_step'}, 'to_approve'),
    ({'amount_inv': False, 'payment_type': 'outbound',
      'vendor_steps': 'one_step'}, 'paid'),
    ({'amount_inv': False, 'payment_type': 'inbound',
      'vendor_steps': 'one_step'}, 'paid'),
])
def test_action_validate(env,
                         model,
                         account_move,
                         partner_demo,
                         journal_cash,
                         product1,
                         payment_term_30days,
                         journal_sale,
                         test_input,
                         expected):
    acc_wht_type = env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 10,
    })
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'wht_type_id': acc_wht_type.id
        })],
    })
    acc_p = model.create({
        'payment_type': test_input.get('payment_type'),
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })],
    })
    acc_p.write(
        {'payment_line_wht_ids': [(0, 0, {
            'invoice_line_id': acc_m.invoice_line_ids.id,
            'wht_type_id': acc_m.invoice_line_ids.wht_type_id.id,
            'percent': acc_m.invoice_line_ids.wht_type_id.percent,
            'amount_wht': acc_m.invoice_line_ids.price_subtotal,
        })]
        })
    acc_p.company_id.beecy_account_payment_vendor_steps = test_input.get(
        'vendor_steps')
    if test_input.get('amount_inv'):
        acc_p.payment_line_wht_ids.amount_wht = 10
        acc_p.payment_line_invoice_ids.amount_tobe_paid = 100
        massge = ("The amount to be paid doesn't "
                  "equal to the paid amount + amount WHT.!")
        with pytest.raises(ValidationError) as excinfo:
            acc_p.action_validate()
        assert str(excinfo.value) == massge
        assert acc_p.state == 'to_approve'
    else:
        acc_p.action_validate()
        assert acc_p.state == expected


def test_action_approve(env,
                        model,
                        account_move,
                        partner_demo,
                        journal_cash,
                        product1,
                        payment_term_30days,
                        journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_approve()
    assert acc_p.state == 'draft'


def test_action_account_wht_print(env,
                                  model,
                                  account_move,
                                  partner_demo,
                                  journal_cash,
                                  product1,
                                  payment_term_30days,
                                  journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_account_wht_print()
    assert acc_p.state == 'draft'


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


@pytest.mark.parametrize('test_input,expected', [
    ({'wht': True}, True),
    ({'wht': False}, True),
])
def test_onchange_payment_line_invoice_ids(
        env,
        payment_demo,
        partner_demo,
        account_move,
        product1,
        payment_term_30days,
        journal_sale,
        wht3,
        test_input,
        expected
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
    acc_m2 = acc_m.copy()
    if test_input.get('wht'):
        acc_m2.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': product1.id,
                'wht_type_id': wht3.id,
                'account_id': env.user.property_account_receivable_id.id
            })],
            'line_ids': [(0, 0, {
                'product_id': product1.id,
                'wht_type_id': wht3.id,
                'account_id': env.user.property_account_receivable_id.id
            })],
        })
        payment_demo.write({
            'payment_line_invoice_ids': [(0, 0, {
                'invoice_id': acc_m2.id
            })]
        })
    payment_demo._onchange_payment_line_invoice_ids()
    if payment_demo.payment_line_wht_ids:
        wht_id = payment_demo.payment_line_wht_ids[0]
        assert wht_id.wht_type_id == wht3
        assert expected
    else:
        payment_wht = env['account.payment.line.wht']
        line_wht_ids = payment_demo.payment_line_wht_ids
        assert line_wht_ids == payment_wht
        assert expected


@pytest.fixture
def invoice(env, model, product1,
            partner_demo, account_id,
            account_other_income_income,
            wht3):
    return env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 10,
            'price_unit': product1.lst_price,
            'account_id': product1.property_account_income_id.id if
            product1.property_account_income_id.id else
            account_other_income_income.id,
            'wht_type_id': wht3.id
        })],
    })


@pytest.fixture
def invoice2(env, model, product1,
             partner_demo, account_id,
             account_other_income_income,
             wht3):
    return env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 10,
            'price_unit': product1.lst_price,
            'account_id': product1.property_account_income_id.id if
            product1.property_account_income_id.id else
            account_other_income_income.id,
            'wht_type_id': wht3.id
        })],
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'choose': 'bill_note'}, True),
    ({'choose': 'manual'}, True),
    ({'choose': 'auto'}, True),
    ({'choose': 'bill_note', 'payment': True}, True),
    ({'choose': 'auto', 'payment': True}, True),
])
def test_get_account_move(env,
                          model,
                          payment_demo,
                          partner_demo,
                          invoice,
                          invoice2,
                          journal_cash,
                          billing_note,
                          test_input,
                          expected):
    invoice.state = 'posted'

    acc_bill_note = billing_note.create({
        'partner_id': partner_demo.id,
        'line_ids': [
            (0, 0,
             {
                 'invoice_id': invoice.id
             }),
        ]
    })
    acc_bill_note.state = 'waiting_payment'
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
    })
    account_inv = invoice
    if test_input.get('payment'):
        invoice2.state = 'posted'
        acc_p.write({
            'payment_line_invoice_ids': [(0, 0, {
                'invoice_id': invoice2.id,
            })]
        })
        acc_bill_note.write({
            'line_ids': [
                (0, 0,
                 {
                     'invoice_id': invoice2.id
                 }),
            ]
        })
        account_inv = invoice
    if test_input.get('choose') == 'bill_note':
        domain = [
            ('partner_id', '=', partner_demo.id),
            ('state', '=', 'waiting_payment'),
            ('invoice_id.billing_note_ids', '=', False)
        ]
        val_data = [{'move_id': account_inv.id,
                     'company_id': account_inv.company_id.id,
                     'currency_id': account_inv.currency_id.id,
                     'name': acc_bill_note.name,
                     'partner_id': account_inv.partner_id.id,
                     'invoice_partner_display_name': account_inv.invoice_partner_display_name,
                     'invoice_date': account_inv.invoice_date,
                     'invoice_due_date': account_inv.invoice_date_due,
                     'amount_untaxed_signed': account_inv.amount_untaxed_signed,
                     'amount_total_signed': account_inv.amount_total_signed,
                     'state': account_inv.state,
                     'move_type': account_inv.move_type}]
    else:
        domain = [
            ('partner_id', '=', partner_demo.id),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('move_type', 'in', ['out_invoice', 'out_refund', 'out_debit']),
            ('amount_residual', '>', 0),
            ('billing_note_ids', '=', False)
        ]
        val_data = [{'move_id': account_inv.id,
                     'company_id': account_inv.company_id.id,
                     'currency_id': account_inv.currency_id.id,
                     'name': account_inv.name,
                     'partner_id': account_inv.partner_id.id,
                     'invoice_partner_display_name': account_inv.invoice_partner_display_name,
                     'invoice_date': account_inv.invoice_date,
                     'invoice_due_date': account_inv.invoice_date_due,
                     'amount_untaxed_signed': account_inv.amount_untaxed_signed,
                     'amount_total_signed': account_inv.amount_total_signed,
                     'state': account_inv.state,
                     'move_type': account_inv.move_type}]
    res = payment_demo.get_account_move(domain, test_input.get('choose'))
    assert res == val_data


@pytest.mark.parametrize('test_input,expected', [
    ({'choose': 'bill_note'}, True),
    ({'choose': 'manual'}, True),
    ({'choose': 'auto'}, True),
])
def test_action_get_account_move(env,
                                 payment_demo,
                                 partner_demo,
                                 account_move,
                                 billing_note,
                                 product1,
                                 payment_term_30days,
                                 journal_sale,
                                 wht3,
                                 test_input,
                                 expected):
    acc_move = account_move.create({
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

    res = payment_demo.with_context(
        {'choose': test_input.get('choose'),
         'move_type': ['out_invoice']}).action_get_account_move()
    ex = {'default_move_type': 'out_invoice', 'payment_id': payment_demo.id}
    if test_input.get('choose') != 'auto':
        assert res['context'] == ex
    else:
        assert res


def test_create_account_move_entry(env,
                                   model,
                                   account_move,
                                   partner_demo,
                                   journal_cash,
                                   product1,
                                   payment_term_30days,
                                   journal_sale,
                                   wht3):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'wht_type_id': wht3.id,
            'amount_wht': 30
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
            'amount_tobe_paid': 100,
            'amount_wht': 30
        })]
    })
    acc_p.create_account_move_entry()
    assert acc_p.state == 'paid'


def test_action_cancel_reject_reason_wizard(env,
                                            model,
                                            account_move,
                                            partner_demo,
                                            journal_cash,
                                            product1,
                                            payment_term_30days,
                                            journal_sale,):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.action_cancel_reject_reason_wizard()
    assert acc_p.state == 'draft'


@pytest.mark.parametrize('test_input,expected', [
    ({'amount_paid': 100}, 'หนึ่งร้อยบาทถ้วน'),
    ({'amount_paid': 101}, 'หนึ่งร้อยเอ็ดบาทถ้วน'),
    ({'amount_paid': 100.50}, 'หนึ่งร้อยบาทห้าสิบสตางค์'),
    ({'amount_paid': 100.11}, 'หนึ่งร้อยบาทสิบเอ็ดสตางค์'),
])
def test__amount_total_text(env,
                            model,
                            account_move,
                            partner_demo,
                            journal_cash,
                            product1,
                            payment_term_30days,
                            journal_sale,
                            test_input,
                            expected):

    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })]
    })
    acc_p.amount_paid = test_input.get('amount_paid')
    amount_paid = acc_p._amount_total_text(acc_p.amount_paid)
    assert amount_paid == expected


def test_compute_amount_all(env,
                            model,
                            account_move,
                            partner_demo,
                            journal_cash,
                            product1,
                            payment_term_30days,
                            journal_sale):
    acc_m = account_move.create({
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    acc_p = model.create({
        'payment_type': 'outbound',
        'partner_id': partner_demo.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id
        })],
        'payment_line_wht_ids': [(0, 0, {
            'amount_wht': 100
        })]
    })
    acc_p.action_confirm()
    acc_p.action_to_paid()
    acc_p._compute_amount_all()
    balance = sum(acc_p.payment_line_invoice_ids.mapped(
        'amount_residual')) or 0.0
    to_be_paid = sum(acc_p.payment_line_invoice_ids.mapped(
        'amount_tobe_paid')) or 0.0
    wht = sum(acc_p.payment_line_wht_ids.mapped('amount_wht')) or 0.0
    paid = (sum(acc_p.payment_line_invoice_ids.mapped(
                'amount_tobe_paid')) or 0.0) - (sum(
                    acc_p.payment_line_method_ids.mapped('amount_total')) or 0.0)
    assert acc_p.amount_balance == balance
    assert acc_p.amount_tobe_paid == to_be_paid
    assert acc_p.amount_wht == wht
    assert acc_p.amount_paid == paid


@pytest.mark.parametrize('test_input,expected', [
    ({'method_payment': True},
     ['Manual',
      'ภาษีถูกหัก ณ ที่จ่าย',
      'ส่วนลด',
      'รวมมูลค่าที่ชำระ / Total Payment']),
    ({'method_payment': False},
     ['ภาษีถูกหัก ณ ที่จ่าย',
      'ส่วนลด',
      'รวมมูลค่าที่ชำระ / Total Payment']),
])
def test_prepare_lines_payment_method(
        env,
        model,
        payment_customer,
        payment_method_line_pay,
        test_input,
        expected):
    if test_input['method_payment']:
        payment_customer.write({
            'payment_line_method_ids': [(0, 0, {
                'payment_method_line_id': payment_method_line_pay.id,
                'amount_total': 100
            })]
        })
        res = payment_customer.prepare_lines_payment_method()
        assert res == expected
    else:
        res = payment_customer.prepare_lines_payment_method()
        assert res == expected


@pytest.mark.parametrize('test_input,expected',
                         [({'method_payment': True},
                           ['100.00', '100.00', '-', '100.00']),
                             ({'method_payment': False},
                              ['100.00', '-', '0.00']),
                          ])
def test_prepare_amount_payment_method(
        env,
        model,
        payment_customer,
        payment_method_line_pay,
        test_input,
        expected):
    if test_input['method_payment']:
        payment_customer.write({
            'payment_line_method_ids': [(0, 0, {
                'payment_method_line_id': payment_method_line_pay.id,
                'amount_total': 100
            })]
        })
        res = payment_customer.prepare_amount_payment_method()
        assert res == expected
    else:
        res = payment_customer.prepare_amount_payment_method()
        assert res == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'line_invoice': True}, True),
    ({'line_invoice': False}, False),
])
def test_check_count_line_invoice(
        env,
        model,
        payment_customer,
        invoice_line_payment,
        test_input,
        expected):
    invoice_2 = invoice_line_payment.copy()
    if test_input['line_invoice']:
        payment_customer.write({
            'payment_line_invoice_ids': [(0, 0, {
                'invoice_id': invoice_2.id
            })],
        })
        payment_customer.check_count_line_invoice()
        assert payment_customer.is_check_line_invoice == expected
    else:
        payment_customer.check_count_line_invoice()
        assert payment_customer.is_check_line_invoice == expected


@pytest.mark.parametrize('test_input', [
    ({'view_tree': "beecy_account_payment.view_beecy_account_payment_tree",
      'default_payment_type': "inbound"}),
    ({'view_tree': "beecy_account_payment.view_beecy_account_supplier_payment_tree",
      'default_payment_type': "outbound"}),
])
def test_fields_view_get(env, model, test_input, monkeypatch, mocker):
    invoice_tree = env.ref(test_input['view_tree'])
    customer = env.ref(
        'beecy_account_payment.action_payment_receipt_report')
    vendor = env.ref(
        'beecy_account_payment.action_payment_voucher_report')
    data_report = []
    spy_prepare_data_report = mocker.spy(type(model), 'prepare_data_report')
    view_infos_invoice = model.with_context(
        default_payment_type=test_input['default_payment_type']).fields_view_get(
        view_id=invoice_tree.id, toolbar=True)

    if view_infos_invoice['toolbar']:
        spy_prepare_data_report.assert_called_once_with(
            model, test_input['default_payment_type'])
        for report in view_infos_invoice['toolbar']['print']:
            data_report.append(report['id'])
            if test_input['view_tree'] == "abeecy.account.payment.tree":
                assert vendor.id not in data_report
            elif test_input[
                    'view_tree'] == "beecy.account.supplier.payment.tree":
                assert customer.id not in data_report


@pytest.mark.parametrize('test_input', [
    ({'report_templte': "beecy_account_payment.action_payment_voucher_report",
      'default_payment_type': "inbound"}),
    ({'report_templte': "beecy_account_payment.action_payment_receipt_report",
      'default_payment_type': "outbound"}),
])
def test_prepare_action_menu_report(env, test_input):
    customer = env.ref(
        'beecy_account_payment.action_payment_receipt_report')
    vendor = env.ref(
        'beecy_account_payment.action_payment_voucher_report')
    payment = env['beecy.account.payment']

    res = payment.prepare_action_menu_report(
        [test_input.get('report_templte')])
    if test_input.get('default_payment_type') == 'inbound':
        assert res == [vendor.id]
    if test_input.get('default_payment_type') == 'outbound':
        assert res == [customer.id]
