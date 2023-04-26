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
def test__prepare_move_line_default_vals(
        env,
        model,
        invoice,
        test_input,
        expected,
        account_id,
        account_pnd3_id,
        account_pnd53_id,
        partner_demo):
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

    payment = model.new({
        'amount': 100,
        'move_wht_ids': [(6, 0, invoice.ids)]
    })
    res = payment._prepare_move_line_default_vals()

    liquidity_line, _, liquidity_wht_line = res
    expected_res = {
        1: account_id,
        2: account_pnd3_id,
        3: account_pnd53_id,
    }
    type_val = 'debit' if payment.payment_type == 'inbound' else 'credit'
    assert liquidity_wht_line['account_id'] == expected_res[expected].id
    assert liquidity_wht_line[type_val] == invoice.amount_wht
    assert liquidity_line[type_val] == payment.amount - invoice.amount_wht
