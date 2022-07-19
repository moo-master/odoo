{
    'name': 'Beecy: Account Sale',
    'summary': '''
        Account Sale Function
    ''',
    'author': 'Roots',
    'category': 'Sales/Sales',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Santi T.',
    ],
    'external_dependencies': {'python': ['html2text']},
    'depends': [
        'beecy_account',
        'report_xlsx',
        'beecy_company_ext',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_sale_tax_report.xml',
        'views/account_menuitem.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
