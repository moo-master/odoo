import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.config.settings']


@pytest.fixture
def company(env):
    return env['res.company'].create({
        'name': 'Limited',
        'is_module_beecy_account_payment_customer_steps': False,
        'beecy_account_payment_customer_steps': 'one_step',
        'is_module_beecy_account_payment_vendor_steps': False,
        'beecy_account_payment_vendor_steps': False,
    })


@pytest.fixture
def config(model):
    return model.create({
        'is_module_beecy_account_payment_customer_steps': False,
        'beecy_account_payment_customer_steps': 'one_step',
        'is_module_beecy_account_payment_vendor_steps': False,
        'beecy_account_payment_vendor_steps': False,
    })


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
def test_set_values(config, test_input, expected):
    is_customer = test_input.get('is_customer_steps')
    customer_steps = test_input.get('customer_steps')
    is_vendor = test_input.get('is_vendor_steps')
    vendor_steps = test_input.get('vendor_steps')
    if test_input.get('is_customer_steps'):
        config.write({
            'is_module_beecy_account_payment_customer_steps': is_customer,
            'beecy_account_payment_customer_steps': customer_steps,
            'is_module_beecy_account_payment_vendor_steps': is_vendor,
            'beecy_account_payment_vendor_steps': vendor_steps,
        })
        config.set_values()
        is_payment = config.is_module_beecy_account_payment_customer_steps
        payment_customer = config.beecy_account_payment_customer_steps
        assert is_payment == expected.get('is_steps')
        assert payment_customer == expected.get('step')
    else:
        config.write({
            'is_module_beecy_account_payment_customer_steps': is_customer,
            'beecy_account_payment_customer_steps': customer_steps,
            'is_module_beecy_account_payment_vendor_steps': is_vendor,
            'beecy_account_payment_vendor_steps': vendor_steps,
        })
        config.set_values()
        is_payment = config.is_module_beecy_account_payment_vendor_steps
        payment_vendor = config.beecy_account_payment_vendor_steps
        assert is_payment == expected.get('is_steps')
        assert payment_vendor == expected.get('step')


@pytest.mark.parametrize('test_input,expected', [
    ({'is_customer_steps': True,
      'customer_steps': 'one_step',
      'is_vendor_steps': False,
      'vendor_steps': False},
     {'is_steps': True, 'step': 'one_step'}),
    ({'is_customer_steps': False,
      'customer_steps': 'one_step',
      'is_vendor_steps': False,
      'vendor_steps': False},
     {'is_steps': False, 'step': False}),
    ({'is_customer_steps': False,
      'customer_steps': False,
      'is_vendor_steps': True,
      'vendor_steps': 'one_step'},
     {'is_steps': True, 'step': 'one_step'}),
    ({'is_customer_steps': False,
      'customer_steps': False,
      'is_vendor_steps': True,
      'vendor_steps': 'two_step'},
     {'is_steps': False, 'step': False}),
])
def test__onchange_payment_customer_step(config, test_input, expected):
    is_customer = test_input.get('is_customer_steps')
    customer_steps = test_input.get('customer_steps')
    is_vendor = test_input.get('is_vendor_steps')
    vendor_steps = test_input.get('vendor_steps')
    if test_input.get('is_vendor_steps'):
        if test_input.get('vendor_steps') != 'one_step':
            is_vendor = False
        config.write({
            'is_module_beecy_account_payment_customer_steps': is_customer,
            'beecy_account_payment_customer_steps': customer_steps,
            'is_module_beecy_account_payment_vendor_steps': is_vendor,
            'beecy_account_payment_vendor_steps': vendor_steps,
        })
        config._onchange_payment_vendor_step()
        is_payment = config.is_module_beecy_account_payment_vendor_steps
        payment_vendor = config.beecy_account_payment_vendor_steps
        assert is_payment == expected.get('is_steps')
        assert payment_vendor == expected.get('step')
    elif test_input.get('is_customer_steps'):
        # is_customer = False
        config.write({
            'is_module_beecy_account_payment_customer_steps': is_customer,
            'beecy_account_payment_customer_steps': customer_steps,
            'is_module_beecy_account_payment_vendor_steps': is_vendor,
            'beecy_account_payment_vendor_steps': vendor_steps,
        })
        config._onchange_payment_customer_step()
        is_payment = config.is_module_beecy_account_payment_customer_steps
        payment_customer = config.beecy_account_payment_customer_steps
        assert is_payment == expected.get('is_steps')
        assert payment_customer == expected.get('step')
    else:
        config.write({
            'is_module_beecy_account_payment_customer_steps': is_customer,
            'beecy_account_payment_customer_steps': customer_steps,
            'is_module_beecy_account_payment_vendor_steps': is_vendor,
            'beecy_account_payment_vendor_steps': vendor_steps,
        })
        config._onchange_payment_customer_step()
        is_payment = config.is_module_beecy_account_payment_customer_steps
        payment_customer = config.beecy_account_payment_customer_steps
        assert is_payment == expected.get('is_steps')
        assert payment_customer == expected.get('step')
