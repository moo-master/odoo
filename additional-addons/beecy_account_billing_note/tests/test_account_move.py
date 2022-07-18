import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError


@pytest.fixture
def model(env):
    return env['account.move']


@pytest.fixture
def product(env):
    return env['product.product'].create({
        'name': 'Mini Fan'
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
def partner(env, payment_term, account_receivable, account_payable):
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
def invoice(
        model,
        product,
        partner,
        account_id):
    return model.create({
        "partner_id": partner.id,
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
def billing(env, partner):
    return env['account.billing.note'].create({
        'partner_id': partner.id,
        'bill_date': fields.Date.today(),
        'payment_date': fields.Date.today()
    })


def test__compute_billing_note_count(
        invoice,
        billing,
):
    invoice.state = 'posted'
    billing.write({
        'line_ids': [(0, 0, {'invoice_id': invoice.id})],
    })
    invoice._compute_billing_note_count()

    assert invoice.billing_note_count == 1


@pytest.mark.parametrize('test_input,expected', [
    ({'n': 1}, 1),
    ({'n': 1, 'stock_picking_type_action': True}, 1),
    ({'n': 2}, 2),
    ({'n': 5}, 5),
])
def test_action_billing_note_ids(monkeypatch, env, model, partner,
                                 test_input, expected):
    data = model.with_context(tracking_disable=True).create({
        'partner_id': partner.id,
        'billing_note_ids': [(0, 0, {
            'partner_id': partner.id,
            'payment_date': fields.Date.today(),
        })] * test_input['n'],
    })
    if test_input.get('stock_picking_type_action'):
        action_stock = env.ref('stock.stock_picking_type_action').read()[0]
        del action_stock['views']
        monkeypatch.setattr(
            type(
                env.ref('stock.stock_picking_type_action')),
            'read',
            lambda a: [action_stock])
    res = data.action_billing_note_ids()
    action_billing = 'beecy_account_billing_note.action_billing_note'
    form_billing = 'beecy_account_billing_note.account_billing_note_view_form'
    if expected > 1:
        assert res['id'] == env.ref(action_billing).id
        assert res['domain'] == [('id', 'in', data.billing_note_ids.ids)]
    else:
        assert res['views'][0] == (env.ref(form_billing).id, 'form')
        assert res['res_id'] == data.billing_note_ids[0].id


@pytest.mark.parametrize('test_input,expected',
                         [({'partner': True},
                           ("The billing note should belong to the same customer,"
                             "right now you're selected the invoices that the partner is not the same")),
                             ({'billing_note_ids': True},
                              "The invoices you selected had been billed"),
                             ({'state': True},
                              "There is nothing left to billing on the selected journal items"),
                             ({'billing_notes': True},
                              ("This customer had more than one pending billing note (draft),"
                               " you have to clear the billing note first")),
                             ({'billing_note': True},
                              True),
                             ({'no_billing_note': True},
                              True),
                          ])
def test_action_create_billing_note(
        invoice,
        billing,
        test_input,
        expected):
    invoice2 = invoice.copy()
    form_view_ref = billing.env.ref(
        'beecy_account_billing_note.account_billing_note_view_form', False)
    tree_view_ref = billing.env.ref(
        'beecy_account_billing_note.account_billing_note_view_tree', False)
    if test_input.get('partner'):
        partner2 = invoice2.partner_id.copy()
        invoice2.partner_id = partner2
        invoice += invoice2
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_create_billing_note()
            assert excinfo.value.name == expected
    elif test_input.get('billing_note_ids'):
        invoice.write({
            'billing_note_ids': [(4, billing.id)]
        })
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_create_billing_note()
            assert excinfo.value.name == expected
    elif test_input.get('billing_note_ids'):
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_create_billing_note()
            assert excinfo.value.name == expected
    elif test_input.get('state'):
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_create_billing_note()
            assert excinfo.value.name == expected
    elif test_input.get('billing_notes'):
        billing.copy()
        invoice.state = 'posted'
        invoice.payment_state = 'not_paid'
        with pytest.raises(ValidationError) as excinfo:
            invoice.action_create_billing_note()
            assert excinfo.value.name == expected
    elif test_input.get('billing_note'):
        invoice.state = 'posted'
        invoice.payment_state = 'not_paid'
        billing.state = 'draft'
        res = invoice.action_create_billing_note()
        assert billing.line_ids
        if expected:
            assert res == {
                'domain': [('id', 'in', [billing.id])],
                'name': 'Billing Note',
                'res_model': 'account.billing.note',
                'type': 'ir.actions.act_window',
                'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
                'context': {'active_id': billing.id, 'active_model': 'account.billing.note'}
            }
    elif test_input.get('no_billing_note'):
        invoice.state = 'posted'
        invoice.payment_state = 'not_paid'
        billing.state = 'bill'
        res = invoice.action_create_billing_note()
        billing = invoice.billing_note_ids
        if expected:
            assert res == {
                'domain': [('id', 'in', [billing.id])],
                'name': 'Billing Note',
                'res_model': 'account.billing.note',
                'type': 'ir.actions.act_window',
                'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
                'context': {'active_id': billing.id, 'active_model': 'account.billing.note'}
            }
