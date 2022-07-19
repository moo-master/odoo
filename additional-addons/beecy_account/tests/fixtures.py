import os
import base64
import xlrd
import pytest
from odoo import fields
from pytest_tr_odoo.fixtures import env
# from .test_account_move import partner


@pytest.fixture
def company2(env, account_account2):
    return env["res.company"].create({
        "name": "company 2",
    })


@pytest.fixture
def product_inv(env, company2):
    return env['product.product'].create({
        'name': 'WEWE',
        'type': 'service',
        'company_id': company2.id,
    })


@pytest.fixture
def account_account_type2(env):
    return env['account.account.type'].create({
        'name': 'credit2',
        'type': 'other',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account2(env, account_account_type2):
    return env['account.account'].create({
        'name': 'acc2 acc2',
        'user_type_id': account_account_type2.id,
        'code': '02',
    })


@pytest.fixture
def account_journal2(env, account_account_type, company2):
    return env['account.journal'].create({
        'name': 'test_out_invoice_multi_company',
        'code': 'XXXXX',
        'type': 'sale',
        'company_id': company2.id,

    })


@pytest.fixture
def currency2(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.fixture
def payment_term2(env, company2):
    return env['account.payment.term'].create({
        'name': 'the 15th of the month, min 31 days from now',
        'company_id': company2.id,
        'line_ids': [
                (0, 0, {
                    'value': 'balance',
                    'days': 31,
                    'day_of_the_month': 15,
                    'option': 'day_after_invoice_date',
                }),
        ],
    })


@pytest.fixture
def account_receivable2(env, account_type, company2):
    return env['account.account'].create({
        'code': '1000',
        'company_id': company2.id,
        'name': 'Test Receivable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_payable2(env, account_type, company2):
    return env['account.account'].create({
        'code': '2000',
        'company_id': company2.id,
        'name': 'Test Payable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def invoice2(
        model,
        product,
        partner2,
        account_id):
    return model.create({
        "partner_id": partner2.id,
        "move_type": "out_invoice",
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


@pytest.fixture
def partner2(env, payment_term, account_receivable, account_payable):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })
