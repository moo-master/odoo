import pytest
import xlsxwriter

from pytest_tr_odoo.fixtures import env
from odoo import fields
from io import BytesIO


@pytest.fixture
def model(env):
    return env['report.kbt_account_ext.profit_loss_report_xlsx']


@pytest.fixture
def partner(env):
    return env.ref('base.res_partner_1')


@pytest.fixture
def product(env):
    return env.ref('product.product_product_1')


@pytest.fixture
def account(env):
    return env['account.account'].create({
        'name': 'acc2 acc2',
        'user_type_id': env.ref('account.data_account_type_receivable').id,
        'account_group_id': env.ref('kbt_account_ext.data_account_group_net_sales_1').id,
        'code': '02',
        'reconcile': True,
    })


def test__generate_xlsx(env, model, mocker):
    report = model.new({})
    file_data = BytesIO()
    workbook = xlsxwriter.Workbook(file_data, {})
    wizard = env['wizard.profit.loss'].create({
        'from_date': fields.Date.today(),
        'to_date': fields.Date.today(),
    })
    spy_fator_1 = mocker.spy(type(model), 'add_format_work_book')
    spy_fator_2 = mocker.spy(type(model), 'set_header_xlsx')
    spy_fator_3 = mocker.spy(type(model), 'set_table_lines_value')
    report.generate_xlsx_report(workbook, False, wizard)

    assert spy_fator_1.called
    assert spy_fator_2.called
    assert spy_fator_3.called
