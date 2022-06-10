import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.partner']


@pytest.fixture
def attachment(env):
    return env['ir.attachment'].create({
        'name': 'attachment'
    })


def test_create(model, attachment):
    name = 'Mabel Daniel'
    partner = model.create({
        'name': name,
        'sale_attachment_ids': [(4, attachment.id)],
        'purchase_attachment_ids': [(4, attachment.id)],
    })
    assert partner.name == name
    assert partner.sale_attachment_ids == attachment
    assert partner.purchase_attachment_ids == attachment
