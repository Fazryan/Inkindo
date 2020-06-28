# -*- coding: utf-8 -*-
{
    "name": """Web Widget Time Delta""",
    "summary": """Added Time Delta Human friedly for From and List""",
    "category": "Project",
    "images": ['static/description/icon.png'],
    "version": "10.17.1.0.0",
    "description": """

            For Form View - added = widget="time_delta"
            For List View - added = widget="time_delta_list"
            
            plan_duration = fields.Integer(string='Plan Duration') store in seconds.

    """,

    "author": "Viktor Vorobjov",
    "license": "LGPL-3",
    "website": "https://straga.github.io",
    "support": "vostraga@gmail.com",
    "price": 0.00,
    "currency": "EUR",

    "depends": [
        "web"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'view/web_widget_time_delta_view.xml'
    ],
    "qweb": [
        'static/src/xml/widget.xml',

    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
    "application": False,
}
