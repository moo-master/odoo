from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move']


def test_get_amount_total_text(model):
    move_id = model.new({
        'amount_total': 1234.50,
    })
    res = move_id.get_amount_total_text(move_id.amount_total)
    assert res == 'หนึ่งพันสองร้อยสามสิบสี่บาทห้าสิบสตางค์'
