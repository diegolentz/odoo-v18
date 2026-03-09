{
    "name": "Custom CRM",
    "depends": ["crm", "web"],
    "data": [
        "filter.xml","actions.xml","kanban.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "custom_crm/static/src/css/hide_systray.css",
            
        ],
    },
}