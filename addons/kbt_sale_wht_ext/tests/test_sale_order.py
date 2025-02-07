from pytest_tr_odoo.fixtures import env
from odoo.exceptions import ValidationError
import pytest


@pytest.fixture
def model(env):
    return env['sale.order']


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'Baht',
        'symbol': 'Baht',
    })


@pytest.fixture
def company(env, currency):
    return env['res.company'].create({
        'name': 'Test Company',
        'currency_id': currency.id,
    })


@pytest.fixture
def partner(env):
    return env.ref('base.user_admin')


@pytest.fixture
def account_type(env):
    return env['account.account.type'].create({
        'name': 'Test Type',
        'type': 'other',
        'internal_group': 'expense',
    })


@pytest.fixture
def account_id(env, account_type, company):
    return env['account.account'].create({
        'code': '4000',
        'name': 'Test Account',
        'user_type_id': account_type.id,
        'internal_type': 'other',
        'internal_group': 'expense',
        'company_id': company.id,
        'reconcile': True,
    })


@pytest.fixture
def account_receivable(env, account_type):
    return env['account.account'].create({
        'code': '1000',
        'name': 'Test Receivable Account',
        'user_type_id': account_type.id,
        'internal_type': 'receivable',
        'internal_group': 'asset',
        'reconcile': True,
    })


@pytest.fixture
def account_payable(env, account_type):
    return env['account.account'].create({
        'code': '2000',
        'name': 'Test Payable Account',
        'user_type_id': account_type.id,
        'internal_type': 'payable',
        'internal_group': 'liability',
        'reconcile': True,
    })


@pytest.fixture
def journal(env, currency, partner):
    return env['account.journal'].create({
        'name': 'Sale',
        'type': 'sale',
        'code': 'SO',
        'company_id': partner.company_id.id,
        'currency_id': currency.id,
    })


@pytest.fixture
def vendor(env, account_receivable, account_payable, company):
    return env['res.partner'].create({
        'name': 'Tester',
        "type": "contact",
        'company_id': company.id,
        "property_account_receivable_id": account_receivable.id,
        "property_account_payable_id": account_payable.id,
        'is_company': True,
    })


@pytest.fixture
def acc_wht(env, account_id):
    return env['account.wht.type'].create({
        'display_name': 'Test WHT',
        'percent': 8,
        'account_id': account_id.id,
    })


@pytest.fixture
def product(env):
    return env.ref('product.expense_product')


def test_compute_wht_amount(model, vendor, currency, product, acc_wht):
    so = model.create({
        'partner_id': vendor.id,
        'currency_id': currency.id,
        'date_order': '2022-08-31 11:11:11',
        'order_line': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'sequence': 10,
            'product_uom_qty': 10,
            'product_uom': 1,
            'price_unit': 100,
            'wht_type_id': acc_wht.id
        })],
    })
    so._compute_wht_amount()
    assert so.amount_wht == 80


def test_create_invoices(
        env,
        model,
        acc_wht,
        journal,
        product,
        partner,
        currency):
    so = model.create({
        'partner_id': partner.id,
        'date_order': '2022-08-31 11:11:11',
        'order_line': [
            (0, 0, {
                'product_id': product.id,
                'name': product.name,
                'sequence': 10,
                'product_uom_qty': 10,
                'product_uom': 1,
                'currency_id': currency.id,
                'price_unit': 100,
                'qty_delivered': 2,
                'wht_type_id': acc_wht.id
            }),
            (0, 0, {
                'product_id': product.id,
                'name': product.name,
                'sequence': 10,
                'product_uom_qty': 10,
                'product_uom': 1,
                'currency_id': currency.id,
                'price_unit': 100,
                'qty_delivered': 2
            })
        ],
    })

    so.action_confirm()

    res = so._create_invoices()

    assert res.invoice_line_ids.wht_type_id == so.order_line.wht_type_id
