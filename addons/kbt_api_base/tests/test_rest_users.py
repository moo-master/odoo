from pytest_tr_odoo.fixtures import env
import pytest

from odoo.exceptions import AccessDenied


@pytest.fixture
def model(env):
    return env['res.users']


@pytest.mark.parametrize('test_input', [
    ({'password': True}),
    ({'password': False})
])
def test__check_credentials(env, model, test_input):
    k = env['res.users.apikeys']._generate(None, 'test_key')
    if test_input.get('password'):
        env.user._check_credentials(k, {})
    else:
        with pytest.raises(AccessDenied) as excinfo:
            env.user._check_credentials('check_error_password', {})
            assert excinfo.value.name == "Access Denied"
