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
        'mail',
        'beecy_reason',
        'account_accountant',
        'sale_management'
    ],
    'data': [
        'data/approval_email_template.xml',
        'data/mail_activity_data.xml',
        'security/ir.model.access.csv',
        'views/org_level_menuitem.xml',
        'views/inherit_hr_employee_views.xml',
        'views/inherit_purchase_order_views.xml',
        'views/inherit_sale_order_views.xml',
        'views/inherit_account_move_views.xml',
        'views/user_approval_line_views.xml',
        'views/res_config_settings_view.xml',
        'views/account_journal_view.xml'
    ]
}
