{
    'name': 'Beecy: Account Payment Extension',
    'summary': '''
        Beecy Account Payment Extension
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Pachara P.',
    ],
    'depends': [
        'beecy_account_payment',
        'beecy_account_tax',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/beecy_account_payment_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
