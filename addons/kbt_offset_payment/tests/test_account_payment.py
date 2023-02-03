from pytest_tr_odoo.fixtures import env
import pytest

from .fixtures import *


@pytest.fixture
def model(env):
    return env['account.payment']


@pytest.mark.parametrize('test_input,expected', [
    ({'move_wht_id': True, 'offset_amount': 100}, 4),
    ({'move_wht_id': True}, False),
    ({'move_wht_id': False, 'offset_amount': 100}, 3),
    ({'move_wht_id': False}, False),
])
def test__prepare_move_line_default_vals(
    env,
    model,
    account_account,
    invoice,
    test_input,
    expected,
):
    ctx_dict = {'offset_account_id': account_account}
    if 'offset_amount' in test_input:
        ctx_dict['offset_amount'] = 100

    val_dict = {
        'amount': 100,
        'move_wht_id': invoice.id if test_input['move_wht_id'] else False
    }
    payment = model.with_context(ctx_dict).new(val_dict)
    res = payment._prepare_move_line_default_vals()
    if 'offset_amount' in test_input:
        assert len(res) == expected
    else:
        assert res[0]['account_id'] == account_account.id


@pytest.mark.parametrize('test_input', [
    ({'is_offset': True}),
    ({'is_offset': False}),
])
def test__get_valid_liquidity_accounts(
        env, model, account_account, test_input):
    ctx_dict = {'offset_account_id': account_account} \
        if test_input['is_offset'] else {}
    payment = model.with_context(ctx_dict).new({'amount': 100})
    res = payment._get_valid_liquidity_accounts()
    if test_input['is_offset']:
        assert account_account.id in [acc.id for acc in res]
    else:
        assert account_account.id not in [acc.id for acc in res]


@pytest.mark.parametrize(
    'test_input, expected', [
        ({
            'create': False}, {
                'is_reconciled': False, 'is_matched': False}), ({
                    'create': True, 'amount': 0}, {
                        'is_reconciled': True, 'is_matched': True}), ({
                            'create': True, 'amount': 100, 'default_account_id': True}, {
                                'is_reconciled': False, 'is_matched': True}), ({
                                    'create': True, 'amount': 100, 'offset_account_id': True}, {
                                        'is_reconciled': False, 'is_matched': True}), ({
                                            'create': True, 'amount': 100, 'offset_account_id': False}, {
                                                'is_reconciled': False, 'is_matched': False}), ])
def test__compute_reconciliation_status(
        env,
        model,
        currency_thb,
        account_account,
        main_company,
        test_input,
        expected):
    ctx_dict = {'offset_account_id': account_account} \
        if test_input.get('offset_account_id') else {}
    # select new or create method
    enter_payment = getattr(
        model.with_context(ctx_dict),
        'create' if test_input['create'] else 'new'
    )

    payment = enter_payment({
        'amount': test_input.get('amount', 0),
        'payment_type': 'inbound',
        'date': fields.Date.today(),
        'currency_id': currency_thb.id
    })
    if test_input.get('default_account_id'):
        # Force journal_id.default_account_id = liquidity_lines.account_id
        liquidity_lines, _, _ = payment._seek_for_lines()
        payment.journal_id.default_account_id = liquidity_lines.account_id.id

    payment._compute_reconciliation_status()
    assert payment.is_reconciled == expected['is_reconciled']
    assert payment.is_matched == expected['is_matched']
