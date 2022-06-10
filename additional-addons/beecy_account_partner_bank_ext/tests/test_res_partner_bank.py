import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.partner.bank']


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Partner',
    })


def test_create(model, partner):
    bank = model.create({
        'bank_name': 'Partner',
        'acc_number': '1234',
        'partner_id': partner.id,
    })
    assert bank.bank_name == 'Partner'
    assert bank.acc_number == '1234'
