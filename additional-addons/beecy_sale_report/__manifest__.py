{
    'name': 'Beecy: Sale Report',
    'summary': '''
        - Report Sale
    ''',
    'author': 'Roots',
    'category': 'Base',
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
        'beecy_core_update',
        'sale',
        'beecy_web_report'
    ],
    'data': [
        'report/sale_order_report_templates.xml',
        'report/sale_order_report_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
