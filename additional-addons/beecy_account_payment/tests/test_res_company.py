import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.company']


@pytest.mark.parametrize('test_input,expected', [
    ({'is_customer_steps': True,
      'customer_steps': 'one_step',
      'is_vendor_steps': False,
      'vendor_steps': False},
     {'is_steps': True, 'step': 'one_step'}),
    ({'is_customer_steps': False,
      'customer_steps': False,
      'is_vendor_steps': True,
      'vendor_steps': 'one_step'},
     {'is_steps': True, 'step': 'one_step'}),
    ({'is_customer_steps': False,
      'customer_steps': False,
      'is_vendor_steps': True,
      'vendor_steps': 'two_step'},
     {'is_steps': True, 'step': 'two_step'}),
])
def test_create(model, test_input, expected):
    company_id = model.create({
        'name': 'Limited',
        'is_module_beecy_account_payment_customer_steps': test_input.get('is_customer_steps'),
        'beecy_account_payment_customer_steps': test_input.get('customer_steps'),
        'is_module_beecy_account_payment_vendor_steps': test_input.get('is_vendor_steps'),
        'beecy_account_payment_vendor_steps': test_input.get('vendor_steps'),
    })
    assert company_id.name == 'Limited'
    if test_input.get('is_customer_steps'):
        assert company_id.is_module_beecy_account_payment_customer_steps == expected.get(
            'is_steps')
        assert company_id.beecy_account_payment_customer_steps == expected.get(
            'step')
    else:
        assert company_id.is_module_beecy_account_payment_vendor_steps == expected.get(
            'is_steps')
        assert company_id.beecy_account_payment_vendor_steps == expected.get(
            'step')
