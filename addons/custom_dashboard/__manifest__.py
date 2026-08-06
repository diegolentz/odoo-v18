# -*- coding: utf-8 -*-
{
    'name': "custom_dashboard",

    'author': "ConfortM",
    'website': "https://www.confortm.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'board', 'legos18'],

    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/js/dashboard.js',
            'custom_dashboard/static/src/xml/dashboard.xml',
        ]
    }

}

