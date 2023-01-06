from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move']


def test_action_register_payment(env, model):
    move = model.new({
        'amount_residual': 300,
        'amount_wht': 100,
    })
    res = move.action_register_payment()
    assert res['context']['default_wht_amount'] == move.amount_wht
    assert res['context']['default_paid_amount'] == \
        move.amount_residual - move.amount_wht
