{
    'name': 'KBT Account Ext',
    'summary': '''
        KBT Account ext.
    ''',
    'author': 'Roots',
    'category': 'Company',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [
            'bahttext',
        ],
    },
    'contributors': [
        'Pachara P.',
    ],
    'assets': {
        'web.assets_backend': [
            'kbt_account_ext/static/src/js/account_group_selection.js',
        ],
    },
    'depends': [
        'kbt_business_type',
        'kbt_partner_ext',
        'kbt_account_wht_ext',
        'beecy_reason',
        'report_xlsx_helper',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'data/report_data.xml',
        'data/account_group_data.xml',
        'report/kbt_invoice_templates.xml',
        'report/kbt_report_template.xml',
        'report/receipt_tax_invoice_report.xml',
        'report/profit_loss_report_xlsx.xml',
        'views/account_payment_term_views.xml',
        'views/account_move_views.xml',
        'views/account_views.xml',
        'views/account_account_group_views.xml',
        'wizards/wizard_profit_loss_views.xml',
    ]
}
