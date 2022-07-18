{
    'name': 'Beecy: Partner Attachment',
    'summary': '''
        Partner Attachment
    ''',
    'author': 'Roots',
    'category': 'Partner',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Isares S.',
    ],
    'depends': [
        'beecy_core_update',
        'account_check_printing',
        'purchase',
        'sales_team',
        'stock',
    ],
    'data': [
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
