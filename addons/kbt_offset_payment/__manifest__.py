{
    'name': 'KBT Offset Payment',
    'summary': '''
        KBT Offset Payment
    ''',
    'author': 'Roots',
    'category': 'Company',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Patipon S.',
    ],
    'depends': [
        'kbt_partner_ext',
        'kbt_account_wht_ext'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_move_view.xml',
        'wizards/offset_payment_wizard_view.xml',
    ]
}
