from pytest_tr_odoo.fixtures import env
import pytest
from odoo import fields, Command
from odoo.exceptions import ValidationError


@pytest.fixture
def move(env):
    return env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': env.ref('base.res_partner_2').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref('account.account_payment_term_immediate').id,
        'invoice_date': fields.Date.today(),
        'invoice_line_ids': [
            Command.create({'product_id': env.ref('product.consu_delivery_02').id, 'price_unit': 100, 'quantity': 5}),
            Command.create({'product_id': env.ref('product.consu_delivery_03').id, 'price_unit': 100, 'quantity': 5}),
        ],
    })


@pytest.mark.parametrize('test_input,expected', [
    ({
        'level': 0,
        'description': 'Operation',
        'limit': 50
    }, 'to approve'),
    ({
        'level': 1,
        'description': 'Manager',
        'limit': 5000000
    }, 'posted'),
])
def test_action_post_move(move, env, test_input, expected):
    mv_model = env['ir.model'].search([('model', '=', 'account.move')])
    level = env['org.level'].search([])
    employee = env.ref('hr.employee_qdp')
    employee_manager = env.ref('hr.employee_stw')
    employee.write({
        'level_id': False
    })
    for l in level:
        l.unlink()
    model_org_level = env['org.level'].create(
        {
            'level': test_input['level'],
            'description': test_input['description'],
            'line_ids': [
                Command.create({
                    'limit': test_input['limit'],
                    'model_id': mv_model.id
                }),
            ]
        }
    )
    employee.write({
        'level_id': model_org_level.id,
        'user_id': env.uid,
        'parent_id': employee_manager.id
    })
    if test_input['level'] == 0:
        with pytest.raises(ValidationError) as excinfo:
            move.action_post()
            msg = (
                "You cannot validate this document due limitation policy. Please contact (Randall Lewis)"
                " ไม่สามารถดำเนินการได้เนื่องจากเกินวงเงินที่กำหนด กรุณาติดต่อ (Randall Lewis)")
            assert move.state == expected
            assert move.is_approve == False
            assert excinfo.value.name == msg
            assert move.show_reset_to_draft_button
    else:
        move.action_post()
        assert move.state == expected
        assert move.is_approve
        assert move.show_reset_to_draft_button


def test_action_post_interface_move(move):
    move.write({
        'x_is_interface': True
    })
    move.action_post()
    assert move.state == 'posted'


def test_cancel_account_move(move):
    res = move.action_cancel_reject_reason_wizard()
    assert res['res_model'] == 'cancel.reject.reason'
