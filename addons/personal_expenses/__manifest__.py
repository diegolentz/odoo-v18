# -*- coding: utf-8 -*-
{
    'name': "personal_expenses",

    'summary': "Personal expenses manager",

    'description': """
Module to manage personal expenses
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'web', 'website'],   # web es importante para tocar el backend

    'data': [
        'security/ir.model.access.csv',
        'views/expense_views.xml',
        'views/expense_action.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'personal_expenses/static/src/xml/custom_navbar.xml',
            'personal_expenses/static/src/css/navbar_hide.css',
            
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
}