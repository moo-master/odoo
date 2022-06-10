import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.move.reversal']


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale'
    })


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
def invoice(env,
            product,
            partner,
            journal,
            account_id):
    return env['account.move'].create({
        "partner_id": partner.id,
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


def test__domain_reason_id(env, model, invoice):
    res = model.with_context(
        move_type='out_invoice',
        model_name='account.move')._domain_reason_id()
    ir_model = env['ir.model'].search([
        ('model', '=', 'account.move')
    ])
    expected = ['|', '&',
                ('model_ids', '=', ir_model.id),
                ('account_type', '=', 'out_invoice'),
                ('model_ids', '=', False)
                ]
    assert res == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'out_invoice'}, 'out_refund'),
    ({'move_type': 'in_invoice'}, 'in_refund'),
])
def test_reverse_moves(model, journal, invoice, test_input, expected):
    if test_input['move_type'] == 'in_invoice':
        journal.type = 'purchase'
    wizard = model.with_context(default_move_type=test_input['move_type']).create({
        'move_ids': [(4, invoice.id)],
        'journal_id': journal.id,
        'accounting_date': '2022-02-25',
        'vendor_ref': 'xx1',
    })
    wizard.reverse_moves()
    assert wizard.new_move_ids.move_type == expected
    assert wizard.new_move_ids.date.strftime("%Y-%m-%d") == '2022-02-25'
    assert wizard.new_move_ids.ref == 'xx1'


@pytest.fixture
def res_reason_onch_reason(env):
    return env['res.reason'].create({
        'name': 'reason created',
        'is_description': True,
    })


def test_onchange_reason_id(env, res_reason_onch_reason):
    wizard = env['account.move.reversal'].new({
        'reason_id': res_reason_onch_reason.id,
        'reason_description': 'test description'
    })
    wizard.reason_id = False
    wizard._onchange_reason_id()
    assert not wizard.reason_description
