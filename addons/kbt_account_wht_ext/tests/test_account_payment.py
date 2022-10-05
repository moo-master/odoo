from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.payment']


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
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_pnd3_id(env, account_type):
    return env['account.account'].create({
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def account_pnd53_id(env, account_type):
    return env['account.account'].create({
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def partner_bank(env, partner_demo, account_id):
    return env['res.partner.bank'].create({
        'bank_name': 'Partner',
        'acc_number': 1234,
        'partner_id': partner_demo.id,
        # 'account_id': account_id.id,
    })


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'JV Sale',
        'type': 'sale',
        'code': 'JV-SO',
        'company_id': env.company.id,
    })


@pytest.fixture
def invoice(env, partner_demo, product, account_id):
    inv = env['account.move'].create({
        'partner_id': partner_demo.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 1000,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id,
        })],
    })
    inv.action_post()
    return inv


def test_create(
        env,
        model,
        invoice,
        partner_demo,
        partner_bank,
        wht3,
        journal):
    res_action = invoice.action_register_payment()
    ctx = res_action.get('context')
    val = {
        'payment_type': 'inbound',
        'journal_id': journal.id,
        'amount': 100,
        'payment_date': '2022-08-01',
        'partner_bank_id': partner_bank.id,
        'payment_method_line_id': 1,
        'payment_difference_handling': 'open',
        'writeoff_account_id': False
    }
    wizard_id = env['account.payment.register'].with_context(
        active_model=ctx['active_model'],
        active_ids=ctx['active_ids']).create(val)
    res = wizard_id.action_create_payments()
    payment_id = env['account.payment'].browse([res['res_id']])
    assert payment_id
