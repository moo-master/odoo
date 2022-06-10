import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['product.template']


@pytest.fixture
def wht(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def product_tmp(model, wht):
    return model.create({
        'name': 'Product A',
        'wht_type_id': wht.id,
    })


def test_create(env):
    product_tmpl = env['product.template'].create({
        'name': 'test create',
    })
    assert product_tmpl


def test__onchange_detailed_type(product_tmp):
    product_tmp._onchange_detailed_type()
    assert not product_tmp.wht_type_id
