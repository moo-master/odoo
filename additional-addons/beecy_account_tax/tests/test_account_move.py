import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields, _
from odoo.exceptions import ValidationError


@pytest.fixture
def tax_test(env):
    return env['account.tax'].create({
        'name': 'TEST',
        'type_tax_use': 'sale'
    })


@pytest.fixture
def tax_test2(env):
    return env['account.tax'].create({
        'name': 'TEST2',
        'type_tax_use': 'sale'
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'have_tax': True}, 'TEST'),
    ({'have_tax': False}, False),
])
def test_onchange_tax_id(env, test_input, expected, tax_test):
    tax_id = test_input.get('have_tax') and tax_test
    move_id = env['account.move'].create({
        'name': 'Test Invoice',
        'move_type': 'out_invoice',
        'invoice_line_ids': [(0, 0, {'name': 'test line'})]
    })

    move_id.tax_id = tax_id
    move_id._onchange_tax_id()
    line_tax_id = move_id.mapped('invoice_line_ids.tax_ids')
    assert line_tax_id.name == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'have_tax': True}, ('TEST', '')),
    ({'have_tax': False}, (False, '')),
    ({'have_tax': True, 'multi_tax': True},
     ('TEST', _('Multiple taxes per line are resticted'))),
])
def test_get_computed_taxes(env, test_input, expected, tax_test, tax_test2):
    tax_id = test_input.get('have_tax') and tax_test.id
    tax_expected = expected[0]
    tax_validation_expected = expected[1]
    move_id = env['account.move'].create({
        'name': 'Test Invoice',
        'move_type': 'out_invoice',
        'tax_id': tax_id,
        'invoice_line_ids': [(0, 0, {'name': 'test line'})]
    })

    line_id = move_id.invoice_line_ids
    if test_input.get('multi_tax'):
        line_id.tax_ids = [(4, tax_test2.id), (4, tax_test.id)]
    try:
        line_id._onchange_taxes()
    except ValidationError as e:
        assert str(e) == tax_validation_expected

    tax_id = line_id._get_computed_taxes()
    tax_id = tax_id and tax_id.name or tax_id
    assert tax_id == tax_expected
