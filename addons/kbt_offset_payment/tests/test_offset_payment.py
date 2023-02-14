from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['offset.payment']


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'out_invoice', }, 'in_invoice'),
    ({'move_type': 'in_invoice', }, 'out_invoice'),
])
def test__compute_move_type(env, model, test_input, expected):
    move = env['account.move'].new({
        'move_type': test_input['move_type']
    })
    offset = model.new({
        'move_id': move.id
    })
    offset._compute_move_type()
    assert offset.offset_move_type == expected
