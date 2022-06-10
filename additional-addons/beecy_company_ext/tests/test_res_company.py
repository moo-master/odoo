import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.company']


@pytest.fixture
def test_title(env):
    return env['res.partner.title'].create({
        'name': 'Test Title',
        'prefix': 'Test Prefix',
        'suffix': 'Test Suffix',
    })


@pytest.mark.parametrize('test_input,expected', [
    ({
        'name': 'Test Company',
        'prefix': 'Test Prefix',
        'suffix': 'Test Suffix',
        'house_number': '1234',
        'village_number': '1',
        'village': '-',
        'building': 'B',
        'floor': '1',
        'room_number': '123',
        'alley': 'Test 21',
        'sub_alley': 'Test 12',
        'name_english': 'Test English',
    }, {
        'nationality': 'th',
        'branch': 'hq',
        'branch_code': '00000',
        'prefix': 'Test Prefix',
        'suffix': 'Test Suffix',
        'title_prefix': 'Test Prefix',
        'title_suffix': 'Test Suffix',
    })
])
def test_create_company(model, test_title, test_input, expected):
    company_id = model.create(test_input)
    company_id._onchange_branch()

    assert company_id.branch == expected['branch']
    assert company_id.branch_code == expected['branch_code']

    assert company_id.prefix == expected['prefix']
    assert company_id.suffix == expected['suffix']

    company_id.title_id = test_title
    company_id._onchange_title()
    assert company_id.prefix == expected['title_prefix']
    assert company_id.suffix == expected['title_suffix']
