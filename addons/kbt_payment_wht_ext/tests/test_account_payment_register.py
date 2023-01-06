from pytest_tr_odoo.fixtures import env
from odoo.exceptions import ValidationError
import pytest


@pytest.fixture
def model(env):
    return env['account.payment.register']


@pytest.fixture
def partner(env):
    return env.ref('base.res_partner_1')


@pytest.fixture
def product(env):
    return env.ref('product.product_order_01')


@pytest.fixture
def invoice(env,
            product,
            partner,):
    return env['account.move'].create({
        'partner_id': partner.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id,
            'quantity': 10,
            'price_unit': 100,
        })],
    })


@pytest.mark.parametrize('test_input', [
    ({'amount': 0}),
    ({'amount': 1000})
])
def test_action_create_payments(env, model, invoice, test_input):
    invoice.action_post()
    wizard = model.with_context(
        active_model='account.move',
        active_ids=invoice.ids
    ).create({
        'amount': test_input.get('amount'),
        'wht_amount': 100,
    })
    if test_input.get('amount'):
        wizard.action_create_payments()
        assert invoice.is_wht_paid
    else:
        with pytest.raises(ValidationError) as excinfo:
            wizard.action_create_payments()
            msg = ("Amount must greater or equal to WHT Amount")
            assert excinfo.value.name == msg


def test__onchange_paid_amount(env, model, invoice):
    invoice.action_post()
    wizard = model.with_context(
        active_model='account.move',
        active_ids=invoice.ids
    ).create({
        'paid_amount': 200,
        'wht_amount': 100,
    })
    wizard._onchange_paid_amount()
    assert wizard.amount == 300
