{
    'name': 'Beecy: Account Withholding Tax',
    'summary': '''
        Beecy Withholding Tax
    ''',
    'author': 'Roots',
    'category': 'Accounting/Accounting',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Suwan S.',
    ],
    'external_dependencies': {
        'python': [
            'bahttext',
        ],
    },
    'depends': [
        'beecy_date_range_sequence',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/account_wht_format_report.xml',
        'report/account_wht_format_report_templates.xml',
        'report/account_wht_substitute_report_templates.xml',
        'report/account_wht_format_substitute_report.xml',
        'report/account_wht_certificate_report_templates.xml',
        'report/account_wht_format_certificate_report.xml',
        'report/account_pnd3_report.xml',
        'report/account_pnd53_report.xml',
        'views/account_wht_type_view.xml',
        'views/product_template_view.xml',
        'views/account_move_views.xml',
        'views/account_wht_view.xml',
        'data/ir_sequence_data.xml',
        'views/account_wht_pnd_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'beecy_account_wht/static/src/css/style_report.css',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
