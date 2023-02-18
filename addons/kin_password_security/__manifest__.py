# Copyright 2015 LasLabs Inc.
# Copyright 2018 Modoolar <info@modoolar.com>.
# Copyright 2019 initOS GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Kin Password Security",
    "summary": "Allow admin to set password security requirements.",
    "version": "15.0.1.1.0",
    "author": "LasLabs, "
    "Kaushal Prajapati, "
    "Tecnativa, "
    "initOS GmbH, "
    "Omar Nasr, "
    "Odoo Community Association (OCA)",
    "category": "Base",
    "depends": [
        "auth_signup",
        "auth_password_policy_signup",
    ],
    "website": "https://github.com/OCA/server-auth",
    "external_dependencies": {
        "python": ["zxcvbn-python "],
    },
    'assets':  {
            'web.assets_common': [
                "password_security/static/src/js/password_gauge.js",
                "password_security/static/lib/zxcvbn/zxcvbn.min.js",
            ],
    },    
    "license": "LGPL-3",
    "data": [
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "security/res_users_pass_history.xml",
    ],
    "demo": [
        "demo/res_users.xml",
    ],
    "installable": True,
}
