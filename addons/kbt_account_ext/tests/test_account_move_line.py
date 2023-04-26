from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move.line']


@pytest.fixture
def account_account_type(env):
    return env['account.account.type'].create({
        'name': 'credit2',
        'type': 'other',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account(env, account_account_type):
    return env['account.account'].create({
        'name': 'Account Test 00',
        'user_type_id': account_account_type.id,
        'code': '0000000',
        'internal_type': 'liquidity',
        'reconcile': True,
    })


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'TestTH',
        'rate': 1.000000,
        'currency_unit_label': 'TestTH',
        'currency_subunit_label': 'TestTHx',
        'symbol': 'x฿'
    })


@pytest.mark.parametrize('test_input', [
    ({'currency_id': True}),
    ({'currency_id': False})
])
def test__compute_amount_residual(
        env,
        model,
        account_account,
        currency,
        test_input):
    rec = model.new({
        'account_id': account_account.id,
        'product_id': env.ref('product.product_product_1').id,
        'quantity': 1,
        'currency_id': currency.id if test_input.get('currency_id') else False,
        'company_currency_id': currency.id,
        'amount_currency': 1000
    })
    rec._compute_amount_residual()

    if test_input.get('currency_id'):
        assert rec.amount_residual_currency
    else:
        assert not rec.amount_residual_currency
