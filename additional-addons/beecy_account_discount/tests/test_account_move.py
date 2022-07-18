import pytest
from pytest_tr_odoo.fixtures import env


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
    ({'price_unit': 100, 'formula': '10'}, 90),
    ({'price_unit': 100, 'formula': '5'}, 95),
])
def test__get_price_discount_model(env,
                                   model,
                                   mocker,
                                   test_input,
                                   expected):

    spy_fator = mocker.spy(
        type(model),
        '_get_ordered_factor',
    )
    value = model._get_price_discount_model(
        price_unit=test_input['price_unit'], formula=test_input['formula'])
    assert spy_fator.called
    assert value == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'price_unit': 100, 'formula': '10'}, 111.11111111111111),
    ({'price_unit': 100, 'formula': '5'}, 105.26315789473685),
])
def test__get_price_wo_discount_model(env,
                                      model,
                                      mocker,
                                      test_input,
                                      expected):

    spy_fator = mocker.spy(
        type(model),
        '_get_ordered_factor',
    )
    value = model._get_price_wo_discount_model(
        price_unit=test_input['price_unit'], formula=test_input['formula'])
    assert spy_fator.called
    assert value == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'formula': '10'}, [0.9]),
    ({'formula': '90'}, [0.09999999999999998]),
    ({'formula': 'None'}, []),
])
def test__get_ordered_factor(env, model, test_input, expected):
    formula = model._get_ordered_factor(test_input['formula'])
    assert formula == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'formula_discount': ''}, 0),
    ({'formula_discount': '10'}, 89),
])
def test__compute_prorated_discount(env,
                                    model,
                                    mocker,
                                    partner_demo,
                                    product1,
                                    test_input,
                                    expected,
                                    ):
    invoice2 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'formula_discount': test_input['formula_discount'],
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 10,
            'price_unit': 100,
            'formula_discount': 10,
            'direct_discount': 10,
        })],
    })
    spy_get_price_discount_model = mocker.spy(
        type(invoice2),
        '_get_price_discount_model',
    )

    invoice2.line_ids._compute_prorated_discount()
    assert spy_get_price_discount_model
    for rec in invoice2.line_ids:
        if rec.exclude_from_invoice_tab or not rec.price_unit:
            assert rec.prorated_discount == 0
        else:
            assert rec.prorated_discount == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'price_include': True}, 100),
    ({'price_include': False}, 100),
])
def test__compute_price_subtotal_wo_prorated(model,
                                             env,
                                             tax_output,
                                             partner_demo,
                                             product1,
                                             test_input,
                                             expected):
    tax_output.write({
        'price_include': test_input['price_include'],
    })
    invoice3 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'formula_discount': '10',
        'direct_discount': 50,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
        })],
    })
    invoice3.invoice_line_ids._compute_price_subtotal_wo_prorated()
    assert invoice3.invoice_line_ids.price_subtotal_wo_prorated == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'formula_discount': '', 'direct_discount': '5'}, 100),
    ({'formula_discount': '10'}, 100),
])
def test__compute_amount_before_global_discount(model,
                                                env,
                                                tax_output,
                                                partner_demo,
                                                product1,
                                                test_input,
                                                expected):
    invoice4 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'formula_discount': 10,
        'direct_discount': 50,
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
        })],
    })
    invoice4._compute_amount()
    assert invoice4.amount_before_global_discount == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'in_invoice'}, 85.00),
])
def test__get_amount_total_after_onchange_balance_model(
        env,
        model,
        test_input,
        expected,
        partner_demo,
        product1,
        tax_output):
    tax_output.write({
        'price_include': True,
    })
    invoice3 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': test_input['move_type'],
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'formula_discount': 10,
            'direct_discount': 5,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
        })],
    })
    assert invoice3.amount_total == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'out_invoice'}, -5.95),
    ({'move_type': 'entry'}, -6.3),
])
def test__compute_base_line_taxes(
        env,
        model,
        partner_demo,
        product1,
        tax_output,
        test_input,
        expected):
    invoice4 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'formula_discount': '10',
            'direct_discount': 5,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
        })],
    })
    for line in invoice4.line_ids:
        line.move_id.move_type = test_input['move_type']
        val = line._compute_base_line_taxes()
        if val['taxes'] != []:
            assert val['taxes'][0]['amount'] == expected


def test_recompute_create_line(env,
                               model,
                               mocker,
                               partner_demo,
                               product1,
                               tax_output):
    inv = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'price_unit': 0,
            'tax_ids': tax_output.ids,
        })],
    })
    vals_list = [{
        'date': '30-05-2022',
        'company_id': 1,
        'company_currency_id': 2,
        'account_id': 21, 'name':
            'Office Design Software',
            'quantity': 1.0,
            'price_unit': 0.0,
            'debit': 0.0,
            'credit': 0.0,
            'balance': 0.0,
            'amount_currency': 0.0,
            'price_subtotal': 0.0,
            'price_total': 0.0,
            'currency_id': 2,
            'partner_id': 7,
            'product_id': 7,
            'tax_ids': False,
            'tax_repartition_line_id': False,
            'tax_tag_ids': False,
            'matched_debit_ids': False,
            'matched_credit_ids': False,
            'analytic_line_ids': False,
            'recompute_tax_line': False,
            'display_type': False,
            'is_rounding_line': False,
            'exclude_from_invoice_tab': False,
            'formula_discount': False,
            'direct_discount': 0.0,
            'price_unit_discount': 0.0,
            'prorated_discount': 0.0,
            'move_id': inv.invoice_line_ids.move_id.id
    },
        {
            'company_id': 1,
            'company_currency_id': 2,
            'account_id': 21,
            'name': 'Output VAT 7%',
            'quantity': 1.0,
            'price_unit': 0.0,
            'debit': 0.0,
            'credit': 0.0,
            'balance': 0.0,
            'amount_currency': 0.0,
            'price_subtotal': 0.0,
            'currency_id': 2,
            'tax_ids': False,
            'group_tax_id': False,
            'tax_base_amount': 0.0,
            'tax_repartition_line_id': 1478,
            'tax_tag_ids': False,
            'matched_debit_ids': False,
            'matched_credit_ids': False,
            'analytic_account_id': False,
            'analytic_tag_ids': False,
            'display_type': False,
            'is_rounding_line': False,
            'exclude_from_invoice_tab': True,
            'formula_discount': False,
            'direct_discount': 0.0,
            'prorated_discount': 0.0,
            'move_id': inv.invoice_line_ids.move_id.id
    },
        {
            'account_id': 6,
            'name': '',
            'quantity': 1.0,
            'price_unit': 0.0,
            'debit': 0.0,
            'credit': 0.0,
            'amount_currency': 0.0,
            'price_subtotal': 0.0,
            'date_maturity': '30-05-2022',
            'currency_id': 2,
            'partner_id': 7,
            'tax_ids': False,
            'matched_debit_ids': False,
            'matched_credit_ids': False,
            'display_type': False,
            'exclude_from_invoice_tab': True,
            'formula_discount': False,
            'direct_discount': 0.0,
            'prorated_discount': 0.0,
            'move_id': inv.invoice_line_ids.move_id.id
    }]
    vals_lst = inv.line_ids.recompute_create_line(vals_list)
    spy__get_price_total_and_subtotal_model = mocker.spy(
        type(inv.line_ids),
        '_get_price_total_and_subtotal_model',
    )
    for val in vals_lst:
        assert val['debit'] == 0
        assert val['credit'] == 0
    assert spy__get_price_total_and_subtotal_model


def test__onchange_discount(env, model, partner_demo, product1, mocker):
    invoice5 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product1.id,
            'name': product1.name,
            'quantity': 1,
            'price_unit': 100,
        })],
    })

    spy__compute_prorated_discount = mocker.spy(
        type(invoice5.line_ids),
        '_compute_prorated_discount',
    )
    spy__onchange_price_subtotal = mocker.spy(
        type(invoice5.invoice_line_ids),
        '_onchange_price_subtotal',
    )
    invoice5._onchange_discount()
    assert spy__compute_prorated_discount
    assert spy__onchange_price_subtotal


def test__onchange_invoice_discount(env, model, mocker):
    invoice6 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': env.ref('base.partner_admin').id,
        'move_type': 'out_invoice',
        'formula_discount': '',
        'direct_discount': 0.0,
        'invoice_line_ids': [(0, 0, {
            'product_id': env.ref('product.product_order_01').id,
            'name': env.ref('product.product_order_01').name,
            'quantity': 1,
            'price_unit': 100,
        })],
    })
    spy__onchange_price_subtotal = mocker.spy(
        type(invoice6),
        '_onchange_discount',
    )
    invoice6._onchange_invoice_discount()
    assert spy__onchange_price_subtotal


def test__onchange_invoice_line_ids(env, model, mocker):
    invoice7 = model.create({
        'invoice_date': '2022-05-20',
        'partner_id': env.ref('base.partner_admin').id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': env.ref('product.product_order_01').id,
            'name': env.ref('product.product_order_01').name,
            'quantity': 1,
            'price_unit': 100,
        })],
    })
    spy__onchange_price_subtotal = mocker.spy(
        type(invoice7),
        '_onchange_invoice_discount',
    )
    invoice7._onchange_invoice_line_ids()
    assert spy__onchange_price_subtotal
