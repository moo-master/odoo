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
        'kbt_account_wht_ext',
    ],
    'data': [
        'report/receipt_tax_invoice_report.xml',
        'views/account_payment_term_views.xml',

    ]
}
