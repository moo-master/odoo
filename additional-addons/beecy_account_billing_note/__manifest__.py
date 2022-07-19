{
    'name': 'Beecy: Account Billing Note',
    'summary': '''
        Account Billing Note
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
        'Saravut S.',
    ],
    'depends': [
        'beecy_partner_ext',
        'beecy_reason',
        'beecy_web_report',
        'beecy_account',
        'beecy_font',
        'stock',
    ],
    'assets': {
        'web.assets_backend': [
            'beecy_account_billing_note/static/src/css/layout.css',
            'beecy_account_billing_note/static/src/js/list_color.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/billing_note_report_templates.xml',
        'report/billing_note_report.xml',
        'views/account_billing_note_views.xml',
        'views/account_move_views.xml',
        'wizard/account_invoice_wizard_views.xml',
        'views/account_billing_note_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
