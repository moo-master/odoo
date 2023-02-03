from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.mark.parametrize('test_input', [
    ({'is_wht_line': True}),
    ({'is_wht_line': False})
])
def test__compute_is_wht_exist(env, model, test_input):
    line_1 = env['account.move.line'].new({
        'is_wht_line': test_input['is_wht_line']
    })
    line_2 = env['account.move.line'].new({
        'is_wht_line': False
    })
    move = model.new({
        'line_ids': [(6, 0, [line_1.id, line_2.id])]
    })
    move._compute_is_wht_exist()
    assert move.is_wht_exist == test_input['is_wht_line']
