# -*- coding: utf-8 -*-
{
    'name': "kin_technical_custom",

    'summary': """
        Technical custom groups for support users role.
        """,

    'description': """
        Technical custom groups for support users role.
    """,

    'author': "Nattikan c.",
    'website': "https://www.kasetinno.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/kin_technical_custom_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
