import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['beecy.account.payment']


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'general',
        'currency_id': env.company.currency_id.id,
    })


@pytest.fixture
def journal_cash(env):
    return env['account.journal'].search([
        ('type', '=', 'cash'),
        ('company_id', '=', env.company.id)], limit=1)


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
def account_suspense(env, account_type):
    return env['account.account'].create({
        'code': '3000',
        'name': 'Test Suspense Account',
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
def partner(env):
    partner = env.ref('base.partner_demo')
    return partner


@pytest.fixture
def product(env):
    product = env.ref('product.product_order_01')
    return product


@pytest.fixture
def wht3(env):
    return env['account.wht.type'].create({
        'display_name': 'Wht 3%',
        'percent': 3.0,
    })


@pytest.fixture
def tax_input(env, account_suspense):
    return env['account.tax'].create({
        'name': 'Input VAT 7% (Suspense)',
        'amount_type': 'percent',
        'type_tax_use': 'purchase',
        'amount': 7,
        'tax_exigibility': 'on_payment',
        'cash_basis_transition_account_id': account_suspense.id
    })


@pytest.fixture
def journal_sale(env):
    return env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', env.company.id)], limit=1)


@pytest.fixture
def payment_term_30days(env):
    payment_term = env.ref('account.account_payment_term_30days')
    return payment_term


@pytest.fixture
def customer_payment(env, model, partner, journal_cash,
                     journal_sale, product, payment_term_30days, tax_input,
                     wht3):
    acc_m = env['account.move'].create({
        'partner_id': partner.id,
        'invoice_payment_term_id': payment_term_30days.id,
        'journal_id': journal_sale.id,
        'tax_id': tax_input.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'price_unit': 100,
            'wht_type_id': wht3.id,
        })],
    })
    acc_payment = model.create({
        'payment_type': 'outbound',
        'partner_id': partner.id,
        'date_date': "2022-04-26",
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'vat_date': "2022-04-26",
        'payment_line_invoice_ids': [(0, 0, {
            'invoice_id': acc_m.id,
        })],
        'payment_line_wht_ids': [(0, 0, {
            'amount_wht': 10
        })],
    })
    return acc_payment


@pytest.mark.parametrize(
    'test_input,expected',
    [({'payment_type': 'outbound',
       'method_manual': 'account.account_payment_method_manual_out'},
      'outbound'),
     ({'payment_type': 'inbound',
       'method_manual': 'account.account_payment_method_manual_in'},
        'inbound'),
     ])
def test_onchange_create_temp_journal_item(env,
                                           model,
                                           customer_payment,
                                           test_input, expected,
                                           account_id,
                                           journal):
    payment_method = env.ref(test_input.get('method_manual'))
    acc_payment_method = env['account.payment.method.line'].create({
        'payment_method_id': payment_method.id,
        'payment_account_id': account_id.id,
        'journal_id': journal.id
    })
    customer_payment.write({
        'payment_type': test_input.get('payment_type'),
        'payment_line_method_ids': [(0, 0, {
            'payment_method_line_id': acc_payment_method.id,
            'amount_total': 5
        })]
    })
    customer_payment._onchange_create_temp_journal_item()
    assert customer_payment.payment_type == expected
    assert len(customer_payment.mapped('temp_journal_ids').ids) == 5


def test_create_account_move_entry(
        model,
        env,
        mocker,
        customer_payment,
        journal_cash,
        partner,
        account_id):
    spy_create_account_move_entry = mocker.spy(
        type(customer_payment), 'create_account_move_entry')
    acc_payment = model.create({
        'payment_type': 'outbound',
        'partner_id': partner.id,
        'date_date': "2022-04-26",
        'journal_id': journal_cash.id,
        'company_id': env.company.id,
        'vat_date': "2022-04-26",
        'temp_journal_ids': [(0, 0, {
            'account_id': account_id.id,
            'name': 'Test credit',
            'credit': 100,
            'debit': 0,
        }),
            (0, 0, {
                'account_id': account_id.id,
                'name': 'Test debit',
                'credit': 0,
                'debit': 100,
            })]
    })
    acc_payment.action_confirm()
    acc_payment.company_id.beecy_account_payment_vendor_steps = 'one_step'
    acc_payment.action_validate()
    assert spy_create_account_move_entry.called
