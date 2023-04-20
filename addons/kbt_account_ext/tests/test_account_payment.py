from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.payment']


def test__amount_total_text(model):
    payment = model.new({
        'amount': 1234.50,
    })
    res = payment._amount_total_text(payment.amount)
    assert res == 'หนึ่งพันสองร้อยสามสิบสี่บาทห้าสิบสตางค์'
