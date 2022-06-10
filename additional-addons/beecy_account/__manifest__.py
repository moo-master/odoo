{
    'name': 'Beecy: Account Extension',
    'summary': '''
        Invoicing & Payment Extension
        Set Sequence CI / VB
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
        'Santi T.',
        'Thotsaphorn Sri.',
    ],
    'depends': [
        'account',
        'beecy_core_update',
        'beecy_reason',
        'beecy_date_range_sequence',
        'beecy_web_report',
        'beecy_account_wht',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_move_reversal_view.xml',
        'wizard/account_debit_note_reason_wizard.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/account_report.xml',
        'report/credit_note_report.xml',
        'report/credit_note_report_templates.xml',
        'report/tax_invoice_delivery_report_templates.xml',
        'report/tax_invoice_delivery_report.xml',
        'report/tax_invoice_billing_note_report_templates.xml',
        'report/tax_invoice_billing_note_report.xml',
        'report/debit_note_template_report.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
