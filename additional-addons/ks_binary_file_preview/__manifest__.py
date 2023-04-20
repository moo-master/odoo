# -*- coding: utf-8 -*-
{
    'name': "Kin Document Preview",

    'license': 'LGPL-3',

    'category': 'Tools',
    
    'version': '15.0.1.0.3',

    'depends': ['base', 'web', 'mail','hr'],

    'data': [
            'views/ks_user.xml',
        ],

    'assets': {
        'web.assets_backend': [
            '/ks_binary_file_preview/static/src/js/ks_binary_preview.js',
            '/ks_binary_file_preview/static/src/js/widget/ksListDocumentViewer.js',

        ],

        'web.assets_qweb': ['ks_binary_file_preview/static/src/xml/ks_binary_preview.xml',
                            'ks_binary_file_preview/static/src/js/widget/ksListDocumentViewer.xml',
                            ],
    },
}
