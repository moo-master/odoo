{
    'name': 'Beecy: Account Payment',
    'summary': '''
        Payment
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [
            'bahttext',
        ],
    },
    'contributors': [
        'Yuthajak Q.',
    ],
    'depends': [
        'beecy_account_billing_note',
        'beecy_account_wht',
        'beecy_web_report',
        'beecy_font',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/billing_note_report_templates.xml',
        'report/payment_voucher_report.xml',
        'report/account_payment_receipt_report.xml',
        'report/account_payment_receipt_report_templates.xml',
        'report/payment_receipt_report_tax_invoice_templates.xml',
        'report/account_payment_receipt_report_tax_invoice.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/payment_account_move_wizard_views.xml',
        'views/account_payment_views.xml',
        'views/beecy_account_payment_views.xml',
        'views/account_billing_note_views.xml',
        'views/account_move_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
