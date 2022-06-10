import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields
from datetime import datetime
from .fixtures_data import DATA_CREATE_LINES_WHT, DATAS_WHT_TYPE, EXPECTED_PREPARE_LINES_WHT, LINES_WHT, UPDATE_GROUP_DATA


@pytest.fixture
def currency(env):
    return env['res.currency'].create({
        'name': 'THR',
        'rate': 1.000000,
        'currency_unit_label': 'TRBaht',
        'currency_subunit_label': 'TRSatang',
        'symbol': 't฿'
    })


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Your Partner',
        'email': 'test@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
    })


@pytest.fixture
def product_inv(env):
    return env['product.product'].create({
        'name': 'product test wht',
        'list_price': 150,
    })


@pytest.fixture
def account_move(env, partner, currency, product_inv):
    return env['account.move'].create({
        'partner_id': partner.id,
        'invoice_date_due': fields.Date.today(),
        'currency_id': currency.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [
            (0, 0, {'product_id': product_inv.id,
                    'price_unit': 100.0,
                    'quantity': 5}),
        ]
    })


@pytest.fixture
def acc_wht_type(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 10,
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
        'code': '4001',
        'name': 'Test Account',
        'user_type_id': account_type.id
    })


@pytest.fixture
def acc_wht(env, partner, account_id):
    return env['account.wht'].create({
        'name': 'wht',
        'partner_id': partner.id,
        'document_date': '2022-03-01',
        'wht_type': 'sale',
        'wht_kind': 'pnd2',
        'wht_payment': 'wht',
        'account_id': account_id.id,
    })


def test_compute_wht_amount(env, account_move):
    acc_wht_type = env['account.wht.type'].create({
        'display_name': 'test WHT',
        'percent': 10,
    })
    acc_wht = env['account.wht'].new({
        'line_ids': [(0, 0, {
            'invoice_line_id': account_move.invoice_line_ids.id,
            'wht_type_id': acc_wht_type.id})]
    })

    acc_wht._compute_wht_amount()
    assert acc_wht.base_amount == 500.0


def test_action_set_to_draft(acc_wht):
    acc_wht.action_set_to_draft()
    assert acc_wht.status == 'draft'


@pytest.mark.parametrize('test_input,expected',
                         [({'sequence_code': 'seq.account.wht.customer',
                            'type': 'sale'},
                           'C22030001'),
                          ({'sequence_code': 'seq.account.wht.vendor',
                            'type': 'purchase'},
                           'S22030001'),
                          ])
def test_action_done(env, acc_wht, mocker, test_input, expected):
    spy_sequence_code = mocker.spy(type(env['ir.sequence']), 'next_by_code')
    acc_wht.name = False
    acc_wht.wht_type = test_input['type']
    acc_wht.action_done()
    spy_sequence_code.assert_called_once_with(
        env['ir.sequence'],
        test_input['sequence_code'],
        acc_wht.document_date,
    )
    assert acc_wht.name == expected


@ pytest.mark.parametrize('test_input,expected', [
    ({'vat': '1111111111111'},
     ('1', '1111', '11111', '11', '1')),
    ({'vat': '11111111'},
     False),
])
def test_split_id_card(acc_wht, test_input, expected):
    acc_wht.partner_id.vat = test_input['vat']
    res = acc_wht.split_id_card()
    assert res == expected


@ pytest.mark.parametrize('test_input,expected', [
    ({'vat': '1111111111111'},
     ('1', '1111', '11111', '11', '1')),
    ({'vat': '11111111'},
     False),
])
def test_split_company_id_card(env, acc_wht, test_input, expected):
    env.company.vat = test_input['vat']
    res = acc_wht.split_company_id_card()
    assert res == expected


@ pytest.fixture
def currency_tax(env):
    return env['res.currency'].create({
        'name': 'GH',
        'rate': 1.000000,
        'currency_unit_label': 'GHQ',
        'currency_subunit_label': 'GHQ',
        'symbol': 'GHQ'
    })


@ pytest.fixture
def partner_tax(env):
    return env['res.partner'].create({
        'name': 'Partner&*&*',
        'email': 'coco@other.company.com',
        'supplier_rank': 10,
        'company_id': 1,
    })


@ pytest.fixture
def product_tax(env):
    product = env['product.product'].create({
        'name': 'product acc move tax',
        'list_price': 600.0,
    })
    return product


@ pytest.fixture
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


@ pytest.fixture
def acc_wht_type(env):
    return env['account.wht.type'].create({
        'display_name': 'test WHT',
        'name': '1. เงินเดือน ค่าจ้าง เบี้ยเลี้ยง โบนัส ฯลฯ ตามมาตรา 40 (1)',
        'percent': 10,
    })


def test__compute_tax(env, acc_wht_type, account_move_tax):
    wht = env['account.wht'].new({
        'line_ids': [(0, 0, {
            'invoice_line_id': account_move_tax.invoice_line_ids.id,
            'wht_type_id': acc_wht_type.id})]
    })
    base_amount = sum(
        account_move_tax.invoice_line_ids.mapped('price_subtotal'))
    tax_expected = base_amount * (acc_wht_type.percent / 100)
    wht._compute_tax()
    assert wht.tax == tax_expected


def test_name_search(env):
    wht_type = env['account.wht.type']
    wht_type.create({
        'name': 'WHT search1',
        'percent': 10,
    })
    wht_type.create({
        'name': 'test search2',
        'percent': 10,
    })
    ids = wht_type.name_search(name='search')
    assert len(ids) == 2


@ pytest.mark.parametrize('test_input,expected', [
    ({'company_type': 'person'}, 'pnd3'),
    ({'company_type': 'company'}, 'pnd53'),
])
def test__onchange_partner_id(acc_wht, test_input, expected):
    acc_wht.partner_id.write({
        'company_type': test_input['company_type']
    })
    acc_wht._onchange_partner_id()
    assert acc_wht.wht_kind == expected


@ pytest.mark.parametrize('test_input', [
    ({'move_type': 'out_invoice', 'wht_type': 'sale'}),
    ({'move_type': 'in_invoice', 'wht_type': 'purchase'})
])
def test__compute_invoice_line_ids(
        env,
        acc_wht,
        partner_tax,
        currency_tax,
        acc_wht_type,
        product_tax,
        test_input):
    Account_move = env['account.move']
    if test_input['move_type'] == 'out_invoice':
        list_invoice_line_ids = Account_move.search(
            [('move_type', 'in',
                ('in_invoice', 'in_refund', 'in_receipt', 'in_debit'))
             ]).mapped('invoice_line_ids').ids
    else:
        list_invoice_line_ids = Account_move.search(
            [('move_type', 'in',
                ('out_invoice', 'out_refund', 'out_receipt', 'out_debit'))
             ]).mapped('invoice_line_ids').ids
    move = env['account.move'].create({
        'partner_id': partner_tax.id,
        'invoice_date_due': fields.Date.today(),
        'currency_id': currency_tax.id,
        'move_type': test_input['move_type'],
        'invoice_line_ids': [
            (0, 0, {'product_id': product_tax.id,
                    'price_unit': product_tax.list_price,
                    'quantity': 5}),
        ]
    })
    acc_wht.write({
        'wht_type': test_input['wht_type'],
        'line_ids': [(0, 0, {
            'invoice_line_id': move.invoice_line_ids.id,
            'wht_type_id': acc_wht_type.id})]
    })
    acc_wht._compute_invoice_line_ids()
    excepted = len(acc_wht.line_ids) + len(list_invoice_line_ids)
    assert len(acc_wht.invoice_line_ids) == excepted


@ pytest.mark.parametrize('test_input,expected', [
    ({'move_date': True}, '01/01/2565'),
    ({'move_date': False}, ['01', '03', 2565]),
])
def test_split_datetime(acc_wht, test_input, expected):
    date = False
    if test_input['move_date']:
        date = datetime.strptime('01012022', "%d%m%Y").date()
    res = acc_wht.split_datetime(date)
    assert res == expected


@ pytest.mark.parametrize('test_input,expected', [
    ({'line_ids': True}, EXPECTED_PREPARE_LINES_WHT),
    ({'line_ids': False}, {}),
])
def test_prepare_lines_wht(
        env,
        acc_wht,
        account_move_tax,
        test_input,
        expected,
        acc_wht_type,
        mocker):
    spy__create_lines_wht = mocker.spy(type(acc_wht), '_create_lines_wht')
    spy_update_line_wht = mocker.spy(type(acc_wht), 'update_line_wht')
    if not test_input['line_ids']:
        res = acc_wht.prepare_lines_wht()
    elif test_input['line_ids']:
        list_wht_type = []
        account_move_tax.invoice_line_ids.write({'date': '2022-04-19'})
        for wht in DATAS_WHT_TYPE:
            acc_wht_type = env['account.wht.type'].create({
                'display_name': wht,
                'name': wht,
                'percent': 10,
            })
            list_wht_type.append(
                (0, 0, {
                    'invoice_line_id': account_move_tax.invoice_line_ids.id,
                    'note': 'Account WHT',
                    'wht_type_id': acc_wht_type.id})
            )
        acc_wht.write({
            'wht_type': 'sale',
            'line_ids': list_wht_type,
        })
        res = acc_wht.prepare_lines_wht()
        assert spy__create_lines_wht.call_count == 1
        assert spy_update_line_wht.call_count == 27
        assert res == expected


def test__create_lines_wht(acc_wht):
    res = acc_wht._create_lines_wht()
    assert res == DATA_CREATE_LINES_WHT


def test_update_group_data_line_wht(acc_wht, account_move_tax, acc_wht_type):
    account_move_tax.invoice_line_ids.write({'date': '2022-04-19'})
    acc_wht.write({
        'wht_type': 'sale',
        'line_ids': [(0, 0, {
            'invoice_line_id': account_move_tax.invoice_line_ids.id,
            'wht_type_id': acc_wht_type.id,
        })]
    })
    acc_wht.update_group_data_line_wht(LINES_WHT, acc_wht.line_ids[0], 'wht_1')
    assert LINES_WHT == UPDATE_GROUP_DATA


def test_amount_total_text(acc_wht):
    th_bath = acc_wht._amount_total_text(40)
    assert th_bath == 'สี่สิบบาทถ้วน'
