import pytest
from pytest_tr_odoo.fixtures import env


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


def test_create(env, account_account):
    payment_method = env.ref('account.account_payment_method_manual_in')
    acc_payment = env['account.payment.method.line'].create({
        'payment_method_id': payment_method.id,
        'payment_account_id': account_account.id,
    })
    assert acc_payment
