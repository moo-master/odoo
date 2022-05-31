{
    'name': 'KBT Business Type',
    'summary': '''
        Business Type.
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
        'kbt_sale_order_api',
        'account',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/business_type_form_views.xml',
        'views/sale_order_views.xml',
    ],
}
