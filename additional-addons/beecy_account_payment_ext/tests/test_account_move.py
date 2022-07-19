import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


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


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale',
        'currency_id': env.company.currency_id.id,
    })


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def payment_term_30days(env):
    payment_term = env.ref('account.account_payment_term_30days')
    return payment_term


@pytest.fixture
def invoice(
        model,
        product,
        partner,
        journal,
        account_id):
    return model.create({
        "partner_id": partner.id,
        "move_type": "out_invoice",
        "journal_id": journal.id,
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


def test_action_register_payment(
        invoice,
        mocker,
        env,
        wht3,
        partner,
        payment_term_30days,
        product
):
    invoice.invoice_line_ids.wht_type_id = wht3.id
    line_invoice = invoice.prepare_account_payment_line()
    invoice.state = 'posted'
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
    beecy_acc_payment = env['beecy.account.payment']
    spy__onchange_create_temp_journal_item = mocker.spy(
        type(beecy_acc_payment), '_onchange_create_temp_journal_item')
    invoice._create_account_payment(line_invoice, billing_note)
    assert spy__onchange_create_temp_journal_item.called
