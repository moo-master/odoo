import pytest
from pytest_tr_odoo.fixtures import env
from .fixtures import *


@pytest.mark.parametrize('test_input,expected',
                         [({'choose': True},
                           {'count': 1,
                             'paid_amount': 500}),
                             ({'choose': True,
                               'move_type': 'out_refund'},
                              {'count': 1,
                               'paid_amount': -500}),
                          ])
def test_action_confirm_invoice(
        env,
        account_move,
        billing_note_wizard,
        test_input,
        expected):
    billing = billing_note_wizard
    if test_input.get('move_type'):
        account_move.move_type = test_input.get('move_type')
    wizard = env['account.invoice.wizard'].create({
        'invoice_id': account_move.id,
        'paid_amount': account_move.amount_residual,
        'billing_note_id': billing.id,
    })
    wizard.action_confirm_invoice()
    assert len(billing.line_ids.invoice_id) == expected['count']
    assert billing.line_ids.paid_amount == expected['paid_amount']
