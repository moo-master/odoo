{
    'name': 'Beecy: Web report',
    'summary': '''
        - Report layout
    ''',
    'author': 'Roots',
    'category': 'Base',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Saravut S.',
    ],
    'depends': [
        'base_location',
        'web',
        'beecy_font',
    ],
    'assets': {
        'web._assets_common_scripts': [
            'beecy_web_report/static/src/js/force_new_page.js',
        ],
    },
    'data': [
        'views/report_templates.xml',
        'views/base_document_layout_views.xml',
        'data/report_rayout.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
