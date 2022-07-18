{
    'name': 'Beecy: Partner Extension',
    'summary': """
        Partner Extension
    """,
    'author': 'Roots',
    'category': 'Partner',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Thotsaphorn Sri.',
    ],
    'depends': [
        'beecy_partner_title',
        'base_location'
    ],
    'data': [
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'beecy_partner_ext/static/src/legacy/scss/form_view.scss',
        ]
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
