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
        'sale',
        'account',
        'purchase',
        'kbt_core_update'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/business_type_form_views.xml',
        'views/inherit_purchase_order_views.xml',
        'views/inherit_sale_order_views.xml',
    ],
}
