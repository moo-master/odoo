# from pytest_tr_odoo.fixtures import env
# import pytest


# @pytest.fixture
# def model(env):
#     return env['org.level']


# def test_create_hr_employee(env):
#     partner_id = env['res.users'].create({
#         'name': 'Marc Demo',
#         'email': 'mark.brown23@example.com',
#         'image_1920': False,
#         'login': 'demo_1',
#         'password': 'demo_123'
#     })
#     hr_employee = env['hr.employee'].create({
#         'user_id': partner_id.id,
#         'image_1920': False
#     })
#     hr_employee.level_id = env['org.level'].create({
#         'level': 123456789,
#         'description': "test",
#     })
#     assert hr_employee.level_id
