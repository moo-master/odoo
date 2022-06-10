import pytest
from unittest.mock import MagicMock
from pytest_tr_odoo.fixtures import env
from .fixtures import *


@pytest.fixture
def cancel_reject_reason(env):
    return env['cancel.reject.reason'].with_context(
        active_id=1,
        active_model='res.users'
    ).create({
        'description': 'Description',
    })


def test_domain_reason_id(mocker, env, cancel_reject_reason):
    expected_domain = [('id', '=', 1)]
    spy = mocker.patch.object(type(env['res.reason']),
                              '_get_domain_reason',
                              return_value=expected_domain)
    domain = cancel_reject_reason._domain_reason_id()
    spy.assert_called_once_with(
        cancel_reject_reason._context['active_model'],
        False
    )
    assert domain == expected_domain


@pytest.mark.parametrize('test_input,expected', [
    ({'is_description': True}, True),
    ({'is_description': False}, False),
])
def test_get_reason_text(reason, cancel_reject_reason, test_input, expected):
    reason.is_description = test_input['is_description']
    cancel_reject_reason.reason_id = reason
    res = cancel_reject_reason._get_reason_text()
    assert res == [reason.name, cancel_reject_reason.description][expected]


@pytest.mark.parametrize('test_input,expected', [
    ({}, {
        'action': 'action_reject_reason',
        'write': {
            'reject_reason': 'text',
            'state': 'reject'
        }
    }),
    ({'state': 'cancel'}, {
        'action': 'action_cancel_reason',
        'write': {
            'cancel_reason': 'text',
            'state': 'cancel'
        }
    }),
    ({'state': 'reject'}, {
        'action': 'action_reject_reason',
        'write': {
            'reject_reason': 'text',
            'state': 'reject'
        }
    }),
])
def test_button_confirm(mocker, env, cancel_reject_reason,
                        test_input, expected):
    spy_get_text = mocker.patch.object(
        type(cancel_reject_reason),
        '_get_reason_text',
        return_value='text'
    )
    spy_action = MagicMock()
    setattr(
        type(env['res.users']),
        expected['action'],
        spy_action
    )
    spy_write = mocker.patch.object(
        type(env['res.users']),
        'write',
        return_value=True
    )
    cancel_reject_reason.env.context = {
        **cancel_reject_reason.env.context,
        **test_input
    }
    cancel_reject_reason.button_confirm()
    assert spy_get_text.call_count == 1
    assert spy_action.call_count == 1
    spy_write.assert_called_once_with(expected['write'])
