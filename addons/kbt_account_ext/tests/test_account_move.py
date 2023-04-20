from pytest_tr_odoo.fixtures import env
import pytest


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
def invoice(model,
            product,
            partner,
            journal,
            acc_wht,
            mocker,
            account_id):
    invoice = model.create({
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
    invoice.action_post()
    return invoice


@pytest.fixture
def credit_note(env, model, invoice):
    move_reversal = env['account.move.reversal']\
        .with_context(active_model="account.move", active_ids=invoice.ids)\
        .create({
                'journal_id': invoice.journal_id.id,
                'reason': "no reason",
                'refund_method': 'cancel',
                })
    reversal = move_reversal.reverse_moves()
    credit_note = env['account.move'].browse(reversal['res_id'])
    return credit_note


def test__compute_old_invoice_amount(env, model, invoice, credit_note):
    credit_note.write({
        'x_real_amount': 100
    })
    credit_note._compute_old_invoice_amount()
    assert credit_note.x_old_invoice_amount == invoice.amount_untaxed
    assert credit_note.x_diff_amount == \
        invoice.amount_untaxed - credit_note.x_real_amount
    assert credit_note.x_wht_amount == invoice.amount_wht


def test__onchange_x_real_amount(env, model, invoice, credit_note):
    credit_note.write({
        'x_real_amount': 100,
    })
    credit_note._onchange_x_real_amount()
    assert credit_note.x_diff_amount == \
        invoice.amount_untaxed - credit_note.x_real_amount


def test_get_amount_total_text(model):
    move_id = model.new({
        'amount_total': 1234.50,
    })
    res = move_id.get_amount_total_text(move_id.amount_total)
    assert res == 'หนึ่งพันสองร้อยสามสิบสี่บาทห้าสิบสตางค์'


def test_remove_menu_print(model, env):
    report = env.ref(
        'kbt_account_ext.action_kbt_debit_note_report',
        raise_if_not_found=False
    )
    res = model.remove_menu_print(
        {'toolbar': {'print': [{'id': 1}, {'id': report.id}]}},
        ['kbt_account_ext.action_kbt_debit_note_report']
    )
    assert res == {'toolbar': {'print': [{'id': 1}]}}


@pytest.mark.parametrize('test_input,expected', [
    (
        {'move_type': 'out_invoice', 'view_type': 'kanban'},
        None
    ),
    (
        {'move_type': 'other', 'view_type': 'tree'},
        None
    ),
    (
        {'move_type': 'out_invoice', 'view_type': 'tree'},
        [
            'kbt_account_ext.action_kbt_debit_note_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
    ),
    (
        {'move_type': 'out_refund', 'view_type': 'tree'},
        [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
    ),
    (
        {'move_type': 'in_refund', 'view_type': 'tree'},
        [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_debit_note_report',
        ]
    ),
    (
        {'move_type': 'in_invoice', 'view_type': 'tree'},
        [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_debit_note_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
    ),
])
def test_fields_view_get(monkeypatch, mocker, model,
                         test_input, expected):
    monkeypatch.setattr(
        type(model),
        'remove_menu_print',
        lambda *args, **kwargs: True
    )
    spy_remove_menu_print = mocker.spy(type(model), 'remove_menu_print')
    model.with_context(
        default_move_type=test_input['move_type']
    ).fields_view_get(
        view_type=test_input['view_type']
    )
    if expected is None:
        assert spy_remove_menu_print.call_count == 0
    else:
        assert spy_remove_menu_print.call_count == 1
        assert spy_remove_menu_print.call_args.args[-1] == expected
