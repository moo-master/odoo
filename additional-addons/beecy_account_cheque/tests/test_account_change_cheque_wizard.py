import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.change.cheque.wizard']


@pytest.fixture
def bank(env):
    return env['res.bank'].create({
        'name': 'Bank'
    })


@pytest.fixture
def account_type(env):
    return env['account.account.type'].create({
        'name': 'Test Type',
        'type': 'other',
        'internal_group': 'income',
    })


@pytest.fixture
def account_id(env, account_type):
    return env['account.account'].create({
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Partner',
    })


@pytest.fixture
def partner_bank(env, partner, account_id):
    return env['res.partner.bank'].create({
        'bank_name': 'Partner',
        'acc_number': 1234,
        'partner_id': partner.id,
        'account_id': account_id.id,
    })


@pytest.fixture
def cheque(env, partner):
    return env['account.cheque'].create({
        'name': 'Cheque Old',
        'partner_id': partner.id,
        'amount': 100,
    })


def test_action_confirm(env, model, cheque, partner_bank, bank):
    wizard = model.with_context(active_ids=[cheque.id]).create({
        'name': 'Wizard Cheque',
        'cheque_date': '2022-01-01',
        'bank_id': bank.id,
        'partner_bank_id': partner_bank.id,
        'reason': 'New Cheque'
    })
    wizard.action_confirm()
    new_cheque = env['account.cheque'].search([('id', '!=', cheque.id)])
    assert cheque.state == 'cancel'
    assert new_cheque.name == 'Wizard Cheque'
    assert new_cheque.reference == cheque.name
    assert new_cheque.state == 'draft'
    assert str(new_cheque.cheque_date) == '2022-01-01'
    assert new_cheque.bank_id == bank
    assert new_cheque.from_bank_id == partner_bank
