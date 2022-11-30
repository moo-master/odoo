from pytest_tr_odoo.fixtures import env
import pytest
from odoo import Command
from odoo.exceptions import ValidationError


@pytest.fixture
def sale(env):
    return env.ref('sale.sale_order_1')


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
    }, 'sale'),
])
def test_action_confirm_false_sale_order(sale, env, test_input, expected):
    so_model = env['ir.model'].search([('model', '=', 'sale.order')])
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
                    'model_id': so_model.id
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
            sale.action_confirm()
            msg = (
                "You cannot validate this document due limitation policy. Please contact (Randall Lewis)"
                " ไม่สามารถดำเนินการได้เนื่องจากเกินวงเงินที่กำหนด กรุณาติดต่อ (Randall Lewis)")
            assert sale.state == expected
            assert sale.is_approve == False
            assert excinfo.value.name == msg
    else:
        sale.action_confirm()
        assert sale.state == expected
        assert sale.is_approve


def test_cancel_sale_order(sale):
    res = sale.action_cancel_reject_reason_wizard()
    assert res['res_model'] == 'cancel.reject.reason'


def test_action_confirm_interface_sale_order(sale):
    sale.write({
        'x_is_interface': True
    })
    sale.action_confirm()
    assert sale.state == 'sale'
