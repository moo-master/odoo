from pytest_tr_odoo.fixtures import env
import pytest
from odoo import Command
from odoo.exceptions import ValidationError


@pytest.fixture
def model(env):
    return env.ref('purchase.purchase_order_1')


@pytest.fixture
def model_org_level(env, model):
    model_id = env['ir.model'].search([('model', '=', 'purchase.order')]).id
    model_org_level = env['org.level'].create({
        'level': 123456789,
        'description': "test",
        'line_ids': [
            Command.create({
                'limit': 50,
                'model_id': model_id,
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


def test_is_approve_send_purchase_order(model):
    model.is_approve_send = False
    assert model.is_approve_send == False


def test_button_confirm_false_purchase_order(model, model_org_level):
    model_org_level.line_ids.write({
        'limit': -1
    })
    with pytest.raises(ValidationError):
        model.button_confirm()


def test_button_confirm_true_purchase_order(model, model_org_level):
    model_org_level.line_ids.write({
        'limit': 50000000
    })
    model.button_confirm()
    assert model.state == 'purchase'


def test_cancel_purchase_order(model):
    res = model.action_cancel_reject_reason_wizard()
    assert res['res_model'] == 'cancel.reject.reason'
