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
            Command.create({'product_id': env.ref(
                'product.consu_delivery_02').id, 'price_unit': 100, 'quantity': 5}),
            Command.create({'product_id': env.ref(
                'product.consu_delivery_03').id, 'price_unit': 100, 'quantity': 5}),
        ],
        'approval_ids': False,
    })


@pytest.fixture
def mv_model(env):
    return env['ir.model'].search([('model', '=', 'account.move')])


@pytest.fixture
def employee(env):
    return env.ref('hr.employee_qdp')


@pytest.fixture
def employee_manager(env):
    return env.ref('hr.employee_stw')


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
def test_action_post_move(
        move,
        env,
        test_input,
        expected,
        mv_model,
        employee,
        employee_manager):
    level = env['org.level'].search([])
    employee_manager.write({'is_send_email': True})
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
                "Please contact (Randall Lewis) for approving this document"
                " โปรดติดต่อ (Randall Lewis) สำหรับการอนุมัติเอกสาร")
            # assert move.state == expected
            # assert move.is_approve == False
            # assert excinfo.value.name == msg
            # assert move.show_reset_to_draft_button
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


@pytest.mark.parametrize('test_input,expected', [
    ({'amount': 50, 'is_level': True}, False),
    ({'amount': 5000000, 'is_level': True}, True),
    ({'amount': 5000000, 'is_level': False}, False),  # Test user with no Level
])
def test__compute_is_over_limit(env, mv_model, employee, test_input, expected):
    model_org_level = env['org.level'].create({
        'level': 100,
        'description': 'TEST',
        'line_ids': [
            Command.create({
                'limit': 10000,
                'model_id': mv_model.id
            }),
        ]
    })
    employee.write({'level_id': model_org_level.id if test_input.get(
        'is_level') else False, 'user_id': env.uid, })
    rec = env['account.move'].new({'amount_total': test_input['amount']})
    rec._compute_is_over_limit()
    assert rec.is_over_limit == expected


def test__user_validation(env):
    ''
    move = env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': env.ref('base.res_partner_2').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref('account.account_payment_term_immediate').id,
        'invoice_date': fields.Date.today(),
        'invoice_line_ids': [
            Command.create({'product_id': env.ref(
                'product.consu_delivery_02').id, 'price_unit': 100, 'quantity': 5}),
            Command.create({'product_id': env.ref(
                'product.consu_delivery_03').id, 'price_unit': 100, 'quantity': 5}),
        ],
        'approval_ids': False,
    })
    move._user_validation()
