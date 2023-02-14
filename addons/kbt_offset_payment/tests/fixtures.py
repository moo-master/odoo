from pytest_tr_odoo.fixtures import env
import pytest

from odoo import fields


@pytest.fixture
def partner(env):
    return env.ref('base.res_partner_1')


@pytest.fixture
def product(env):
    return env.ref('product.product_product_1')


@pytest.fixture
def currency_thb(env):
    return env.ref('base.THB')


@pytest.fixture
def main_company(env):
    return env.ref('base.main_company')


@pytest.fixture
def account_type_receivable(env):
    return env.ref('account.data_account_type_receivable')


@pytest.fixture
def account_type_payable(env):
    return env.ref('account.data_account_type_payable')


@pytest.fixture
def account_type_credit_card(env):
    return env.ref('account.data_account_type_credit_card')


@pytest.fixture
def account_type_current_assets(env):
    return env.ref('account.data_account_type_current_assets')


@pytest.fixture
def account_type_non_current_assets(env):
    return env.ref('account.data_account_type_non_current_assets')


@pytest.fixture
def account_type_non_current_assets(env):
    return env.ref('account.data_account_type_non_current_assets')


@pytest.fixture
def account_type_liquidity(env):
    return env.ref('account.data_account_type_liquidity')


@pytest.fixture
def account_type_other_income(env):
    return env.ref('account.data_account_type_other_income')


@pytest.fixture
def account_type_demo(env):
    return env['account.account.type'].create({
        'name': 'Test Type',
        'type': 'other',
        'internal_group': 'income',
    })


@pytest.fixture
def account_id(env, account_type_demo):
    return env['account.account'].create({
        'code': '1',
        'name': 'Test Account',
        'user_type_id': account_type_demo.id
    })


@pytest.fixture
def account_pnd3_id(env, account_type_demo):
    return env['account.account'].create({
        'code': '2',
        'name': 'Test Account',
        'user_type_id': account_type_demo.id
    })


@pytest.fixture
def account_pnd53_id(env, account_type_demo):
    return env['account.account'].create({
        'code': '3',
        'name': 'Test Account',
        'user_type_id': account_type_demo.id
    })


@pytest.fixture
def acc_wht(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 0.7,
        'sequence': 5,
    })


@pytest.fixture
def account_account_type(env):
    return env['account.account.type'].create({
        'name': 'credit2',
        'type': 'other',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account_type2(env):
    return env['account.account.type'].create({
        'name': 'Income',
        'type': 'in',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account(env, account_account_type):
    return env['account.account'].create({
        'name': 'Account Demo',
        'user_type_id': account_account_type.id,
        'code': '0000000',
    })


@pytest.fixture
def account_account2(env):
    return env['account.account'].create({
        'name': 'Account Demo2',
        'user_type_id': env.ref('account.data_account_type_revenue').id,
        'code': '00000002',
    })


@pytest.fixture
def account_journal(env, account_account2):
    return env['account.journal'].create({
        'name': 'Bangkok',
        'code': 'BNK',
        'type': 'bank',
        'default_account_id': account_account2.id,
        'company_id': env.company.id,
    })


@pytest.fixture
def invoice(env, product, partner, acc_wht):
    invoice = env['account.move'].create({
        'name': 'invoice_test',
        'partner_id': partner.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 1000,
            'wht_type_id': acc_wht.id,
        })],
    })
    invoice.action_post()
    return invoice


@pytest.fixture
def bill(env, product, partner,):
    bill = env['account.move'].create({
        'name': 'bill_test',
        'partner_id': partner.id,
        'move_type': 'in_invoice',
        'invoice_date': fields.Date.today(),
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 500,
        })],
    })
    bill.action_post()
    return bill
