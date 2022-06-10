import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['base.document.layout']


@pytest.mark.parametrize('test_input,expected', [(
    {'phone': 123456},
    '<span><b>YourCompany<br></b>250 Executive Park Blvd,'
    ' Suite 3400<br>False<br>เขต California False<br><span'
    ' class="fa fa-phone"></span>123456  Tax ID:False</span>'),
    ({'phone': 987654321},
     '<span><b>YourCompany<br></b>250 Executive Park Blvd'
        ', Suite 3400<br>False<br>เขต California False<br><span '
        'class="fa fa-phone"></span>987654321  Tax ID:False</span>'),
])
def test_action_update_company_detail(model, env, test_input, expected):
    company = env["res.company"].search([], limit=1)
    company.phone = test_input['phone']
    model.company_id = company.id
    model.action_update_company_detail()
    assert company.company_details == expected
