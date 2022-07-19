import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def currency_tax(env):
    return env['res.currency'].create({
        'name': 'AAS',
        'rate': 1.000000,
        'currency_unit_label': 'ASS',
        'currency_subunit_label': 'ASS',
        'symbol': 'ASS'
    })


@pytest.fixture
def partner_tax(env):
    return env['res.partner'].create({
        'name': 'partner AAS',
        'email': 'kaka@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
    })


@pytest.fixture
def product_tax(env):
    product = env['product.product'].create({
        'name': 'product coco',
        'list_price': 600.0,
    })
    return product


@pytest.fixture
def account_move_tax(env, partner_tax, currency_tax, product_tax):
    return env['account.move'].create({
        'partner_id': partner_tax.id,
        'invoice_date_due': fields.Date.today(),
        'currency_id': currency_tax.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [
            (0, 0, {'product_id': product_tax.id,
                    'price_unit': product_tax.list_price,
                    'quantity': 5}),
        ]
    })


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
        'code': '9897',
        'name': 'Account WHT',
        'user_type_id': account_type.id
    })


@pytest.mark.parametrize('test_input', [
    ({'pnd_type': 'pnd3', 'wht_type_name': 'AW'}),
    ({'pnd_type': 'pnd53', 'wht_type_name': 'AQ'}),
])
def test_compute_tax(env, account_move_tax, test_input, account_id):
    wht_type = env['account.wht.type'].create({
        'display_name': f"WHT {test_input['wht_type_name']}",
        'percent': 10,
    })
    wht = env['account.wht'].create({
        'wht_type': 'sale',
        'wht_kind': test_input['pnd_type'],
        'document_date': fields.Datetime.now(),
        'wht_payment': 'wht',
        'account_id': account_id.id,
        'line_ids': [(0, 0, {
            'invoice_line_id': account_move_tax.invoice_line_ids.id,
            'wht_type_id': wht_type.id})]
    })
    pnd = env['account.wht.pnd'].create({
        'pnd_date': fields.Date.today(),
        'pnd_type': test_input['pnd_type'],
    })
    pnd._get_selection()
    pnd.write({
        'wht_ids': [(6, 0, [wht.id])],
    })
    pnd._compute_line()
    assert pnd.total_tax == sum(pnd.wht_ids.mapped('tax'))


@pytest.fixture
def account_type_partner(env):
    return env['account.account.type'].create({
        'name': 'ACC Type',
        'type': 'other',
        'internal_group': 'income',
    })


@pytest.fixture
def account_id(env, account_type_partner):
    return env['account.account'].create({
        'code': '2341',
        'name': 'Account WHT Partner',
        'user_type_id': account_type_partner.id
    })


@pytest.mark.parametrize('test_input', [
    ({'has_line': True}),
    ({'has_line': False}),
])
def test__compute_wht_line_partner(env, test_input, account_id):
    if not test_input['has_line']:
        pnd = env['account.wht.pnd'].create({'pnd_type': 'pnd3'})
        pnd._compute_wht_line_partner()
        assert pnd.wht_ids_count_str == False
    else:
        pnd = env['account.wht.pnd'].create({'pnd_type': 'pnd3'})
        wht = env['account.wht'].create({
            'document_date': fields.Datetime.now(),
            'wht_type': 'sale',
            'wht_kind': 'pnd3',
            'wht_payment': 'wht',
            'account_id': account_id.id,
        })
        pnd.write({
            'wht_ids': [(6, 0, [wht.id])],
        })
        pnd._compute_wht_line_partner()
        partner_count = len(pnd.wht_ids.mapped('partner_id')) or 0
        expected = f'{len(pnd.wht_ids) or 0} Records From {partner_count} Partner'
        assert pnd.wht_ids_count_str == expected


def test_action_print_pnd3(env):
    pnd = env['account.wht.pnd'].create({
        'pnd_type': 'pnd3',
    })
    result = pnd.action_print_pnd3()
    assert result


def test_action_print_pnd53(env):
    pnd = env['account.wht.pnd'].create({
        'pnd_type': 'pnd53',
    })
    result = pnd.action_print_pnd53()
    assert result


def test_action_files_docs(env):
    pnd = env['account.wht.pnd'].create({
        'pnd_type': 'pnd3',
    })
    result = pnd.action_files_docs()
    assert result


def test_action_file(env):
    pnd = env['account.wht.pnd'].create({
        'pnd_type': 'pnd3',
    })
    result = pnd.action_file()
    assert result


def test__compute_pickup_time_formated(env):
    pnd = env['account.wht.pnd'].create({
        'pnd_type': 'pnd3',
        'pnd_date': '2022-03-31',
        'select_month_date': '2022-03-31',
    })
    pnd._compute_pickup_time_formated()
    assert pnd.name == '03/2022'


@pytest.mark.parametrize('test_input,expected', [
    ({'move_type': 'pnd3'}, 'section3'),
    ({'move_type': 'pnd53'}, 'section53'), ])
def test__default_get_pnd(env, test_input, expected):
    pnd = env['account.wht.pnd'].with_context({"default_pnd_type": test_input['move_type']}).create({
        'pnd_type': test_input['move_type'], })
    pnd.with_context(
        {"default_pnd_type": test_input['move_type']})._default_get_pnd()
    assert pnd.section == expected
