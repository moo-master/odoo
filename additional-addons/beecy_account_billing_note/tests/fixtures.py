import os
import base64
import xlrd
import pytest
from odoo import fields
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def payment_term(env):
    return env['account.payment.term'].create({
        'name': 'the 15th of the month, min 31 days from now',
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
def partner(env, payment_term):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'property_payment_term_id': payment_term.id
    })


@pytest.fixture
def billing_note_wizard(env, partner):
    return env['account.billing.note'].create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today()
    })


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.fixture
def product_inv(env):
    return env['product.product'].create({
        'name': 'WEWE',
        'type': 'service',
    })


@pytest.fixture
def account_move(env, partner, currency, product_inv):
    return env['account.move'].create({
        'partner_id': partner.id,
        'invoice_date_due': fields.Date.today(),
        'currency_id': currency.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [
            (0, 0, {'product_id': product_inv.id,
                    'price_unit': 100.0,
                    'quantity': 5}),
        ]
    })
