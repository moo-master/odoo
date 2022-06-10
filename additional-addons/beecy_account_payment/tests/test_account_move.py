import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields
from datetime import datetime
from odoo.exceptions import ValidationError


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def product(env):
    return env['product.product'].create({
        'name': 'Mini Fan'
    })


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
def account_receivable(env, account_type):
    return env['account.account'].create({
        'code': '1000',
        'name': 'Test Receivable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_payable(env, account_type):
    return env['account.account'].create({
        'code': '2000',
        'name': 'Test Payable Account',
        'user_type_id': account_type.id
    })


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
def partner(env, payment_term, account_receivable, account_payable):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


def test__domain_reason_id(env, model):
    res = model._domain_reason_id()
    ir_model = env['ir.model'].search([
        ('model', '=', 'account.move')
    ])
    expected = ['|', ('model_ids', '=', ir_model.id),
                ('model_ids', '=', False)]
    assert res == expected


@pytest.fixture
def account_account_type(env):
    return env['account.account.type'].create({
        'name': 'credit',
        'type': 'liquidity',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account(env, account_account_type):
    return env['account.account'].create({
        'name': 'acc acc',
        'user_type_id': account_account_type.id,
        'code': '01',
    })


@pytest.fixture
def account_journal(env, account_account):
    return env['account.journal'].create({
        'name': "acc journal",
        'type': 'sale',
        'code': "abc",
        'default_account_id': account_account.id,
    })


def test_compute_credit_debit_note_count(model, account_journal):
    acc_move_ref = model.create({
        'journal_id': account_journal.id,
    })
    acc_move = model.create({
        'journal_id': account_journal.id,
        'credit_note_ids': [(0, 0, {
            'invoice_ref_id': acc_move_ref.id,
            'move_type': 'in_refund',
        })],
    })
    acc_move._compute_credit_debit_note_count()
    assert acc_move.credit_note_count == 1
# ------------------------


@pytest.fixture
def account_account_type_act(env):
    return env['account.account.type'].create({
        'name': 'credit 12',
        'type': 'liquidity',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account_act(env, account_account_type_act):
    return env['account.account'].create({
        'name': 'acc acc 12',
        'user_type_id': account_account_type_act.id,
        'code': '01',
    })


@pytest.fixture
def account_journal_act(env, account_account_act):
    return env['account.journal'].create({
        'name': "acc journal 12",
        'type': 'sale',
        'code': "abc12",
        'default_account_id': account_account_act.id,
    })


@pytest.fixture
def account_journal_act2(env, account_account_act):
    return env['account.journal'].create({
        'name': "acc journal 321",
        'type': 'purchase',
        'code': "abc1898",
        'default_account_id': account_account_act.id,
    })


@pytest.fixture
def company2(env, account_account2):
    return env["res.company"].create({
        "name": "company 2",
    })


@pytest.fixture
def product_inv(env, company2):
    return env['product.product'].create({
        'name': 'WEWE',
        'type': 'service',
        'company_id': company2.id,
    })


@pytest.fixture
def account_account_type2(env):
    return env['account.account.type'].create({
        'name': 'credit2',
        'type': 'other',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account2(env, account_account_type2):
    return env['account.account'].create({
        'name': 'acc2 acc2',
        'user_type_id': account_account_type2.id,
        'code': '02',
    })


@pytest.fixture
def account_journal2(env, account_account_type, company2):
    return env['account.journal'].create({
        'name': 'test_out_invoice_multi_company',
        'code': 'XXXXX',
        'type': 'sale',
        'company_id': company2.id,

    })


@pytest.fixture
def currency2(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.fixture
def payment_term2(env, company2):
    return env['account.payment.term'].create({
        'name': 'the 15th of the month, min 31 days from now',
        'company_id': company2.id,
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
def account_receivable2(env, account_type, company2):
    return env['account.account'].create({
        'code': '1000',
        'company_id': company2.id,
        'name': 'Test Receivable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_payable2(env, account_type, company2):
    return env['account.account'].create({
        'code': '2000',
        'company_id': company2.id,
        'name': 'Test Payable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def invoice2(
        model,
        product,
        partner2,
        account_id):
    return model.create({
        "partner_id": partner2.id,
        "move_type": "in_invoice",
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


@pytest.fixture
def partner2(env, payment_term, account_receivable, account_payable):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def invoice(
        model,
        product,
        partner,
        account_id):
    return model.create({
        "partner_id": partner.id,
        "move_type": "out_invoice",
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


@pytest.mark.parametrize('test_input', [
    ({'move_type': 'out_invoice',
      'journal_type': 'sale'}),
    ({'move_type': 'in_invoice',
      'journal_type': 'purchase'}),
    ({'move_type': 'entry',
      'journal_type': 'purchase'})
])
def test_action_register_payment(
        invoice,
        invoice2,
        monkeypatch,
        mocker,
        env,
        test_input
):
    if test_input.get('journal_type') == 'sale':
        inv = invoice
    else:
        inv = invoice2
    inv.state = 'posted'
    inv.move_type = test_input.get('move_type')
    inv.journal_id.type = test_input.get('journal_type')
    spy_check_inv = mocker.spy(type(inv), 'check_inv_register_payment')
    spy_prepare_account = mocker.spy(
        type(inv), 'prepare_account_payment_line')
    line_invoice = []
    val = (0, 0, {
        'invoice_id': inv.id,
        'amount_wht': inv.amount_wht,
        'amount_tobe_paid': inv.amount_residual,
    })
    line_invoice.append(val)
    spy__create_account = mocker.spy(type(inv), '_create_account_payment')
    inv.write({
        'payment_state': 'not_paid',
    })

    inv.action_register_payment()
    spy_check_inv.assert_called_once_with(inv)
    spy_prepare_account.assert_called_once_with(inv)
    spy__create_account.assert_called_once_with(
        inv, line_invoice, env['account.billing.note'])


@pytest.mark.parametrize('test_input,expected', [
    ({'partner': True},
     ("You can only register payment for the same partner")),
    ({'company_id': True},
     "You can't create payments for entries belonging to different companies."),
    ({'internal_type': True},
     "You can't register payments for journal items being either all inbound, either all outbound."),
    ({'state': True},
     ("You can only register payment for posted journal"
      " entries.")),
    ({'invoice_line_ids': True},
     ("You can't register a payment because there is nothing"
      " left to pay on the selected journal items.")),
])
def test_check_inv_register_payment(
        env,
        account_account2,
        invoice,
        invoice2,
        test_input,
        account_move2,
        partner,
        expected):
    invoice.state = 'posted'
    account_move2.state = 'posted'
    if test_input.get('partner'):
        invoice += invoice2
        with pytest.raises(ValidationError) as excinfo:
            invoice.check_inv_register_payment()
        assert str(excinfo.value) == expected
    if test_input.get('company_id'):
        invoice += account_move2
        with pytest.raises(ValidationError) as excinfo:
            invoice.check_inv_register_payment()
        assert str(excinfo.value) == expected
    if test_input.get('internal_type'):
        invoice3 = invoice2.copy()
        invoice3.state = 'posted'
        invoice3.invoice_line_ids.account_id = account_account2.id
        invoice2 += invoice3
        with pytest.raises(ValidationError) as excinfo:
            invoice2.check_inv_register_payment()
        assert str(excinfo.value) == expected
    if test_input.get('state'):
        invoice2.state = "draft"
        with pytest.raises(ValidationError) as excinfo:
            invoice2.check_inv_register_payment()
        assert str(excinfo.value) == expected
    if test_input.get('invoice_line_ids'):
        with pytest.raises(ValidationError) as excinfo:
            account_move2.check_inv_register_payment()
        assert str(excinfo.value) == expected


@pytest.fixture
def account_move2(
        env,
        partner,
        product_inv,
        company2,
        account_journal2,
        currency2):
    partner.company_id = company2.id
    return env['account.move'].create({
        'partner_id': partner.id,
        'company_id': company2.id,
        'journal_id': account_journal2.id,
        'invoice_date_due': fields.Date.today(),
        'currency_id': currency2.id,
        'move_type': 'out_invoice',
    })


def test_prepare_account_payment_line(env, invoice):
    line_invoice = invoice.prepare_account_payment_line()
    assert line_invoice[0][2]['invoice_id'] == invoice.id


@pytest.fixture
def payment_term_30days(env):
    payment_term = env.ref('account.account_payment_term_30days')
    return payment_term


@pytest.fixture
def journal_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


def test__create_account_payment(
        env,
        invoice,
        monkeypatch,
        mocker,
        wht3,
        partner,
        product,
        payment_term_30days):
    beecy_payment = env['beecy.account.payment']
    invoice.invoice_line_ids.wht_type_id = wht3.id
    line_invoice = invoice.prepare_account_payment_line()
    spy_beecy_payment = mocker.spy(
        type(beecy_payment),
        '_onchange_payment_line_invoice_ids')

    acc_m = env['account.move'].create({
        'partner_id': partner.id,
        'invoice_payment_term_id': payment_term_30days.id,
    })
    acc_m.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'account_id': env.user.property_account_receivable_id.id
        })],
    })
    acc_m.state = 'posted'

    billing_note = env['account.billing.note'].create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today(),
        'line_ids': [(0, 0,
                      {
                          'invoice_id': acc_m.id
                      }),
                     ]
    })

    res = invoice._create_account_payment(line_invoice, billing_note)
    beecy_payment_res = beecy_payment.search([
        ('payment_line_invoice_ids.invoice_id', '=', invoice.id)
    ])
    spy_beecy_payment.assert_called_once_with(res)
    assert res == beecy_payment_res


def test__compute_beecy_payment_count(env,
                                      invoice2,
                                      partner,
                                      journal_cash):
    acc_p = env['beecy.account.payment'].create({
        'payment_type': 'outbound',
        'partner_id': partner.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': invoice2.id,
        })]
    })
    invoice2.write({'beecy_payment_id': acc_p.id})
    invoice2._compute_beecy_payment_count()
    assert invoice2.beecy_payment_count == 1


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'in_invoice', 'payment_type': 'outbound'}, True),
    ({'move_type': 'out_invoice', 'payment_type': 'inbound'}, True),
    ({'move_type': 'out_refund', 'payment_type': 'inbound'}, True),
    ({'move_type': 'out_receipt', 'payment_type': 'inbound'}, False),
])
def test_action_payment_view(env,
                             partner,
                             partner2,
                             product,
                             journal_cash,
                             account_id,
                             test_input,
                             expected):
    invoice = env['account.move'].create({
        "partner_id": partner2.id,
        "move_type": test_input.get('move_type'),
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })
    acc_p = env['beecy.account.payment'].create({
        'payment_type': test_input.get('payment_type'),
        'partner_id': partner.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': invoice.id,
        })]
    })
    invoice.write({'beecy_payment_id': acc_p.id})
    res = invoice.action_payment_view()
    if expected:
        assert res['domain'] == [('id', 'in', acc_p.ids)]
    else:
        assert res == expected
