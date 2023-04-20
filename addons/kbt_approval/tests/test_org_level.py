from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    level = env['org.level'].search([])
    employee = env.ref('hr.employee_qdp')
    employee.write({
        'level_id': False
    })
    for l in level:
        l.unlink()
    return env['org.level'].create({
        'level': 0,
        'description': "Operation",
    })


@pytest.fixture
def model_line(env):
    return env['org.level.line']


@pytest.fixture
def employee_admin(env):
    return env.ref('hr.employee_admin')


@pytest.fixture
def employee_al(env, employee_admin):
    rec = env.ref('hr.employee_al')
    rec.parent_id = employee_admin.id
    return rec


def test_create_org_level(model):
    assert model.level == 0


def test__compute_new_display_name(model):
    assert model.display_name == str(0) + ' ' + "Operation"


def test_approval_validation(env, model, model_line, employee_al):
    account_move_id = env['ir.model'].search(
        [('model', '=', 'account.move')]).id
    line_id_1 = model_line.create({
        'limit': 50,
        'model_id': account_move_id,
        'move_type': 'entry',
        'org_level_id': model.id
    })
    approval = []
    model.write({
        'line_ids': line_id_1
    })
    approval, res = model.approval_validation(
        'account.move', 5000, 'entry', employee_al, approval)
    assert not res
    assert approval


def test_non_approval_validation(env, model, model_line, employee_al):
    po_id = env['ir.model'].search(
        [('model', '=', 'purchase')]).id
    line_id_1 = model_line.create({
        'limit': 5000,
        'model_id': po_id,
        'org_level_id': model.id
    })
    model.write({
        'line_ids': line_id_1
    })
    approval = []
    approval, res = model.approval_validation(
        'purchase.order', 50, False, employee_al, approval)
    assert res
    assert not approval
