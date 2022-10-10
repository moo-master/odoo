from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['account.move']


def test_dummy(model):
    # Dummy test for pass test in Jenkin
    move = model.new()
    assert move
