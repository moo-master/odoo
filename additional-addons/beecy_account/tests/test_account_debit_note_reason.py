import pytest
from pytest_tr_odoo.fixtures import env


def test_domain_reason_id(env):
    wizard = env['account.debit.note.reason'].with_context(
        {'move_type': 'out_debit',
         'model_name': 'account.move', }
    ).create({})
    domain = wizard._domain_reason_id()
    assert domain


@pytest.mark.parametrize('test_input', [
    ({'type': 'out_invoice', 'type_debit': 'out_debit'}),
    ({'type': 'in_invoice', 'type_debit': 'in_debit'})
])
def test_action_debit_note_moves(env, test_input, mocker, monkeypatch):
    acc_move = env['account.move'].with_context({
        'default_move_type': test_input['type']
    }).create({})
    ir_model = env['ir.model'].search([
        ('model', '=', 'account.move')
    ])
    reason = env['res.reason'].create({
        'name': 'test',
        'model_ids': [(6, 0, ir_model.ids)],
        'account_type': test_input['type']
    })
    wizard = env['account.debit.note.reason'].with_context({
        'move_type': test_input.get('type'),
        'model_name': 'account.move',
        'default_move_type': test_input.get('type'),
        'active_id': acc_move.id,
    }).create({
        'reason_id': reason.id
    })
    res = wizard.action_debit_note_moves()
    dn = env['account.move'].search([
        ('invoice_ref_id', '=', acc_move.name),
    ])
    view = env.ref('beecy_account.view_move_form_inherit_beecy_accont')

    expected = {
        'name': 'Debit Note',
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_model': 'account.move',
        'res_id': dn.id,
        'domain': [('move_type', '=', test_input['type_debit'])],
        'view_id': view.id,
        'context': {
            'move_type': test_input.get('type'),
            'model_name': 'account.move',
            'default_move_type': test_input.get('type_debit'),
            'active_id': acc_move.id}}
    assert dn
    assert res == expected
