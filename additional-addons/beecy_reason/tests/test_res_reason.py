import pytest
from pytest_tr_odoo.fixtures import env
from .fixtures import *


@pytest.fixture
def model(env):
    return env['res.reason']


@pytest.mark.parametrize('test_input', [
    {'move_type': 'out_invoice'},
    {'move_type': False},
])
def test_get_domain_reason(model, ir_model_users, test_input):
    res = model._get_domain_reason(
        ir_model_users.model, test_input.get('move_type')
    )
    if test_input.get('move_type'):
        domain = [
            '|', '&',
            ('model_ids', '=', ir_model_users.id),
            ('account_type', '=', test_input.get('move_type')),
            ('model_ids', '=', False),
        ]
    else:
        domain = [
            '|',
            ('model_ids', '=', ir_model_users.id),
            ('model_ids', '=', False),
        ]
    assert res == domain


@pytest.mark.parametrize('test_input', [
    'out_invoice',
    'out_refund',
    'in_invoice',
    'in_refund',
])
def test_update_model_in_reason(env, reason, ir_model_users, test_input):
    ir_model_company = env['ir.model'].search([
        ('model', '=', 'res.company')
    ])
    reason.update_model_in_reason(
        ir_model_company.id, test_input
    )
    assert reason.model_ids.ids == [ir_model_users.id, ir_model_company.id]
    assert reason.account_type == test_input
