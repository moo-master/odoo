import pytest
from unittest.mock import MagicMock
from pytest_tr_odoo.fixtures import env
from .fixtures import *


@pytest.fixture
def create_reason(env):
    return env['create.reason'].create({
        'reason': 'Reason',
    })


def test_search_reason(reason, create_reason):
    assert create_reason._search_reason() == reason


def test_prepare_data_reason(create_reason):
    model_ids = [1]
    account_type = 'out_invoice'
    assert create_reason._prepare_data_reason(model_ids, account_type) == {
        'name': create_reason.reason,
        'model_ids': [(6, 0, model_ids)],
        'account_type': account_type,
    }


@pytest.mark.parametrize('test_input', [
    {'reason': True},
    {'reason': False}
])
def test_create_reason(mocker, create_reason, ir_model_users, reason,
                       test_input):
    prepare_reason = {'test': 1}
    spy_update_reason = mocker.patch.object(
        type(reason),
        'update_model_in_reason',
    )
    spy_create_reason = mocker.patch.object(
        type(reason),
        'create',
    )
    spy_prepare_reason = mocker.patch.object(
        type(create_reason),
        '_prepare_data_reason',
        return_value=prepare_reason
    )
    spy_search_reason = mocker.patch.object(
        type(create_reason),
        '_search_reason',
        return_value=test_input['reason'] and reason
    )
    create_reason\
        .with_context(active_id=1, active_model=ir_model_users.model)\
        .create_reason()
    assert spy_search_reason.call_count == 1
    if test_input['reason']:
        spy_update_reason.assert_called_once_with(
            ir_model_users.id,
            False,
        )
    else:
        spy_prepare_reason.assert_called_once_with(
            ir_model_users.ids,
            False
        )
        spy_create_reason.assert_called_once_with(prepare_reason)
