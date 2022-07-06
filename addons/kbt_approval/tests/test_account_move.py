from pytest_tr_odoo.fixtures import env
import pytest
from odoo import fields, Command
from odoo.exceptions import ValidationError


@pytest.fixture
def model(env):
    return env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': env.ref('base.res_partner_2').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref('account.account_payment_term_immediate').id,
        'invoice_date': fields.Date.today(),
        'invoice_line_ids': [
            Command.create({'product_id': env.ref('product.consu_delivery_02').id, 'quantity': 5}),
            Command.create({'product_id': env.ref('product.consu_delivery_03').id, 'quantity': 5}),
        ],
    })


@pytest.fixture
def model_org_level(env, model):
    account_move_id = env['ir.model'].search(
        [('model', '=', 'account.move')]).id
    model_org_level = env['org.level'].create({
        'level': 123456789,
        'description': "test",
        'line_ids': [
            Command.create({
                'limit': 50,
                'model_id': account_move_id,
                'move_type': 'out_invoice',
                'org_level_id': model.id
            }),
        ]
    })

    employee = env.ref('hr.employee_chs')
    model.partner_id.write({
        'employee_ids': [employee.id]
    })

    employee.write({
        'level_id': model_org_level.id
    })

    return model_org_level


def test_is_approve_send_account_move(model):
    model.is_approve_send = False
    assert model.is_approve_send == False


def test_action_post_false_account_move(model, model_org_level):
    model_org_level.line_ids.write({
        'limit': -1
    })
    with pytest.raises(ValidationError):
        model.action_post()


def test_action_post_true_account_move(model, model_org_level):
    model_org_level.line_ids.write({
        'limit': 50000000
    })
    model.action_post()
    assert model.state == 'posted'


def test_cancel_account_move(model):
    res = model.action_cancel_reject_reason_wizard()
    assert res['res_model'] == 'cancel.reject.reason'
