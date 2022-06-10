import pytest
from pytest_tr_odoo.fixtures import env
from unittest.mock import MagicMock, call
from odoo.tests.common import Form
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale'
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
def account_other_income_income(env):
    account_type = env.ref('account.data_account_type_other_income')
    return env['account.account'].create({
        'code': '4002',
        'name': 'Test Account Income',
        'user_type_id': account_type.id,
        'reconcile': True
    })


@pytest.fixture
def account_receivable(env, account_type):
    return env['account.account'].create({
        'code': '1000',
        'name': 'Test Receivable Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_payable(env, account_type):
    return env['account.account'].create({
        'code': '2000',
        'name': 'Test Payable Account',
        'user_type_id': account_type.id
    })


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
def partner(env, payment_term, account_receivable, account_payable):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'company_id': env.company.id,
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def product(env):
    return env['product.product'].create({
        'name': 'Mini Fan',
    })


@pytest.fixture
def tax_input(env):
    return env['account.tax'].create({
        'name': 'Input VAT 7%',
        'amount_type': 'percent',
        'type_tax_use': 'purchase',
        'amount': 7
    })


@pytest.fixture
def tax_output(env):
    return env['account.tax'].create({
        'name': 'Output VAT 7%',
        'amount_type': 'percent',
        'type_tax_use': 'sale',
        'amount': 7
    })


@pytest.fixture
def product1(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


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
def invoice(env, model, product1,
            partner_demo,
            account_other_income_income, tax_output):
    return env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 10,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'formula_discount': 10,
            'direct_discount': 10,
        })],
    })


@pytest.mark.parametrize('test_input,expected', [
    (True, True),
    (False, False)
])
def test_create(
        env, mocker, partner_demo, product1,
        tax_output, test_input, expected):
    check_balanced_spy = mocker.spy(
        type(env['account.move']), '_check_balanced')
    res = env['account.move'].with_context(
        check_move_validity=test_input).create(
        {
            'invoice_date': '2022-05-20',
            'partner_id': partner_demo.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': product1.id,
                'name': product1.name,
                'quantity': 10,
                'price_unit': 100,
                'tax_ids': tax_output.ids,
                'formula_discount': 10,
                'direct_discount': 10,
            })],
        })
    if test_input:
        check_balanced_spy.assert_called_once_with(res)


@pytest.mark.parametrize('test_input,expected', [
    ({
        'price_unit': 100, 'quantity': 10,
        'price_subtotal': 1000.0, 'formula': '10'}, 90),
    ({
        'price_unit': 100, 'quantity': 10,
        'price_subtotal': 1000.0, 'formula': '5'}, 95),
])
def test__get_price_total_and_subtotal(
        env,
        mocker,
        monkeypatch,
        partner_demo,
        product1,
        tax_output,
        test_input,
        expected):
    invoice = env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_refund',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': test_input.get('quantity'),
            'price_unit': test_input.get('price_unit'),
            'tax_ids': tax_output.ids,
            'formula_discount': test_input.get('formula'),
            'direct_discount': test_input.get('formula'),
        })],
    })
    monkeypatch.setattr(type(env['account.move.line']),
                        '_get_price_total_and_subtotal_model',
                        lambda *args,
                        **kwargs: {
                            'price_subtotal': test_input.get('price_subtotal'),
                            'price_total': test_input.get('price_unit')})
    move_line = invoice.line_ids[0]
    price_total_model_spy = mocker.spy(
        type(env['account.move.line']),
        '_get_price_total_and_subtotal_model',
    )
    res = move_line._get_price_total_and_subtotal(
        price_unit=None, quantity=1.0, discount=0.0, currency=None,
        product=None, partner=None, taxes=None,
        move_type='out_refund',
        formula_discount=test_input.get('formula'), prorated_discount=0.0
    )
    product = move_line.product_id
    price_unit = move_line.price_unit
    quantity = move_line.quantity
    discount = move_line.direct_discount
    move_type = move_line.move_id.move_type
    currency = move_line.currency_id
    taxes = move_line.tax_ids
    formula_discount = test_input.get('formula')
    prorated_discount = move_line.prorated_discount
    expected = {
        'currency': currency,
        'discount': discount,
        'formula_discount': formula_discount,
        'move_type': move_type,
        'partner': partner_demo,
        'price_unit': price_unit,
        'product': product,
        'prorated_discount': prorated_discount,
        'quantity': 1.0,
        'taxes': taxes,
    }
    price_total_model_spy.assert_any_call(move_line, **expected)
    assert res == {
        'price_subtotal': test_input.get('price_subtotal'),
        'price_total': test_input.get('price_unit')}


@pytest.mark.parametrize('test_input,expected', [
    ({
        'move_type': 'out_invoice', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 0.0}, 90),
    ({
        'move_type': 'out_refund', 'quantity': 1.0, 'formula_discount': 0.0,
        'price_unit': 100, 'direct_discount': 10.0}, 90),
    ({
        'move_type': 'out_debit', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 10.0}, 90),

])
def test__get_fields_onchange_balance(
        env,
        monkeypatch,
        mocker,
        partner_demo,
        account_id,
        tax_output,
        product1,
        test_input,
        expected):
    invoice = env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': test_input.get('move_type'),
    })
    invoice.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': test_input.get('quantity'),
            'tax_ids': [(6, 0, tax_output.ids)],
            'price_unit': test_input.get('price_unit'),
            'account_id': product1.property_account_income_id.id if
            product1.property_account_income_id.id else account_id.id,
            'formula_discount': test_input.get('formula_discount'),
            'direct_discount': test_input.get('direct_discount'),
        })],
    })
    move_line = invoice.line_ids[0]
    quantity = move_line.quantity
    discount = move_line.direct_discount
    amount_currency = move_line.amount_currency
    move_type = move_line.move_id.move_type
    currency = move_line.currency_id
    taxes = move_line.tax_ids
    price_subtotal = move_line.price_subtotal
    force_computation = False
    formula_discount = move_line.formula_discount
    prorated_discount = move_line.prorated_discount
    monkeypatch.setattr(type(env['account.move.line']),
                        '_get_fields_onchange_balance_model',
                        lambda *args,
                        **kwargs:
                        {'quantity': test_input.get('quantity'),
                         'discount': discount,
                         'price_unit': test_input.get('price_unit'),
                         'prorated_discount': prorated_discount})
    onchange_balance_model_spy = mocker.spy(
        type(env['account.move.line']),
        '_get_fields_onchange_balance_model',
    )
    res = move_line._get_fields_onchange_balance(
        quantity=quantity, discount=discount,
        amount_currency=amount_currency,
        move_type=move_type, currency=currency, taxes=taxes,
        price_subtotal=price_subtotal, force_computation=force_computation,
        formula_discount=formula_discount, prorated_discount=prorated_discount)
    assert res == {'quantity': test_input.get('quantity'),
                   'discount': discount,
                   'price_unit': test_input.get('price_unit'),
                   'prorated_discount': prorated_discount}
    assert onchange_balance_model_spy.called


@pytest.fixture
def fixed_tax(env):
    return env['account.tax'].create({
        'name': "Fixed tax",
        'amount_type': 'fixed',
        'amount': 10,
        'sequence': 1,
    })


@pytest.mark.parametrize('test_input,expected', [
    ({
        'move_type': 'out_invoice', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 0.0}, 90),
    ({
        'move_type': 'out_invoice', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 0.0,
        'amount_currency': 100.0}, 90),
    ({
        'move_type': 'out_invoice', 'quantity': 1.0,
        'formula_discount': 10.0, 'amount_type': 'group',
        'price_unit': 100, 'direct_discount': 0.0}, 90),
    ({
        'move_type': 'out_refund', 'quantity': 1.0, 'formula_discount': 0.0,
        'price_unit': 100, 'direct_discount': 10.0}, 90),
    ({
        'move_type': 'out_debit', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 10.0}, 90),
    ({
        'move_type': 'out_debit', 'quantity': 1.0, 'formula_discount': 10.0,
        'price_unit': 100, 'direct_discount': 10.0,
        'amount_currency': 100.0}, 90)

])
def test__get_fields_onchange_balance_model(
        env,
        monkeypatch,
        mocker,
        partner_demo,
        account_id,
        tax_output,
        fixed_tax,
        product1,
        test_input,
        expected):
    # with_context({'create_map': True}) env, price_unit=100, formula='10'
    monkeypatch.setattr(type(env['account.move']),
                        '_get_price_wo_discount_model',
                        lambda *args, **kwargs: True)

    invoice = env['account.move'].create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': test_input.get('move_type'),
    })
    if test_input.get('amount_type'):
        tax_output.amount_type = test_input.get('amount_type')
        tax_output.price_include = True
        tax_output.children_tax_ids = [(6, 0, fixed_tax.ids)]
        fixed_tax.price_include = True
    invoice.write({
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': test_input.get('quantity'),
            'tax_ids': [(6, 0, tax_output.ids)],
            'price_unit': test_input.get('price_unit'),
            'account_id': product1.property_account_income_id.id if
            product1.property_account_income_id.id else account_id.id,
            'formula_discount': test_input.get('formula_discount'),
            'direct_discount': test_input.get('direct_discount'),
        })],
    })
    if test_input.get('amount_currency'):
        amount_currency = test_input.get('amount_currency')
    else:
        amount_currency = 0.0
    move_line = invoice.line_ids[0]
    quantity = move_line.quantity
    discount = move_line.direct_discount
    amount_currency = amount_currency
    move_type = move_line.move_id.move_type
    currency = move_line.currency_id
    taxes = move_line.tax_ids
    price_subtotal = move_line.price_subtotal
    force_computation = False
    formula_discount = move_line.formula_discount
    prorated_discount = move_line.prorated_discount
    flatten_taxes_spy = mocker.spy(
        type(env['account.tax']),
        'flatten_taxes_hierarchy',
    )
    move_line._get_fields_onchange_balance_model(
        quantity=quantity, discount=discount,
        amount_currency=amount_currency, move_type=move_type,
        currency=currency, taxes=taxes, price_subtotal=price_subtotal,
        force_computation=True, formula_discount=formula_discount,
        prorated_discount=prorated_discount
    )


def test_recompute_create_line(env, monkeypatch, mocker,):
    tax_repartition_line = env.company.account_sale_tax_id. \
        refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax')
    default_account_revenue = env['account.account'].search([
        ('company_id', '=', env.company.id),
        ('user_type_id.type', '=', 'other'),
        ('user_type_id.name', '=', 'Income')
    ], limit=1)
    monkeypatch.setattr(type(env['account.move']),
                        'is_invoice', lambda a, **kwargs: True)
    inv = env['account.move'].create({
        'partner_id': env.ref('base.partner_admin').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref(
            'account.account_payment_term_end_following_month').id,
        'move_type': 'out_invoice',
        'invoice_date': fields.Date.today(),
        'line_ids': [
            (0, None, {
                'name': 'revenue line 1',
                'account_id': default_account_revenue.id,
                'debit': 500.0,
                'credit': 0.0,
            }),
            (0, None, {
                'name': 'tax line',
                'account_id': default_account_revenue.id,
                'debit': 0.0,
                'credit': 0.0,
                'tax_repartition_line_id': tax_repartition_line.id,
            }),
            (0, None, {
                'name': 'counterpart line',
                'account_id': default_account_revenue.id,
                'debit': 0.0,
                'credit': 500.0,
            }),
        ]

    })
    inv.line_ids[1].recompute_create_line([
        {'move_id': inv.id,
         'currency_id': env.ref('base.AUD').id,
         'price_unit': 100,
         'quantity': 1,
         'discount': 0,
         }
    ])
    res = inv.line_ids[0].recompute_create_line([
        {'move_id': inv.id, 'currency_id': env.ref('base.AUD').id}
    ])
    is_invoice_spy = mocker.spy(type(env['account.move']), 'is_invoice')
    expected = [{'move_id': inv.id,
                 'currency_id': env.ref('base.AUD').id,
                 'company_currency_id':
                     env.ref('base.main_company').currency_id.id,
                 'amount_currency': 0.0}]
    assert res == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'currency_id': None}, True),
    ({'currency_id': True}, True),
])
def test__compute_base_line_taxes(env, model, test_input, expected):
    tax_repartition_line = env.company.account_sale_tax_id.\
        refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax')
    default_account_revenue = env['account.account'].search([
        ('company_id', '=', env.company.id),
        ('user_type_id.type', '=', 'other'),
        ('user_type_id.name', '=', 'Income')
    ], limit=1)
    if test_input.get('currency_id'):
        inv = model.create({
            'partner_id': env.ref('base.partner_admin').id,
            'invoice_user_id': env.ref('base.user_demo').id,
            'invoice_payment_term_id': env.ref(
                'account.account_payment_term_end_following_month').id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'company_id': env.ref('base.main_company').id,
            'currency_id': env.ref('base.main_company').currency_id.id,
            'line_ids': [
                (0, None, {
                    'name': 'revenue line 1',
                    'account_id': default_account_revenue.id,
                    'debit': 500.0,
                    'credit': 0.0,
                }),
                (0, None, {
                    'name': 'tax line',
                    'account_id': default_account_revenue.id,
                    'debit': 0.0,
                    'credit': 0.0,
                    'tax_repartition_line_id': tax_repartition_line.id,
                }),
                (0, None, {
                    'name': 'counterpart line',
                    'account_id': default_account_revenue.id,
                    'debit': 0.0,
                    'credit': 500.0,
                }),
            ]

        })
    else:
        inv = model.create({
            'partner_id': env.ref('base.partner_admin').id,
            'invoice_user_id': env.ref('base.user_demo').id,
            'invoice_payment_term_id': env.ref(
                'account.account_payment_term_end_following_month').id,
            'move_type': 'entry',
            'invoice_date': fields.Date.today(),
            'line_ids': [
                (0, None, {
                    'name': 'revenue line 1',
                    'account_id': default_account_revenue.id,
                    'debit': 500.0,
                    'credit': 0.0,
                }),
                (0, None, {
                    'name': 'tax line',
                    'account_id': default_account_revenue.id,
                    'debit': 0.0,
                    'credit': 0.0,
                    'tax_repartition_line_id': tax_repartition_line.id,
                }),
                (0, None, {
                    'name': 'counterpart line',
                    'account_id': default_account_revenue.id,
                    'debit': 0.0,
                    'credit': 500.0,
                }),
            ]

        })
    expected = {'base_tags': [],
                'taxes': [],
                'total_excluded': 500.0,
                'total_included': 500.0,
                'total_void': 500.0
                }
    res = inv.line_ids[0].with_context({})._compute_base_line_taxes()
    assert res == expected
