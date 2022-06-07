from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['sale.order']


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
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def model_seq(env):
    return env['ir.sequence'].create({
        'name': 'Account reconcile sequence',
        'implementation': 'standard',
        'padding': 0,
        'number_increment': 1,
    })


@pytest.fixture
def business_type(env, account_payable, model_seq):
    return env['business.type'].create({
        'x_name': 'Your Supplier',
        'x_type': 'sale',
        'x_code': 10,
        'x_sequence_id': model_seq.id,
        'x_revenue_account_id': account_payable.id
    })


@pytest.fixture
def company(env):
    return env["res.company"].create({
        "name": "company",
    })


@pytest.fixture
def product(env):
    return env['product.product'].create({
        'name': 'Mini Fan'
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'x_is': True}, 'account_id'),
    ({'x_is': False}, 'account_id'),
])
def test__prepare_invoice_line(model,
                               env,
                               partner,
                               business_type,
                               company,
                               product,
                               test_input,
                               expected):
    so_vals = model.create({'partner_id': partner.id,
                            'so_type_id': business_type.id,
                            'x_is_interface': test_input['x_is'],
                            'company_id': company.id,
                            'order_line': [(0, 0, {
                                'product_id': product.id,
                                'product_uom_qty': 1,
                                'price_unit': 100,
                                'sequence': 1
                            })]
                            })
    inv_line = so_vals.order_line._prepare_invoice_line()
    if so_vals.x_is_interface:
        assert inv_line['account_id'] == business_type.x_revenue_account_id
    else:
        assert expected not in inv_line
