from pytest_tr_odoo.fixtures import env
import pytest

from .fixtures import *


@pytest.fixture
def model(env):
    return env['account.move']


def test__compute_offset(env, invoice, bill):
    invoice.write({
        'offset_ids': [(0, 0, {
            'invoice_id': bill.id
        })]
    })
    invoice._compute_offset()
    assert invoice.total_offset
    assert invoice.move_offset_ids
