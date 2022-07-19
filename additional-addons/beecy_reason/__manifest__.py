{
    'name': 'Beecy: Reason',
    'summary': '''
        - Reason Master For Other Model
        - Create Reason From Other Model
        - Add Cancel and Reject Wizard
    ''',
    'author': 'Roots',
    'category': 'Base',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Santi T.',
        'Thotsaphorn Sri.'
    ],
    'depends': [
        'beecy_core_update',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_reason_views.xml',
        'wizard/cancel_reject_reason_views.xml',
        'views/res_reason_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
