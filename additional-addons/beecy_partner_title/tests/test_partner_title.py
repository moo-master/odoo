import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.partner.title']


def test_create(model):
    name = 'Mabel Daniel'
    prefix = 'Title Prefix'
    suffix = 'Title Suffix'
    partner = model.create({
        'name': name,
        'prefix': prefix,
        'suffix': suffix,
    })
    assert partner.name == name
    assert partner.prefix == prefix
    assert partner.suffix == suffix
    assert partner.contact_type == 'person'


def test_create2(model):
    name = 'Mabel Daniel'
    prefix = 'Title Prefix'
    suffix = 'Title Suffix'
    contact_type = 'company'
    partner = model.create({
        'name': name,
        'prefix': prefix,
        'suffix': suffix,
        'contact_type': contact_type
    })
    assert partner.name == name
    assert partner.prefix == prefix
    assert partner.suffix == suffix
    assert partner.contact_type == contact_type
