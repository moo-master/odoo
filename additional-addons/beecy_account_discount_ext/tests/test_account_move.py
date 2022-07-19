import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale'
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
def account_other_income_income(env):
    account_type = env.ref('account.data_account_type_other_income')
    return env['account.account'].create({
        'code': '4002',
        'name': 'Test Account Income',
        'user_type_id': account_type.id,
        'reconcile': True
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
        'company_id': env.company.id,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def product(env):
    return env['product.product'].create({
        'name': 'Mini Fan',
    })


@pytest.fixture
def tax_input(env):
    return env['account.tax'].create({
        'name': 'Input VAT 7%',
        'amount_type': 'percent',
        'type_tax_use': 'purchase',
        'amount': 7
    })


@pytest.fixture
def tax_output(env):
    return env['account.tax'].create({
        'name': 'Output VAT 7%',
        'amount_type': 'percent',
        'type_tax_use': 'sale',
        'amount': 7
    })


@pytest.fixture
def product1(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


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
def invoice(env, model, product1,
            partner_demo,
            account_other_income_income, tax_output):
    return env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 10,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'formula_discount': 10,
            'direct_discount': 10,
        })],
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'price_unit': 100, 'formula': '10'}, 90),
    ({'price_unit': 100, 'formula': '5'}, 95),
])
def test__get_price_discount_model(env,
                                   model,
                                   mocker,
                                   test_input,
                                   expected):

    spy_fator = mocker.spy(
        type(model),
        '_get_ordered_factor',
    )
    value = model._get_price_discount_model(
        price_unit=test_input['price_unit'], formula=test_input['formula'])
    assert spy_fator.called
    assert value == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'price_unit': 100, 'formula': '10'}, 111.11111111111111),
    # ({'price_unit': 100, 'formula': '5'}, 105.26315789473685),
])
def test_get_price_wo_discount_model(env,
                                     model,
                                     mocker,
                                     test_input,
                                     expected):

    spy_fator = mocker.spy(
        type(model),
        '_get_ordered_factor',
    )
    value = model._get_price_wo_discount_model(
        price_unit=test_input['price_unit'], formula=test_input['formula'])
    assert spy_fator.called
    assert value == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'formula': '10'}, [0.9]),
    ({'formula': '90'}, [0.09999999999999998]),
    ({'formula': 'None'}, []),
])
def test__get_ordered_factor(env, model, test_input, expected):
    formula = model._get_ordered_factor(test_input['formula'])
    assert formula == expected
