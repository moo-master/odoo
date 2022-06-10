import pytest
from pytest_tr_odoo.fixtures import env
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import _


@pytest.fixture
def model(env):
    return env['account.cheque']


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
def vendor_cheque_journal(env):
    return env['account.journal'].create({
        'name': 'Vender',
        'code': 'IB1',
        'type': 'sale'
    })


@pytest.fixture
def customer_cheque_journal(env, account_id):
    return env['account.journal'].create({
        'name': 'Customer',
        'code': 'IB2',
        'type': 'purchase',
        'suspense_account_id': account_id.id,
    })


@pytest.fixture
def cheque_journal_bank(env, account_id):
    return env['account.journal'].create({
        'name': 'Customer',
        'code': 'IB2',
        'type': 'bank',
        'suspense_account_id': account_id.id,
    })


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Partner',
    })


@pytest.fixture
def partner_bank(env, partner, account_id):
    return env['res.partner.bank'].create({
        'bank_name': 'Partner',
        'acc_number': 1234,
        'partner_id': partner.id,
        'account_id': account_id.id,
    })


@pytest.fixture
def cheque(model, partner):
    return model.create({
        'partner_id': partner.id,
        'amount': 100,
    })


@pytest.fixture
def company(env, vendor_cheque_journal, customer_cheque_journal):
    return env['res.company'].create({
        'name': 'Limited',
        'default_vendor_cheque_journal_id': vendor_cheque_journal.id,
        'default_customer_cheque_journal_id': customer_cheque_journal.id,
    })


def test_onchange_partner_id(cheque):
    cheque._onchange_partner_id()
    assert not cheque.pay_id


@pytest.mark.parametrize('test_input', [
    ({'type': 'vendor'}),
    ({'type': 'customer'}),
])
def test__default_get_journal(
        model,
        company,
        vendor_cheque_journal,
        customer_cheque_journal,
        test_input):
    model.env.company.update({
        'default_vendor_cheque_journal_id': vendor_cheque_journal.id,
        'default_customer_cheque_journal_id': customer_cheque_journal.id,
    })
    res = model.with_context(default_type=test_input['type']).new({})
    if test_input['type'] == 'customer':
        assert res.journal_id == customer_cheque_journal
    else:
        assert res.journal_id == vendor_cheque_journal


@pytest.mark.parametrize('test_input, expected',
                         [({'type': 'vendor'},
                           [('draft', 'Draft'),
                             ('to_approve', 'To Approve'),
                             ('to_deposit', 'To Deposit'),
                             ('deposit', 'Deposit'),
                             ('close', 'Close'),
                             ('cancel', 'Cancel'),
                             ('reject', 'Reject')
                            ]), ({'type': 'customer'},
                                 [('draft', 'Draft'),
                                  ('to_deposit', 'To Deposit'),
                                  ('deposit', 'Deposit'),
                                  ('close', 'Close'),
                                  ('cancel', 'Cancel'),
                                  ('reject', 'Reject')
                                  ]),
                          ])
def test__state_selection(model, test_input, expected):
    res = model.with_context(default_type=test_input['type']).new({})
    field = res._fields['state']._description_selection(res.env)
    assert field == expected


@pytest.mark.parametrize('expected', [
                         ('to_deposit')
                         ])
def test_action_confirm(cheque, partner_bank, expected):
    cheque.write({
        'to_bank_id': partner_bank.id,
    })
    cheque.action_confirm()
    assert cheque.to_bank_id == partner_bank
    assert cheque.state == expected


@pytest.mark.parametrize('test_input, expected',
                         [({'deposit_date': False},
                           ('The Deposit Date is required,'
                            ' please check before proceeding further.')),
                             ({'deposit_date': '2022-01-01'},
                              'deposit')])
def test_action_to_deposit(cheque, test_input, expected):
    if test_input['deposit_date']:
        cheque.write({
            'deposit_date': '2022-01-01',
        })
        cheque.action_to_deposit()
        assert str(cheque.deposit_date) == test_input['deposit_date']
        assert cheque.state == expected
    else:
        with pytest.raises(ValidationError) as excinfo:
            cheque.action_to_deposit()
        assert str(excinfo.value) == expected


@pytest.mark.parametrize('test_input', [
    ({'type': 'vendor'}),
    ({'type': 'customer'}),
])
def test_action_change_cheque(cheque, test_input):
    view = cheque.env.ref(
        'beecy_account_cheque.account_change_cheque_wizard_views')
    res = cheque.with_context(
        default_type=test_input['type']).action_change_cheque()
    assert res == {
        'name': 'Account Cheque',
        'view_mode': 'form',
        'res_model': 'account.change.cheque.wizard',
        'view_id': view.id,
        'context': {
            'default_type': f"{test_input['type']}",
            'default_move_type': f"{test_input['type']}"},
        'type': 'ir.actions.act_window',
        'target': 'new'}


@pytest.mark.parametrize('test_input, expected',
                         [({
                             'close_date': False,
                             'type': 'customer'
                         }, 'The close date is required, please check.'),
                             ({
                                 'close_date': True,
                                 'type': 'customer'
                             }, True),
                             ({
                                 'close_date': True,
                                 'type': 'vendor'
                             }, True),
                         ])
def test_action_close(
        cheque,
        partner_bank,
        cheque_journal_bank,
        test_input,
        expected):
    if test_input['close_date']:
        cheque.write({
            'close_date': (datetime.utcnow().date()
                           if test_input['type'] == 'customer' else False),
            'type': test_input['type'],
            'from_bank_id': partner_bank.id,
            'to_bank_id': partner_bank.id,
            'journal_id': cheque_journal_bank.id,
        })
        res = cheque.action_close()
        assert cheque.close_date == datetime.utcnow().date()
        assert res == expected
        assert cheque.state == 'close'
        assert cheque.account_move_id
    else:
        cheque.write({
            'type': test_input['type'],
        })
        with pytest.raises(ValidationError) as excinfo:
            cheque.action_close()
        assert str(excinfo.value) == expected


def test_action_cancel(env, cheque):
    res = cheque.action_cancel()
    ctx = {
        'active_model': 'account.cheque',
        'active_id': cheque.id,
        'state': 'cancel'
    }
    view = env.ref('beecy_reason.view_cancel_reject_reason_form')
    expected = {
        'name': _('Cancel Account Payment'),
        'view_mode': 'form',
        'res_model': 'cancel.reject.reason',
        'view_id': view.id,
        'type': 'ir.actions.act_window',
        'context': ctx,
        'target': 'new'
    }
    assert res == expected


def test_action_set_draft(env, cheque, partner, cheque_journal_bank):
    Move = env['account.move']
    move_id = Move.create({
        "partner_id": partner.id,
        "journal_id": cheque_journal_bank.id,
    })
    cheque.write({
        'account_move_id': move_id.id
    })
    cheque.action_set_draft()
    assert cheque.state == 'draft'
    assert not cheque.account_move_id


@pytest.mark.parametrize('test_input, expected', [
                         ({'name': ''}, ("Please define your cheque number"
                                         " before proceeding further.")),
                         ({'name': 'Checque'}, 'to_deposit')
                         ])
def test_action_approve(cheque, test_input, expected):
    if test_input['name']:
        cheque.write({
            'name': test_input['name']
        })
        cheque.action_approve()
        assert cheque.name == test_input['name']
        assert cheque.state == expected
    else:
        cheque.write({
            'name': test_input['name']
        })
        with pytest.raises(ValidationError) as excinfo:
            cheque.action_approve()
        assert str(excinfo.value) == expected


def test_action_reject(env, cheque):
    res = cheque.action_reject()
    ctx = {
        'active_model': 'account.cheque',
        'active_id': cheque.id,
        'state': 'reject'
    }
    view = env.ref('beecy_reason.view_cancel_reject_reason_form')
    expected = {
        'name': _('Cancel Account Payment'),
        'view_mode': 'form',
        'res_model': 'cancel.reject.reason',
        'view_id': view.id,
        'type': 'ir.actions.act_window',
        'context': ctx,
        'target': 'new'
    }
    assert res == expected


def test_action_print_cheque(cheque, mocker):
    actoin_cheque = cheque.env.ref(
        'beecy_account_cheque.action_account_cheque_report')
    cheque.write({
        'state': 'draft',
    })
    spy_report_action = mocker.spy(type(actoin_cheque),
                                   'report_action')
    res = cheque.with_context(
        default_type='vendor').action_print_cheque()
    assert cheque.state == 'to_approve'
    spy_report_action.assert_any_call(actoin_cheque, cheque)
    expected = {
        'report_action': {
            'context': {
                'default_type': 'vendor',
                'active_ids': [cheque.id]},
            'data': None,
            'type': 'ir.actions.report',
            'report_name': 'beecy_account_cheque.cheque_report',
            'report_type': 'qweb-pdf',
            'report_file': 'beecy_account_cheque.cheque_report',
            'name': 'Cheque',
            'close_on_report_download': True}}
    assert res['context'] == expected
