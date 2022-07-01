{
    'name': 'KBT Approval',
    'summary': '''
        KBT Approval
    ''',
    'author': 'Roots',
    'category': 'Company',
    'website': 'https://roots.tech',
    'version': '15.0.0.0.1',
    'license': 'LGPL-3',
    'contributors': [
        'Pachara P.',
    ],
    'depends': [
        'kbt_business_type',
        'hr',
        'beecy_reason',
    ],
    'data': [
        'views/org_level_menuitem.xml',
        'views/inherit_hr_employee_views.xml',
        'views/inherit_purchase_order_views.xml',
    ]
}
