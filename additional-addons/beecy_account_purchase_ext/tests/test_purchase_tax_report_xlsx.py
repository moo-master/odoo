import pytest
from pytest_tr_odoo.fixtures import env
from unittest.mock import call
from odoo import fields
from odoo.exceptions import ValidationError
import xlsxwriter
from io import BytesIO


@pytest.fixture
def purchase_tax_wizard(env):
    return env['report.beecy_account_purchase_ext.purchase_tax_report_xlsx']


def report_xlsx(env):
    return env['report.report_xlsx.abstract']


@pytest.fixture
def account_move(env):
    return env['account.move']


@pytest.fixture
def product1(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def product2(env):
    product = env.ref('product.product_product_3')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def partner_1(env):
    partner = env.ref('base.res_partner_1')
    return partner


@pytest.fixture
def payment_term_30days(env):
    payment_term = env.ref('account.account_payment_term_30days')
    return payment_term


@pytest.fixture
def journal_purchase(env):
    return env['account.journal'].search([
        ('type', '=', 'purchase'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)

#


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'in_refund'}, True),
    ({'move_type': 'in_invoice'}, True),
])
def test_generate_xlsx_report(
        env,
        account_move,
        purchase_tax_wizard,
        partner_demo,
        payment_term_30days,
        journal_purchase,
        product1,
        test_input,
        expected):
    account_move.create({
        'move_type': test_input.get('move_type'),
        'invoice_date': '2022-03-23',
        'company_id': env.company.id,
        'partner_id': partner_demo.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_purchase.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id
        })],
    })
    account_move.state = 'posted'
    account_move_ids = env['account.move'].search(
        [('invoice_date', '!=', False)])
    wizard = env['purchase.tax.report.wizard'].create({
        'start_date': '2022-03-23',
        'account_move_ids': [(6, 0, account_move_ids.ids)]
    })
    file_data = BytesIO()
    workbook = xlsxwriter.Workbook(file_data, {})
    data = False
    purchase_tax_wizard.generate_xlsx_report(workbook, data, wizard)
