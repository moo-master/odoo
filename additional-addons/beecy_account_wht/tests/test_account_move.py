from math import exp
import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields
from odoo.exceptions import ValidationError


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def acc_wht(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 0.7,
        'sequence': 5,
    })


@pytest.fixture
def product(env, acc_wht):
    return env['product.product'].create({
        'name': 'Mini Fan',
        'wht_type_id': acc_wht.id
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
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale'
    })


@pytest.fixture
def partner(env, payment_term, account_receivable, account_payable):
    return env['res.partner'].create({
        'name': 'Your Supplier',
        'email': 'supplier@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
        'company_type': 'company',
        'property_payment_term_id': payment_term.id,
        'property_account_receivable_id': account_receivable.id,
        'property_account_payable_id': account_payable.id
    })


@pytest.fixture
def invoice(
        model,
        product,
        partner,
        journal,
        account_id):
    return model.create({
        'partner_id': partner.id,
        'journal_id': journal.id,
    })


@pytest.fixture
def invoice_full(model,
                 product,
                 partner,
                 journal,
                 acc_wht,
                 mocker,
                 account_id):
    return model.create({
        'partner_id': partner.id,
        'journal_id': journal.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': 500.2,
            'wht_type_id': acc_wht.id,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


def test_create(model,
                product,
                partner,
                journal,
                acc_wht,
                mocker,
                account_id):
    map_invoice_line = mocker.spy(type(model),
                                  'map_invoice_line')
    data = {
        'partner_id': partner.id,
        'journal_id': journal.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'wht_type_id': acc_wht.id,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    }
    invoice = model.create(data)
    map_invoice_line.assert_any_call(
        model,
        data
    )
    assert invoice.invoice_line_ids.wht_type_id == acc_wht


def test_write(model,
               invoice,
               product,
               partner,
               journal,
               acc_wht,
               mocker,
               account_id):
    map_invoice_line = mocker.spy(type(model),
                                  'map_invoice_line')
    data = {'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'quantity': 2,
                'price_unit': product.lst_price,
                'account_id': product.property_account_income_id.id if
                product.property_account_income_id.id else account_id.id
            })],
            }
    invoice.write(data)
    map_invoice_line.assert_any_call(
        invoice,
        data
    )


def test_map_invoice_line(invoice, acc_wht):
    data = {
        'invoice_line_ids': [[0, 'virtual_372',
                              {'name': 'product1', 'wht_type_id': acc_wht.id}
                              ]],
        'line_ids': [[0, 'virtual_372', {'name': 'product1'}]],
    }
    expected = {'invoice_line_ids': [
        [0, 'virtual_372',
         {'name': 'product1',
          'wht_type_id': acc_wht.id}]
    ],
        'line_ids': [
        [0, 'virtual_372',
         {'name': 'product1',
          'wht_type_id': acc_wht.id}]
    ]}
    res = invoice.map_invoice_line(data)
    assert res == expected


def test__compute_wht_amount(invoice_full):
    invoice_full._compute_wht_amount()
    assert invoice_full.amount_wht == 35.01


@pytest.mark.parametrize('test_input, expected', [
    ({'sequence': 5},
     ("You can not select different WHT under the same category."
      " Right now your section 5 or section 6"
      " are under the same category.")),
    ({'sequence': 6},
     ("You can not select different WHT under the same category."
      " Right now your section 5 or section 6"
      " are under the same category.")),
    ({'sequence': 0},
        True
     ),
])
def test_action_post(invoice,
                     journal,
                     product,
                     acc_wht,
                     account_id,
                     test_input,
                     expected):
    product2 = product.copy()
    invoice.write({'move_type': 'out_invoice',
                   'invoice_line_ids': [(0, 0, {
                       'product_id': product.id,
                       'name': product.name,
                       'quantity': 10,
                       'wht_type_id': acc_wht.id,
                       'price_unit': product.lst_price,
                       'account_id': product.property_account_income_id.id if
                       product.property_account_income_id.id else account_id.id
                   }), (0, 0, {
                       'product_id': product2.id,
                       'name': product2.name,
                       'quantity': 10,
                       'wht_type_id': acc_wht.id,
                       'price_unit': product2.lst_price,
                       'account_id': product2.property_account_income_id.id if
                       product2.property_account_income_id.id else account_id.id
                   })],
                   })
    if test_input.get('sequence'):
        acc_wht.write({
            'sequence': test_input.get('sequence')
        })
        acc_wht2 = acc_wht.copy({'sequence': test_input.get('sequence')})
        invoice.invoice_line_ids[0].write({
            'wht_type_id': acc_wht2.id
        })
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_post()
            assert excinfo.value.name == expected
    else:
        invoice.write({
            'auto_post': True
        })
        invoice.action_post()
        assert invoice.state == 'posted'

# AccountMoveLine


@ pytest.mark.parametrize('test_input, expected', [
    ({'move_type': 'in_invoice', 'type': 'purchase'}, 'in_invoice'),
    ({'move_type': 'out_invoice', 'type': 'sale'}, 'out_invoice'),
])
def test__onchange_product_id(
        invoice,
        journal,
        product,
        acc_wht,
        account_id,
        test_input,
        expected):
    journal.write({'type': test_input['type']})
    invoice.write({'move_type': test_input['move_type'],
                   'invoice_line_ids': [(0, 0, {
                       'product_id': product.id,
                       'name': product.name,
                       'quantity': 10,
                       'price_unit': product.lst_price,
                       'account_id': product.property_account_income_id.id if
                       product.property_account_income_id.id else account_id.id
                   })],
                   })

    invoice.invoice_line_ids._onchange_product_id()
    assert invoice.invoice_line_ids.wht_type_id == acc_wht
    assert invoice.move_type == expected


def test__compute_wht_amount_line(invoice_full, acc_wht, mocker):
    wht_calculator = mocker.spy(type(acc_wht), 'wht_calculator')
    invoice_full.invoice_line_ids._compute_wht_amount()
    wht_calculator.assert_any_call(
        acc_wht,
        invoice_full.invoice_line_ids.price_subtotal
    )
    assert round(invoice_full.invoice_line_ids.amount_wht, 2) == 35.01
