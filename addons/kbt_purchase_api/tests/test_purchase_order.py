from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['purchase.order']


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
        'supplier_rank': 5,
        'company_id': 1,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def model_sequence(env):
    return env['ir.sequence'].create({
        'name': 'Account reconcile sequence',
        'implementation': 'standard',
        'padding': 0,
        'number_increment': 1,
    })


@pytest.fixture
def business_type(env, account_payable, model_sequence):
    return env['business.type'].create({
        'x_name': 'Test Business',
        'x_type': 'purchase',
        'x_code': 1,
        'x_sequence_id': model_sequence.id,
        'x_revenue_account_id': account_payable.id,
        'default_gl_account_id': account_payable.id,
    })


def test_create(model, env, partner, business_type):
    vals = {'partner_id': partner.id,
            'po_type_id': business_type.id,
            'x_is_interface': False,
            'order_line': [(0, 0, {
                'name': 'string',
                'display_type': 'line_note',
                'product_qty': 0,
                'note': 'abc'
            })],
            }
    res = model.create(vals)
    assert res.order_line.note
