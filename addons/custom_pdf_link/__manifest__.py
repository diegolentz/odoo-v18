# -*- coding: utf-8 -*-
{
    'name': "custom_pdf_link",
    'version': '1.0',
    'author': "My Company",
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_pdf_link/static/src/js/sign_button.js',
            'custom_pdf_link/static/src/xml/sign_button.xml',
        ],
    },
    'installable': True,
}