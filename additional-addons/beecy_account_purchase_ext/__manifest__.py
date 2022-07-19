{
    'name': 'Beecy: Account Purchase Extension',
    'summary': '''
        Invoicing & Purchase Extension
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Saravut s.',
    ],
    'depends': [
        'beecy_core_update',
        'report_xlsx',
        'beecy_account',
        'beecy_company_ext',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/purchase_tax_report_xlsx.xml',
        'wizard/purchase_tax_report_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
