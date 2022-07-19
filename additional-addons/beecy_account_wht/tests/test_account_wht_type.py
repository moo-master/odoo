import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['account.wht.type']


@pytest.fixture
def acc_wht(model):
    return model.create({
        'display_name': 'test WHT',
        'percent': 0.7,
        'sequence': 5,
    })


@pytest.mark.parametrize('test_input,expected', [
    (True, True),
    (False, False),
])
def test__onchange_parent(env, test_input, expected):
    wht = env['account.wht.type'].new({})
    if test_input:
        acc_wht = env['account.wht.type'].create({
            'display_name': 'test WHT',
        })
        wht.parent_id = acc_wht.id
        wht._onchange_parent()
    else:
        wht._onchange_parent()
    assert wht.is_parent == expected


def test_wht_calculator(acc_wht, monkeypatch):
    res = acc_wht.wht_calculator(50)
    assert res == 0.35


def test_compute_display_name(model):
    wht_type = model.new({
        'percent': 15
    })
    wht_type.update({
        'name': "test create wht type"
    })
    wht_type._compute_display_name()
    assert wht_type.display_name == f'({wht_type.percent}%) {wht_type.name}'
