from pytest_tr_odoo.fixtures import env
from odoo.exceptions import ValidationError
import pytest

from .fixtures import *


@pytest.fixture
def model(env):
    return env['offset.payment.wizard']


@pytest.fixture
def offset_wizard(env, account_account):
    return env['offset.payment.wizard'].create({
        'account_id': account_account.id
    })


@pytest.mark.parametrize('test_input, expected', [
    ('out_invoice', ('inbound', 'customer')),
    ('in_invoice', ('outbound', 'supplier')),
])
def test__get_type(offset_wizard, test_input, expected):
    res = offset_wizard._get_type(test_input)
    assert res == expected


def test__get_bank_journal(env, offset_wizard, account_journal):
    res = offset_wizard._get_bank_journal()
    assert res.code == 'BNK'


def test__get_manual_payment_method(env, offset_wizard, account_journal):
    res = offset_wizard._get_manual_payment_method(account_journal, 'inbound')
    assert res


def test_button_confirm_error(env, model, account_account, invoice, bill):
    offset = model.with_context(active_ids=invoice.ids).create({
        'account_id': account_account.id
    })
    invoice.write({
        'offset_ids': [(0, 0, {
            'invoice_id': bill.id
        })]
    })
    with pytest.raises(ValidationError) as excinfo:
        msg = "Waning! This process cannot continues because the amount to be processed is greater than the amount of this document"
        invoice.write({'total_offset': 9999999})
        offset.button_confirm()
        assert excinfo.value.name == msg


def test_button_confirm(
        env,
        model,
        account_account,
        invoice,
        bill,
        account_journal,
        account_id,
        account_pnd3_id,
        account_pnd53_id):
    env.company.write({
        'ap_wht_default_account_pnd3_id': account_pnd3_id.id,
        'ap_wht_default_account_pnd53_id': account_pnd53_id.id,
        'ar_wht_default_account_id': account_id.id,
    })
    offset = model.with_context(active_ids=invoice.ids).create({
        'account_id': account_account.id
    })
    invoice.write({
        'offset_ids': [(0, 0, {'invoice_id': bill.id})]
    })
    offset.button_confirm()
    assert invoice.x_offset
    assert invoice.payment_state == 'paid'
    assert bill.payment_state == 'paid'
