{
    'name': 'KBT Account WHT Ext',
    'summary': '''
        KBT Account WHT Ext
    ''',
    'author': 'Roots',
    'category': 'Company',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Pachara P.',
    ],
    'depends': [
        'kbt_payment_wht_ext',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/account_wht_view.xml',
    ]
}
