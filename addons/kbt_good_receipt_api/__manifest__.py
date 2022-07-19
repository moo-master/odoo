{
    'name': 'KBT Good Receipt Api',
    'summary': '''
        KBT Good Receipt Api
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
        'kbt_stock_picking_ext',
        'purchase_stock',
        'kbt_api_base',
    ],
    'data': [
        'views/inherit_view_picking_form.xml',
    ]
}
