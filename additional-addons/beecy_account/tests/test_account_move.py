from datetime import datetime
from odoo import fields
from pytest_tr_odoo.fixtures import env
import pytest


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


def test__domain_reason_id(env, model):
    res = model._domain_reason_id()
    ir_model = env['ir.model'].search([
        ('model', '=', 'account.move')
    ])
    expected = ['|', ('model_ids', '=', ir_model.id),
                ('model_ids', '=', False)]
    assert res == expected


@pytest.fixture
def account_account_type(env):
    return env['account.account.type'].create({
        'name': 'credit',
        'type': 'liquidity',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account(env, account_account_type):
    return env['account.account'].create({
        'name': 'acc acc',
        'user_type_id': account_account_type.id,
        'code': '01',
    })


@pytest.fixture
def account_journal(env, account_account):
    return env['account.journal'].create({
        'name': "acc journal",
        'type': 'sale',
        'code': "abc",
        'default_account_id': account_account.id,
    })


def test_compute_credit_debit_note_count(model, account_journal):
    acc_move_ref = model.create({
        'journal_id': account_journal.id,
    })
    acc_move = model.create({
        'journal_id': account_journal.id,
        'credit_note_ids': [(0, 0, {
            'invoice_ref_id': acc_move_ref.id,
            'move_type': 'in_refund',
        })],
    })
    acc_move._compute_credit_debit_note_count()
    assert acc_move.credit_note_count == 1
# ------------------------


@pytest.fixture
def account_account_type_act(env):
    return env['account.account.type'].create({
        'name': 'credit 12',
        'type': 'liquidity',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account_act(env, account_account_type_act):
    return env['account.account'].create({
        'name': 'acc acc 12',
        'user_type_id': account_account_type_act.id,
        'code': '01',
    })


@pytest.fixture
def account_journal_act(env, account_account_act):
    return env['account.journal'].create({
        'name': "acc journal 12",
        'type': 'sale',
        'code': "abc12",
        'default_account_id': account_account_act.id,
    })


@pytest.fixture
def account_journal_act2(env, account_account_act):
    return env['account.journal'].create({
        'name': "acc journal 321",
        'type': 'purchase',
        'code': "abc1898",
        'default_account_id': account_account_act.id,
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
def credit_invoice(
        model,
        product,
        partner,
        journal,
        account_id):
    return model.create({
        "name": "/",
        "partner_id": partner.id,
        "move_type": "out_refund",
        "journal_id": journal.id,
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
def debit_invoice(
        model,
        product,
        partner,
        journal,
        account_id):
    return model.create({
        "name": "/",
        "partner_id": partner.id,
        "move_type": "out_debit",
        "journal_id": journal.id,
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': 0.0,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'out_invoice', }, 'out_refund'),
    ({'move_type': 'in_invoice', }, 'in_refund'),
])
def test_action_reverse(
        model,
        product,
        partner,
        account_id,
        test_input,
        expected):
    invoice = model.create({
        "partner_id": partner.id,
        "move_type": test_input['move_type'],
        "invoice_line_ids": [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 10,
            'price_unit': product.lst_price,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id
        })],
    })
    res = invoice.action_reverse()
    assert res['context']['move_type'] == expected
    assert res['context']['model_name'] == 'account.move'


@pytest.mark.parametrize('test_input', [
    ({'acc_type': 'credit',
      'move_type': 'in_invoice'}),
    ({'acc_type': 'credit',
      'move_type': 'out_invoice'}),
    ({'acc_type': 'debit',
      'move_type': 'in_invoice'}),
    ({'acc_type': 'debit',
      'move_type': 'out_invoice'}),
    ({'acc_type': '',
      'move_type': 'out_invoice'}),
])
def test_action_credit_debit_note_view(
        model,
        account_journal_act,
        account_journal_act2,
        test_input):
    acc_move = model.create({
        'journal_id': account_journal_act.id if test_input['move_type'] == 'out_invoice' else account_journal_act2.id,
        'move_type': test_input['move_type']
    })

    wizard = acc_move.with_context(
        account_type=test_input['acc_type']).action_credit_debit_note_view()
    assert wizard


@pytest.mark.parametrize('test_input,expected', [
    ({'type': 'out_invoice'}, 'out_debit'),
    ({'type': 'in_invoice'}, 'in_debit'),
])
def test_action_debit_note_reason_wizard(model, test_input, expected):
    invoice = model.create({
        'move_type': test_input['type'],
    })
    wizard = invoice.action_debit_note_reason_wizard()
    assert wizard['context'].get('move_type') == expected


def test_action_approve(invoice, monkeypatch, mocker,):
    spy_approve = mocker.spy(type(invoice), 'action_approve')
    invoice.action_approve()
    assert invoice.approve_uid == invoice.env.user
    assert invoice.approve_date == datetime.utcnow().date()
    spy_approve.assert_called_once_with(
        invoice
    )


def test_action_reject_reason(invoice):
    res = invoice.action_reject_reason()
    assert invoice.reject_uid == invoice.env.user
    assert invoice.reject_date == datetime.utcnow().date()
    assert res


@pytest.mark.parametrize('test_input,expected', [
    ({'user_has_groups': True}, 'posted'),
    ({'user_has_groups': False}, 'to_approve'),
])
def test_action_to_approve(
        invoice,
        monkeypatch,
        test_input,
        expected):
    monkeypatch.setattr(type(invoice), 'user_has_groups',
                        lambda a, b: test_input.get('user_has_groups'))
    invoice.action_to_approve()
    assert invoice.state == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'user_has_groups': True}, 'posted'),
    ({'user_has_groups': False}, 'to_approve'),
])
def test_action_to_approve_credit_note(
        credit_invoice,
        monkeypatch,
        test_input,
        expected):
    monkeypatch.setattr(type(credit_invoice), 'user_has_groups',
                        lambda a, b: test_input.get('user_has_groups'))
    credit_invoice.action_to_approve()
    assert credit_invoice.state == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'user_has_groups': True}, 'posted'),
    ({'user_has_groups': False}, 'to_approve'),
])
def test_action_to_approve_debit_note(
        debit_invoice,
        monkeypatch,
        test_input,
        expected):
    monkeypatch.setattr(type(debit_invoice), 'user_has_groups',
                        lambda a, b: test_input.get('user_has_groups'))
    debit_invoice.action_to_approve()
    assert debit_invoice.state == expected


def test__compute_show_reset_to_draft_button(invoice):
    invoice.write({
        'state': 'reject'
    })
    invoice._compute_show_reset_to_draft_button()
    assert invoice.show_reset_to_draft_button


def test_action_cancel_reject_reason_wizard(invoice):
    view = invoice.env.ref('beecy_reason.view_cancel_reject_reason_form')
    res = invoice.action_cancel_reject_reason_wizard()
    expected = {
        'name': 'Reject Invoice',
        'view_mode': 'form',
        'res_model': 'cancel.reject.reason',
        'view_id': view.id,
        'type': 'ir.actions.act_window',
        'context': {
            'move_type': 'out_invoice',
            'model_name': 'account.move',
            'state': 'reject'},
        'target': 'new'}
    assert res == expected


def test_amount_total_text(invoice):
    th_bath = invoice._amount_total_text(invoice.amount_total_signed)
    assert th_bath == 'สิบบาทถ้วน'


@pytest.mark.parametrize('test_input', [
    ({'view_tree': "account.view_out_invoice_tree",
      'default_move_type': "out_invoice"}),
    ({'view_tree': "account.view_out_credit_note_tree",
      'default_move_type': "out_refund"}),
    ({'view_tree': "beecy_account.debit_inherit_view_invoice_tree",
      'default_move_type': "out_debit"}),
    ({'view_tree': "account.view_in_invoice_bill_tree",
      'default_move_type': "in_invoice"}),
    ({'view_tree': "account.view_in_invoice_refund_tree",
      'default_move_type': "in_refund"}),
    ({'view_tree': "beecy_account.debit_inherit_view_invoice_tree",
      'default_move_type': "in_debit"}),
])
def test_fields_view_get(env, model, test_input, monkeypatch, mocker):
    invoice_tree = env.ref(test_input['view_tree'])
    report_credit = env.ref(
        'beecy_account.action_credit_note_report')
    report_debit = env.ref(
        'beecy_account.action_debit_note_report')
    report_tax_invoice = env.ref(
        'beecy_account.action_tax_invoice_billing_note_report')
    report_invoice_billing = env.ref(
        'beecy_account.action_invoice_billing_billing_note_report')
    report_invoice_delivery = env.ref(
        'beecy_account.action_tax_invoice_delivery_report')
    report_billing_delivery = env.ref(
        'beecy_account.action_invoice_billing_delivery_report')

    data_report = []
    spy_prepare_data_report = mocker.spy(type(model), 'prepare_data_report')
    view_infos_invoice = model.with_context(
        default_move_type=test_input['default_move_type']).fields_view_get(
        view_id=invoice_tree.id,
        toolbar=True
    )

    if view_infos_invoice['toolbar']:
        spy_prepare_data_report.assert_called_once_with(
            model, test_input['default_move_type'])
        for report in view_infos_invoice['toolbar']['print']:
            data_report.append(report['id'])
            if test_input['view_tree'] == "account.view_out_invoice_tree":
                assert report_debit.id not in data_report
                assert report_credit.id not in data_report
            elif test_input[
                    'view_tree'] == "account.view_out_credit_note_tree":
                assert report_debit.id not in data_report
                assert report_tax_invoice.id not in data_report
                assert report_invoice_billing.id not in data_report
                assert report_invoice_delivery.id not in data_report
                assert report_billing_delivery.id not in data_report
            elif test_input[
                    'view_tree'] == "account.view_in_invoice_bill_tree":
                assert report_debit.id not in data_report
                assert report_credit.id not in data_report
            elif test_input[
                    'view_tree'] == "account.view_in_invoice_refund_tree":
                assert report_debit.id not in data_report
                assert report_tax_invoice.id not in data_report
                assert report_invoice_billing.id not in data_report
                assert report_invoice_delivery.id not in data_report
                assert report_billing_delivery.id not in data_report
            elif test_input[
                'view_tree'
            ] == "beecy_account.debit_inherit_view_invoice_tree":
                assert report_credit.id not in data_report
                assert report_tax_invoice.id not in data_report
                assert report_invoice_billing.id not in data_report
                assert report_invoice_delivery.id not in data_report
                assert report_billing_delivery.id not in data_report
            else:
                assert report_credit.id not in data_report
                assert report_tax_invoice.id not in data_report
                assert report_invoice_billing.id not in data_report
                assert report_invoice_delivery.id not in data_report
                assert report_billing_delivery.id not in data_report


@pytest.mark.parametrize('test_input,expected', [
    ({'default_move_type': "out_invoice"},
     ["beecy_account.action_credit_note_report",
      "beecy_account.action_debit_note_report"]
     ),
    ({'default_move_type': "out_refund"},
     [
        'beecy_account.action_tax_invoice_billing_note_report',
        'beecy_account.action_invoice_billing_billing_note_report',
        'beecy_account.action_tax_invoice_delivery_report',
        'beecy_account.action_invoice_billing_delivery_report',
        'beecy_account.action_debit_note_report'
    ]
    ),
    ({'default_move_type': "out_debit"},
     [
        'beecy_account.action_tax_invoice_billing_note_report',
        'beecy_account.action_invoice_billing_billing_note_report',
        'beecy_account.action_tax_invoice_delivery_report',
        'beecy_account.action_invoice_billing_delivery_report',
        'beecy_account.action_credit_note_report'
    ]
    ),
])
def test_prepare_data_report(
        env,
        model,
        test_input,
        expected,
        monkeypatch,
        mocker):
    data_report = []
    spy_prepare_data_invoice_report = mocker.spy(
        type(model), 'prepare_data_invoice_report')
    spy_prepare_data_credit_report = mocker.spy(
        type(model), 'prepare_data_credit_report')
    spy_prepare_data_debit_report = mocker.spy(
        type(model), 'prepare_data_debit_report')
    default_move_type = test_input['default_move_type']
    view_report = model.prepare_data_report(default_move_type)
    for report in expected:
        data_report.append(env.ref(report).id)
    if test_input['default_move_type'] == "out_invoice":
        spy_prepare_data_invoice_report.assert_called_once_with(model)
    if test_input['default_move_type'] == "out_refund":
        spy_prepare_data_credit_report.assert_called_once_with(model)
    if test_input['default_move_type'] == "out_debit":
        spy_prepare_data_debit_report.assert_called_once_with(
            model, view_report)
    assert data_report == view_report


@pytest.mark.parametrize('test_input,expected', [
    ({'view_tree': "account.view_out_invoice_tree"},
     ["beecy_account.action_credit_note_report",
      "beecy_account.action_debit_note_report"]
     ),
])
def test_prepare_data_invoice_report(env, model, test_input, expected,):
    data_report = []
    report_data = model.prepare_data_invoice_report()
    for report in expected:
        data_report.append(env.ref(report).id)
    assert report_data == data_report


@pytest.mark.parametrize('test_input,expected', [
    ({'view_tree': "account.view_out_invoice_tree"},
     [
        'beecy_account.action_tax_invoice_billing_note_report',
        'beecy_account.action_invoice_billing_billing_note_report',
        'beecy_account.action_tax_invoice_delivery_report',
        'beecy_account.action_invoice_billing_delivery_report',
        'beecy_account.action_debit_note_report'
    ]
    ),
])
def test_prepare_data_credit_report(env, model, test_input, expected,):
    data_report = []
    report_data = model.prepare_data_credit_report()
    for report in expected:
        data_report.append(env.ref(report).id)
    assert report_data == data_report


@pytest.mark.parametrize('test_input,expected', [
    ({'view_tree': "account.view_out_invoice_tree"},
     [
        'beecy_account.action_tax_invoice_billing_note_report',
        'beecy_account.action_invoice_billing_billing_note_report',
        'beecy_account.action_tax_invoice_delivery_report',
        'beecy_account.action_invoice_billing_delivery_report',
        'beecy_account.action_credit_note_report'
    ]
    ),
])
def test_prepare_data_debit_report(env, model, test_input, expected,):
    data_report = []
    prepar_data_report = model.prepare_data_credit_report()
    report_data = model.prepare_data_debit_report(prepar_data_report)
    for report in expected:
        data_report.append(env.ref(report).id)
    assert report_data == data_report
# ---------------------


@pytest.fixture
def journal(env):
    return env['account.journal'].create({
        'name': 'IB',
        'code': 'IB',
        'type': 'sale',
        'is_debit_note_sequence': True,
        'refund_sequence': True
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
def invoice_2(model, partner, payment_term, journal):
    return model.create({
        'partner_id': partner.id,
        'date': "2022-04-26",
        'invoice_payment_term_id': payment_term.id,
        'journal_id': journal.id,
        'move_type': 'out_debit',
    })


@pytest.fixture
def account_account_type_income(env):
    return env['account.account.type'].create({
        'name': 'Income',
        'type': 'other',
        'include_initial_balance': True,
        'internal_group': 'income',
    })


@pytest.fixture
def account_account_income(env, account_account_type_income):
    return env['account.account'].create({
        'name': 'Income',
        'user_type_id': account_account_type_income.id,
        'code': '410001',
    })


@pytest.fixture
def account_account_type_receivable(env):
    return env['account.account.type'].create({
        'name': 'Receivable',
        'type': 'receivable',
        'include_initial_balance': True,
        'internal_group': 'liability',
    })


@pytest.fixture
def account_account_receivable(env, account_account_type_receivable):
    return env['account.account'].create({
        'name': 'Receivable',
        'user_type_id': account_account_type_receivable.id,
        'code': '2100001',
        'reconcile': True,
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': "out_debit", }, True),
    ({'move_type': "out_invoice", }, True),
    ({'move_type': "in_debit", }, True),
])
def test_compute_amount(env,
                        model,
                        invoice_2,
                        product,
                        tax_output,
                        account_account_receivable,
                        account_account_income,
                        test_input,
                        expected,
                        journal):
    if test_input.get('move_type') in ['out_invoice', 'out_debit']:
        invoice_2.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'quantity': 1,
                'price_unit': 100,
                'tax_ids': tax_output.ids,
                'account_id': account_account_income.id,
            })],
            'line_ids': [(0, 0, {
                'name': '1234',
                'quantity': 1,
                'tax_ids': tax_output.ids,
                'debit': 0.0,
                'credit': 0.0,
                'account_id': account_account_income.id,
            }), (0, 0, {
                'name': '222',
                'quantity': 1,
                'tax_ids': tax_output.ids,
                'debit': 0.0,
                'credit': 0.0,
                'account_id': account_account_receivable.id,
            }),
            ],
            'amount_untaxed': 100,
            'amount_untaxed_signed': 100,
            'amount_total_signed': 107,
        })
    else:
        journal.write({
            'type': 'purchase'
        })
        invoice_2.write({
            'move_type': 'in_debit',
            'journal_id': journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': env.ref('product.product_order_01').id,
                'name': env.ref('product.product_order_01').name,
                'quantity': 1,
                'price_unit': 100,
                'tax_ids': tax_output.ids,
            })],
        })

    invoice_2._compute_amount()
    if test_input.get('move_type') == 'out_debit':
        assert invoice_2.amount_untaxed == 0.0
        assert invoice_2.amount_tax == 0.0
    elif test_input['move_type'] == 'in_debit':
        assert invoice_2.amount_untaxed == 100.0
        assert invoice_2.amount_tax == 7.0
    else:
        assert invoice_2.amount_untaxed == 0.0
        assert invoice_2.amount_tax == 0.0


@pytest.mark.parametrize('test_input,expected', [
    ({'grouping_key': False,
      'recompute_tax_base_amount': False}, True),
    ({'grouping_key': True,
      'recompute_tax_base_amount': False}, True),
    ({'grouping_key': True,
      'recompute_tax_base_amount': True}, True),
    ({'grouping_key': False,
      'recompute_tax_base_amount': True}, True),
])
def test__recompute_tax_lines(
        mocker,
        monkeypatch,
        env,
        model,
        product,
        tax_output,
        account_id,
        test_input,
        expected):
    tax_repartition_line = env.company.account_sale_tax_id.\
        refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax')
    default_account_revenue = env['account.account'].search([
        ('company_id', '=', env.company.id),
        ('user_type_id.type', '=', 'other'),
        ('user_type_id.name', '=', 'Income')
    ], limit=1)

    inv = model.create({
        'partner_id': env.ref('base.partner_admin').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'invoice_payment_term_id': env.ref(
            'account.account_payment_term_end_following_month').id,
        'move_type': 'entry',
        'invoice_date': fields.Date.today(),
        'company_id': env.ref('base.main_company').id,
        'invoice_line_ids': [
            (0, 0, {
                'product_id': product.id,
                'name': product.name,
                'quantity': 1,
                'price_unit': 100,
                'tax_ids': tax_output.ids,
                'account_id': product.property_account_income_id.id if
                product.property_account_income_id.id else account_id.id,
            }),
        ],
    })

    if test_input.get('grouping_key'):
        inv.write({
            'line_ids': [(0, None, {
                'name': 'tax line 1',
                'account_id': default_account_revenue.id,
                'tax_ids': tax_output.ids,
                'debit': 0.0,
                'credit': 0.0,
                'tax_repartition_line_id': tax_repartition_line.id,
            }),
                (0, None, {
                 'name': 'tax line 2',
                 'account_id': default_account_revenue.id,
                 'tax_ids': tax_output.ids,
                 'debit': 0.0,
                 'credit': 0.0,
                 'tax_repartition_line_id': tax_repartition_line.id,
                 })
            ]
        })
    else:
        inv.write({
            'line_ids': [(0, None, {
                'name': 'tax line 1',
                'account_id': default_account_revenue.id,
                'tax_ids': tax_output.ids,
                'debit': 0.0,
                'credit': 0.0,
            }),
                (0, None, {
                 'name': 'tax line 2',
                 'account_id': default_account_revenue.id,
                 'tax_ids': tax_output.ids,
                 'debit': 0.0,
                 'credit': 0.0,
                 })
            ]
        })
    debit = sum(inv.line_ids.mapped('debit'))
    credit = sum(inv.line_ids.mapped('credit'))
    inv._recompute_tax_lines(
        recompute_tax_base_amount=test_input.get('recompute_tax_base_amount'))

    assert debit - credit == 0.0


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


def test_recompute_create_line(env, model):
    tax_repartition_line = env.company.account_sale_tax_id. \
        refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax')
    default_account_revenue = env['account.account'].search([
        ('company_id', '=', env.company.id),
        ('user_type_id.type', '=', 'other'),
        ('user_type_id.name', '=', 'Income')
    ], limit=1)
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
    res = inv.line_ids[0].recompute_create_line([
        {'move_id': inv.id, 'currency_id': env.ref('base.AUD').id}
    ])
    expected = [{'move_id': inv.id,
                 'currency_id': env.ref('base.AUD').id,
                 'company_currency_id':
                     env.ref('base.main_company').currency_id.id,
                 'amount_currency': 0.0}]
    assert res == expected


def test__compute_narration(env, model,
                            product,
                            account_id,
                            tax_output):
    move = model.create({
        'partner_id': env.ref('base.partner_admin').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'company_id': env.company.id,
        'invoice_payment_term_id': env.ref(
            'account.account_payment_term_end_following_month').id,
        'move_type': 'out_invoice',
        'invoice_date': fields.Date.today(),
        'narration': '1234',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id,
        })],
    })
    move._compute_narration()


def test__onchange_invoice_discount(
        env,
        model,
        product,
        account_id,
        tax_output):
    move = model.create({
        'partner_id': env.ref('base.partner_admin').id,
        'invoice_user_id': env.ref('base.user_demo').id,
        'company_id': env.company.id,
        'invoice_payment_term_id': env.ref(
            'account.account_payment_term_end_following_month').id,
        'move_type': 'out_invoice',
        'invoice_date': fields.Date.today(),
        'narration': '1234',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': 100,
            'tax_ids': tax_output.ids,
            'account_id': product.property_account_income_id.id if
            product.property_account_income_id.id else account_id.id,
        })],
    })
    move._onchange_invoice_discount()
    assert True
