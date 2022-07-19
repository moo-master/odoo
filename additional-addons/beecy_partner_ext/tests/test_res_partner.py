import pytest
from pytest_tr_odoo.fixtures import env


@pytest.fixture
def model(env):
    return env['res.partner']


@pytest.fixture
def test_title(env):
    return env['res.partner.title'].create({
        'name': 'Test Title',
        'prefix': 'Test Prefix',
        'suffix': 'Test Suffix',
    })


@pytest.mark.parametrize('test_input,expected', [
    ({
        'is_company': False,
        'name': 'Test Partner',
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
        'company_type': 'person',
        'title_domain': [
            ('contact_type', '=', 'person')
        ],
        'prefix': 'Test Prefix',
        'suffix': 'Test Suffix',
        'title_prefix': 'Test Prefix',
        'title_suffix': 'Test Suffix',
    })
])
def test_create_partner(model, test_title, test_input, expected):
    partner_id = model.new(test_input)
    partner_id._onchange_branch()
    assert partner_id.nationality == expected['nationality']
    assert partner_id.branch == expected['branch']
    assert partner_id.branch_code == expected['branch_code']
    assert partner_id.company_type == expected['company_type']

    assert partner_id.prefix == expected['prefix']
    assert partner_id.suffix == expected['suffix']

    partner_id.title = test_title
    partner_id._onchange_title()
    assert partner_id.prefix == expected['title_prefix']
    assert partner_id.suffix == expected['title_suffix']

    title_domain = partner_id._onchange_company_type_domain_title()
    assert title_domain['domain']['title'] == expected['title_domain']


def test_compute_display_name(model):
    partner_id = model.new({
        'name': 'Test Partner',
        'prefix': 'Prefix',
        'suffix': 'Suffix',
    })
    partner_id._compute_display_name()
    assert partner_id.display_name == 'Prefix Test Partner Suffix'


@pytest.mark.parametrize('test_input,expected',
                         [({'company_name': 'Trinity Roots',
                            'house_number': "191",
                            },
                           {'company': 'Trinity Roots',
                             'check_format': 2}),
                             ({'company_name': 'Trinity Roots',
                               'house_number': "191",
                               'arg': True},
                              {'company': '',
                               'check_format': -1}),
                          ])
def test_prepare_display_address(model, test_input, expected):

    if test_input.get('company_name'):
        partner_id = model.new({
            'room_number': test_input.get('house_number'),
            'company_name': test_input.get('company_name')
        })
    else:
        partner_id = model.new({
            'room_number': test_input.get('house_number'),
        })

    # assert partner_id._prepare_display_address(test_input.get('arg'))[0].rfind("company_name")

    assert partner_id._prepare_display_address(test_input.get(
        'arg'))[0].rfind("company_name") == expected['check_format']
    assert partner_id._prepare_display_address(test_input.get(
        'arg'))[1].get("company_name") == expected['company']
