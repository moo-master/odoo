import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env["account.journal"]


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].create({
        'name': 'JV Sale',
        'type': 'sale',
        'code': 'JV-SO',
        'company_id': env.company.id,
    })


@pytest.mark.parametrize('test_input', [
    ({'name': 'sale 1',
      'type': 'sale',
      'code': 'CN',
      'is_debit_note_sequence': False}),
    ({'name': 'sale 2',
      'type': 'sale',
      'code': 'DN',
      'is_debit_note_sequence': True}),
    ({'name': 'purchase 1',
      'type': 'purchase',
      'code': 'SCN',
      'is_debit_note_sequence': True}),
    ({'name': 'purchase 2',
      'type': 'purchase',
      'code': 'SDN',
      'is_debit_note_sequence': False})
])
def test_create(env, model, test_input):
    model.create({
        'name': test_input.get('name'),
        'type': test_input.get('type'),
        'code': test_input.get('code'),
        'is_debit_note_sequence': test_input.get('is_debit_note_sequence'),
        'company_id': env.company.id,
    })


def test__onchange_type(env, journal_sale):
    journal_sale.type = 'purchase'
    journal_sale._onchange_type()
