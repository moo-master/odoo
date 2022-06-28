from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move.line']


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.mark.parametrize('test_input', [
    ({'type': 'out_invoice', 'type_debit': 'out_debit'}),
    ({'type': 'in_invoice', 'type_debit': 'in_debit'})
])
def test_x_offset(model, env, test_input, currency):
    acc_move = env['account.move'].with_context({
        'default_move_type': test_input['type']
    }).create({})
    vals = {'move_id': acc_move.id,
            'currency_id': currency.id,
            'x_offset': True}
    res = model.create(vals)
    assert res.x_offset
