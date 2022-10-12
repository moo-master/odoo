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
    'depends': [
        'kbt_business_type',
        'kbt_partner_ext',
        'kbt_account_wht_ext',
        'beecy_reason',
        # 'account_reports',
    ],
    'assets': {
        'web._assets_common_scripts': [
            'kbt_account_ext/static/src/js/force_new_page.js',
        ],
    },
    'data': [
        'data/paper_format.xml',
        'data/report_data.xml',
        'report/kbt_invoice_templates.xml',
        'report/kbt_report_template.xml',
        'report/receipt_tax_invoice_report.xml',
        'views/account_payment_term_views.xml',
        'views/account_move_views.xml',
    ]
}
