from pytest_tr_odoo.fixtures import env
import pytest
from odoo import fields


@pytest.fixture
def model(env):
    return env['account.payment.register']


@pytest.fixture
def product(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def partner_demo(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
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
        'code': '1',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_pnd3_id(env, account_type):
    return env['account.account'].create({
        'code': '2',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_pnd53_id(env, account_type):
    return env['account.account'].create({
        'code': '3',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def partner_bank(env, partner_demo):
    return env['res.partner.bank'].create({
        'bank_name': 'Partner',
        'acc_number': 1234,
        'partner_id': partner_demo.id,
    })


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'JV Sale',
        'type': 'sale',
        'code': 'SO',
        'company_id': env.company.id,
    })


@pytest.fixture
def invoice(env, partner_demo, product, account_id, wht3):
    inv = env['account.move'].create({
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_date': '2022-01-01',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 1000,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id,
            'wht_type_id': wht3.id,
        })],
    })
    return inv


@pytest.mark.parametrize('test_input, expected',
                         [({'move_type': 'out_invoice',
                            'company_type': 'person',
                            'journal_type': 'sale'},
                           1),
                          ({'move_type': 'in_invoice',
                            'company_type': 'person',
                            'journal_type': 'purchase'},
                             2),
                             ({'move_type': 'in_invoice',
                               'company_type': 'company',
                               'journal_type': 'purchase'},
                              3),
                          ])
def test_create(
        env,
        model,
        invoice,
        partner_demo,
        partner_bank,
        wht3,
        test_input,
        account_id,
        account_pnd3_id,
        account_pnd53_id,
        journal,
        expected):
    partner_demo.company_id.write({
        'ap_wht_default_account_pnd3_id': account_pnd3_id.id,
        'ap_wht_default_account_pnd53_id': account_pnd53_id.id,
        'ar_wht_default_account_id': account_id.id,
    })
    partner_demo.write({
        'company_type': test_input['company_type']
    })
    invoice.journal_id.write({
        'type': test_input['journal_type']
    })

    invoice.write({
        'move_type': test_input['move_type']
    })
    invoice.action_post()

    res_action = invoice.action_register_payment()
    ctx = res_action.get('context')
    val = {
        'payment_type': 'inbound'
        if test_input['move_type'] == 'out_invoice' else 'outbound',
        'journal_id': journal.id,
        'amount': 100,
        'payment_date': '2022-08-01',
        'partner_bank_id': partner_bank.id,
        'payment_method_line_id': 1,
        'payment_difference_handling': 'open',
        'writeoff_account_id': False
    }
    wizard_id = model.with_context(
        active_model=ctx['active_model'],
        active_ids=ctx['active_ids']).create(val)
    wizard_id._create_payments()

    wht = env['account.wht'].search([])
    res_expected = {
        1: account_id.id,
        2: account_pnd3_id.id,
        3: account_pnd53_id.id,
    }
    assert wht.account_id.id == res_expected[expected]


def test__compute_amount(
        env,
        model,
        invoice,
        wht3,
        journal,
        partner_bank):
    invoice.action_post()
    res_action = invoice.action_register_payment()
    ctx = res_action.get('context')
    val = {
        'payment_type': 'inbound',
        'journal_id': journal.id,
        'amount': 100,
        'payment_date': '2022-08-01',
        'partner_bank_id': partner_bank.id,
        'payment_difference_handling': 'open',
        'writeoff_account_id': False
    }
    wizard_id = model.with_context(
        active_model=ctx['active_model'],
        active_ids=ctx['active_ids']).create(val)
    wizard_id._compute_amount()

    assert wizard_id.amount == invoice.amount_residual - invoice.amount_wht
