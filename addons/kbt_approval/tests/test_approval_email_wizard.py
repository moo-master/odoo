from pytest_tr_odoo.fixtures import env
import pytest


@pytest.fixture
def model(env):
    return env['approval.email.wizard']


@pytest.fixture
def email_template(env):
    return env.ref('kbt_approval.approval_email_template')


@pytest.fixture
def employee(env):
    return env.ref('hr.employee_qdp')


@pytest.fixture
def manager(env):
    return env.ref('hr.employee_stw')


def test_send_approval_email(
        env,
        model,
        mocker,
        email_template,
        employee,
        manager):
    spy_send_mail = mocker.spy(type(email_template), 'send_mail')
    wizard = model.with_context(
        id=1,
        model='model',
        cids=1,
        menu_id='hr.employee_qdp',
        action='hr.employee_qdp',
    ).create({
        'employee_id': employee.id,
        'manager_id': manager.id,
        'name': 'TEST',
        'order_amount': 100,
        'order_name': 'TEST',
    })

    wizard.send_approval_email()
    assert spy_send_mail.called
