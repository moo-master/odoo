from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['org.level'].create({
        'level': 123456789,
        'description': "test",
    })


@pytest.fixture
def model_line(env):
    return env['org.level.line']


def test_create_org_level(model):
    assert model.level == 123456789


def test__compute_new_display_name(model):
    assert model.display_name == str(123456789) + ' ' + "test"


def test_approval_validation(env, model, model_line):
    account_move_id = env['ir.model'].search(
        [('model', '=', 'account.move')]).id
    line_id_1 = model_line.create({
        'limit': 50,
        'model_id': account_move_id,
        'move_type': 'entry',
        'org_level_id': model.id
    })
    model.write({
        'line_ids': line_id_1
    })
    res = model.approval_validation('account.move', 5000, 'entry')
    assert res == False


def test_non_approval_validation(env, model, model_line):
    account_move_id = env['ir.model'].search(
        [('model', '=', 'account.move')]).id
    line_id_1 = model_line.create({
        'limit': 5000,
        'model_id': account_move_id,
        'move_type': 'entry',
        'org_level_id': model.id
    })
    model.write({
        'line_ids': line_id_1
    })
    res = model.approval_validation('purchase.order', 50, 'entry')
    assert res
