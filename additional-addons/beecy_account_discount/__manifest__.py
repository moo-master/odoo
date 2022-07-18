{
    'name': 'Beecy: Account Discount',
    'summary': '''
        Beecy Invoicing Discount
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Tewtawat C.',
    ],
    'depends': [
        'beecy_base',
        'beecy_account_tax',
    ],
    'data': [
        'data/decimal_precision_data.xml',
        'views/account_move_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
