import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['base.document.layout']


@pytest.mark.parametrize('test_input,expected', [(
    {'amount': 200},
    'สองร้อยบาทถ้วน'),
    ({'amount': 300},
     'สามร้อยบาทถ้วน'),
])
def test_amount_total_text(env, test_input, expected):
    so = env['sale.order'].new()
    so.amount_total = test_input['amount']
    text_th = so._amount_total_text(so.amount_total)
    assert text_th == expected
