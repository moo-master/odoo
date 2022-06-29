from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move.line']


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.fixture
def account_type(env):
    return env['account.account.type'].create({
        'name': 'Test Type',
        'type': 'other',
        'internal_group': 'income',
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
        'property_account_payable_id': account_payable.id,
        'x_offset': True,
    })


@pytest.mark.parametrize('test_input', [
    ({'type': 'out_invoice', 'type_debit': 'out_debit'}),
    ({'type': 'in_invoice', 'type_debit': 'in_debit'})
])
def test_create_model_with_x_offset(model, env, test_input, currency, partner):
    acc_move = env['account.move'].with_context({
        'default_move_type': test_input['type']
    }).create({'partner_id': partner.id})
    vals = {'move_id': acc_move.id,
            'currency_id': currency.id,
            'product_id': env.ref('product.product_product_2').id,
            'price_unit': 642.0,
            'quantity': 1}
    res = model.new(vals)
    assert res.x_offset == res.move_id.partner_id.x_offset
