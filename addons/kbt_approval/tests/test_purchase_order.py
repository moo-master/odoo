from pytest_tr_odoo.fixtures import env
import pytest
from odoo import Command
from odoo.exceptions import ValidationError


@pytest.fixture
def purchase(env):
    return env.ref('purchase.purchase_order_1')


@pytest.fixture
def po_model(env):
    return env['ir.model'].search([('model', '=', 'purchase.order')])


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
    }, 'purchase'),
])
def test_button_confirm_purchase_order(
        purchase,
        env,
        test_input,
        expected,
        po_model,
        employee,
        employee_manager):
    purchase.write({'approval_ids': False})
    level = env['org.level'].search([])
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
            assert purchase.approval_ids
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


@pytest.mark.parametrize('test_input,expected', [
    ({'amount': 50, 'is_level': True}, False),
    ({'amount': 5000000, 'is_level': True}, True),
    ({'amount': 5000000, 'is_level': False}, False),  # Test user with no Level
])
def test__compute_is_over_limit(env, po_model, employee, test_input, expected):
    model_org_level = env['org.level'].create({
        'level': 100,
        'description': 'TEST',
        'line_ids': [
            Command.create({
                'limit': 10000,
                'model_id': po_model.id
            }),
        ]
    })
    employee.write({
        'level_id': model_org_level.id if test_input.get('is_level')
        else False,
        'user_id': env.uid,
    })
    rec = env['purchase.order'].new({'amount_total': test_input['amount']})
    rec._compute_is_over_limit()
    assert rec.is_over_limit == expected
