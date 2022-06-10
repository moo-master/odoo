import pytest
from pytest_tr_odoo.fixtures import env
import decimal


@pytest.fixture
def wht_type(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 10,
    })


def test_compute_wht_amount(env, wht_type):
    wht_line = env['account.wht.line'].new({
        'wht_type_id': wht_type.id
    })
    wht_line._compute_wht_amount()
    expected = wht_line.base_amount * wht_line.percent / 100
    assert wht_line.wht_amount == expected


@pytest.fixture
def account_move(env):
    return env['account.move']


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'TOR',
        'rate': 1.000000,
        'currency_unit_label': 'TOBaht',
        'currency_subunit_label': 'TOSatang',
        'symbol': 'TO฿'
    })


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Your TEST',
        'email': 'test@other23.company.com',
        'supplier_rank': 10,
        'company_id': 1,
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
def journal_sale(env):
    return env['account.journal'].create({
        'name': 'HU',
        'code': 'HU',
        'type': 'sale'
    })


@pytest.fixture
def product1(env):
    product = env['product.product'].create({
        'name': 'product acc move',
        'lst_price': 600.0,
    })
    return product


@pytest.fixture
def move(env,
         wht_type,
         account_move,
         partner,
         journal_sale,
         product1,
         currency):
    return account_move.create({
        'partner_id': partner.id,
        'journal_id': journal_sale.id,
        'currency_id': currency.id,
    })


def test_compute_tax(
        env,
        wht_type,
        account_move,
        partner,
        journal_sale,
        product1,
        currency):
    acc_m = account_move.create({
        'partner_id': partner.id,
        'journal_id': journal_sale.id,
        'currency_id': currency.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'price_unit': product1.lst_price,
            'quantity': 5,
        })],
    })
    acc_wht_line = env['account.wht.line'].create({
        'invoice_line_id': acc_m.invoice_line_ids.id,
        'wht_type_id': wht_type.id
    })
    acc_wht_line._compute_wht_amount()
    acc_wht_line._compute_base_amount()
    acc_wht_line._compute_tax()
    expected = round((wht_type.percent / 100) * acc_wht_line.base_amount, 2)
    assert acc_wht_line.tax == expected


def test__onchange_wht_type_id(env,
                               move,
                               wht_type,
                               account_id,
                               product1):
    move.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'price_unit': product1.lst_price,
            'wht_type_id': wht_type.id,
            'quantity': 5,
            'account_id': product1.property_account_income_id.id if
            product1.property_account_income_id.id else account_id.id
        })],
    })
    acc_wht_line = env['account.wht.line'].create({
        'invoice_line_id': move.invoice_line_ids.id,
    })
    acc_wht_line._onchange_wht_type_id()
    assert acc_wht_line.wht_type_id == wht_type
