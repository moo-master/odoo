import pytest
from pytest_tr_odoo.fixtures import env
from odoo import fields


@pytest.fixture
def model(env):
    return env['wizard.profit.loss']


def test__create_wizard(env, model):
    report = model.create({
        'from_date': fields.Date.today(),
        'to_date': fields.Date.today(),
    })
    test = report.print_report_xls()
    assert test is not None


def test__onchange_to_date(env, model):
    report = model.create({'from_date': '2023-01-15'})
    report._onchange_to_date()
    assert report.from_date.day == 1
    assert report.to_date.day == 31
