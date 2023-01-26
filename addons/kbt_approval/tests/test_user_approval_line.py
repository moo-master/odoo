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
        ],
        'approval_ids': [(0, 0, {'manager_id': env.ref('hr.employee_admin').id})]
    })


def test_confirm_approval_line(env, move):
    employee = env.ref('hr.employee_admin')
    move.approval_ids.confirm_approval_line(employee)
    assert move.approval_ids.is_approve
