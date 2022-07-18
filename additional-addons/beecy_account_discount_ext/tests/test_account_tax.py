from pytest_tr_odoo.fixtures import env
import pytest

from datetime import datetime
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.move']


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
def tax_output(env):
    return env['account.tax'].create({
        'name': 'Output VAT 7%',
        'amount_type': 'percent',
        'type_tax_use': 'sale',
        'sequence': 1,
        'amount': 7
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'round': True},
     {'total_excluded': 100.0,
      'total_included': 107.0,
      'total_void': 107.0}),
    ({'round': False},
     {'total_excluded': 100.0,
      'total_included': 107.0,
      'total_void': 107.0}),
    ({'include_base_amount': True},
     {'total_excluded': 100.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': True},
     {'total_excluded': 93.46000000000001,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': True, 'amount_type': 'division'},
     {'total_excluded': 93.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': True, 'amount_type': 'fixed'},
     {'total_excluded': 93.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': True, 'amount_type': 'group'},
     {'total_excluded': 99.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': True, 'tax_exigibility': 'on_payment'},
     {'total_excluded': 93.46000000000001,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': False, 'is_base_affected': True, 'tax_exigibility': 'on_payment'},
     {'total_excluded': 100,
      'total_included': 107.0,
      'total_void': 107.0}),
    ({'force_price_include': None,
      'is_base_affected': True,
      'tax_exigibility': 'on_payment',
      },
     {'total_excluded': 100,
      'total_included': 107.0,
      'total_void': 107.0}),
    ({'force_price_include': True,
      'tax_exigibility': 'on_payment',
      'include_base_amount': True},
     {'total_excluded': 100.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_empty': True,
      'force_price_include': True,
      'tax_exigibility': 'on_payment',
      'include_base_amount': True},
     {'total_excluded': 100.0,
      'total_included': 100.0,
      'total_void': 100.0}),
    ({'force_price_include': None,
      'is_base_affected': True,
      'tax_exigibility': 'on_payment',
      'nber_rounding_steps': True,
      },
     {'total_excluded': 100,
      'total_included': 107.0,
      'total_void': 107.0}),
])
def test_compute_all(env, model, tax_output, account_id, test_input, expected):
    tax_repartition_line = env.company.account_sale_tax_id. \
        refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax')
    default_account_revenue = env['account.account'].search([
        ('company_id', '=', env.company.id),
        ('user_type_id.type', '=', 'other'),
        ('user_type_id.name', '=', 'Income')
    ], limit=1)
    product = env.ref('product.product_product_25')

    if test_input.get('include_base_amount'):
        tax_output.include_base_amount = test_input.get('include_base_amount')
        tax_output.include_base_amount = True
    if test_input.get('amount_type'):
        tax_output.include_base_amount = True
        if test_input.get('amount_type') == 'group':
            tax_output.amount_type = False
        else:
            tax_output.amount_type = test_input.get('amount_type')
    if test_input.get('tax_exigibility'):
        tax_output.include_base_amount = True
        tax_output.tax_exigibility = test_input.get('tax_exigibility')
    if test_input.get('is_base_affected'):
        tax_output.include_base_amount = True
        tax_output.is_base_affected = False
    if test_input.get('include_base_amount'):
        tax_output.include_base_amount = True
        tax_output.amount_type = 'group'

    inv = model.create({
        'partner_id': env.ref('base.partner_admin').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref(
            'account.account_payment_term_end_following_month').id,
        'move_type': 'entry',
        'invoice_date': fields.Date.today(),
        'company_id': env.ref('base.main_company').id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'account_id': account_id.id,
        })],
        'line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'account_id': account_id.id,
            'tax_repartition_line_id': tax_repartition_line.id,
        })],
    })

    price_unit = 100
    if test_input.get('force_empty'):
        env['account.tax'].with_context(
            {'round': test_input.get('round'),
             'force_price_include': test_input.get('force_price_include')}
        ).compute_all(
            price_unit, currency=None,
            quantity=1.0, product=None, partner=None,
            is_refund=False, handle_price_include=True,
            include_caba_tags=False,
            discount=0
        )
    else:
        rec = inv.invoice_line_ids.tax_ids.with_context(
            {'round': test_input.get('round'),
             'force_price_include': test_input.get('force_price_include')}
        ).compute_all(
            price_unit, currency=None, quantity=1.0, product=None, partner=None,
            is_refund=False, handle_price_include=True, include_caba_tags=False,
            discount=0
        )
        assert rec['total_excluded'] == expected.get('total_excluded')
        assert rec['total_included'] == expected.get('total_included')
        assert rec['total_void'] == expected.get('total_void')
