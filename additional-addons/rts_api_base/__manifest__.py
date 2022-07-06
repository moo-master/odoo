{
    'name': "Roots - API Base",
    'summary': '''Interface Base''',
    'author': "Tewtawat C. & Isares S., Roots",
    'website': "https://roots.tech",
    'version': '15.0.1.1.0',
    'external_dependencies': {
        'python': ['requests', 'validators']
    },
    'depends': [
        'mail',
    ],
    'data': [
        'data/ir_config_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'wizards/api_service_try_wizard_view.xml',
        'views/api_logs_view.xml',
        'views/api_service_route_view.xml',
        'views/api_service_view.xml',
        'views/menu_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rts_api_base/static/src/scss/style.scss'
        ]
    },
    'category': 'Base',
    'application': True,
}
