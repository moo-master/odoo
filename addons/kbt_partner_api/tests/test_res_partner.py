from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['res.partner']


def test_create_partner(model):
    res_partner = model.create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'company_id': 1,
        'x_interface_id': 'Test-id-001',
    })
    assert res_partner.x_interface_id
    assert res_partner.ref == res_partner.x_interface_id
