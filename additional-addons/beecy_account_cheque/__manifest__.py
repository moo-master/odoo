{
    'name': 'Beecy: Account Cheque',
    'summary': '''
        Account Cheque
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Yuthajak Q.',
    ],
    'depends': [
        'beecy_account_partner_bank_ext',
        'beecy_account_payment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_payment_method_cheque_data.xml',
        'report/cheque_report_templates.xml',
        'report/cheque_report.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_cheque_views.xml',
        'wizard/account_change_cheque_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
