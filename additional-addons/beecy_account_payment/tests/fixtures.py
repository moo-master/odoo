import os
import base64
import xlrd
import pytest
from pytest_tr_odoo.fixtures import env
from datetime import datetime
from odoo import fields


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def invoice_line_payment(env, journal_sale):
    partner = env.ref('base.partner_demo')
    payment_term_30 = env.ref('account.account_payment_term_30days')
    product_invoice = env.ref('product.product_order_01')
    return env['account.move'].create({
        'partner_id': partner.id,
        'invoice_payment_term_id': payment_term_30.id,
        'journal_id': journal_sale.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product_invoice.id
        })],
    })


@pytest.fixture
def journal_payment_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def payment_customer(env, invoice_line_payment, journal_payment_cash):
    partner = env.ref('base.partner_demo')
    return env['beecy.account.payment'].create({
        'payment_type': 'outbound',
        'partner_id': partner.id,
        'date_date': fields.Date.today(),
        'journal_id': journal_payment_cash.id,
        'company_id': env.company.id,
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': invoice_line_payment.id
        })],
        'payment_line_wht_ids': [(0, 0, {
            'amount_wht': 100
        })]
    })


@pytest.fixture
def account_account_type_pay(env):
    return env['account.account.type'].create({
        'name': 'credit',
        'type': 'liquidity',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account_pay(env, account_account_type_pay):
    return env['account.account'].create({
        'name': 'acc acc',
        'user_type_id': account_account_type_pay.id,
        'code': '01',
    })


@pytest.fixture
def payment_method_line_pay(env, account_account_pay):
    payment_method = env.ref('account.account_payment_method_manual_in')
    return env['account.payment.method.line'].create({
        'payment_method_id': payment_method.id,
        'payment_account_id': account_account_pay.id,
    })
