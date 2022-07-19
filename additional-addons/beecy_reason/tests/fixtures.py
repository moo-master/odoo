import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def ir_model_users(env):
    return env['ir.model'].search([
        ('model', '=', 'res.users')
    ])


@pytest.fixture
def reason(env, ir_model_users):
    return env['res.reason'].create({
        'name': 'Reason',
        'model_ids': ir_model_users.ids,
        'account_type': 'out_invoice',
    })
