from pytest_tr_odoo.fixtures import env
import pytest


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
def product_tmp_demo(env, wht):
    product_tmp = env.ref('product.product_product_4_product_template')
    product_tmp.write({
        'purchase_wht_type_id': wht.id,
        'wht_type_id': wht.id,
    })
    return product_tmp


def test__onchange_detailed_type(env, model, product_tmp_demo):
    product_tmp_demo.write({
        'detailed_type': 'consu'
    })
    product_tmp_demo._onchange_detailed_type()
    assert not product_tmp_demo.purchase_wht_type_id
    assert not product_tmp_demo.wht_type_id
