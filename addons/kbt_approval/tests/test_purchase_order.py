from pytest_tr_odoo.fixtures import env
import pytest
from odoo import Command
from odoo.exceptions import ValidationError


@pytest.fixture
def purchase(env):
    return env.ref('purchase.purchase_order_1')


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
    }, 'purchase'),
])
def test_button_confirm_purchase_order(purchase, env, test_input, expected):
    po_model = env['ir.model'].search([('model', '=', 'purchase.order')])
    level = env['org.level'].search([])
    employee = env.ref('hr.employee_qdp')
    employee_manager = env.ref('hr.employee_stw')
    employee_manager.write({
        'is_send_email': True
    })
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
                    'model_id': po_model.id
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
            purchase.button_confirm()
            msg = (
                "You cannot validate this document due limitation policy. Please contact (Randall Lewis)"
                " ไม่สามารถดำเนินการได้เนื่องจากเกินวงเงินที่กำหนด กรุณาติดต่อ (Randall Lewis)")
            assert purchase.state == expected
            assert purchase.is_approve == False
            assert excinfo.value.name == msg
    else:
        purchase.button_confirm()
        assert purchase.state == expected
        assert purchase.is_approve


def test_button_confirm_interface_purchase_order(purchase):
    purchase.write({
        'x_is_interface': True
    })
    purchase.button_confirm()
    assert purchase.state == 'purchase'


def test_cancel_purchase_order(purchase):
    res = purchase.action_cancel_reject_reason_wizard()
    assert res['res_model'] == 'cancel.reject.reason'
