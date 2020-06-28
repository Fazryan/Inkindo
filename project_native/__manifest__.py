# -*- coding: utf-8 -*-
{
    "name": """Gantt Native view for Projects""",
    "summary": """Added support Gantt""",
    "category": "Project",
    "images": ['static/description/icon.png'],
    "version": "10.17.1.12.2",
    "description": """
    Update 1: Add Milestone icon on Gantt bar.
    Update 2: Add Progress Bar and Task Nanme on Gantt.
    Update 3: Add New Scale.
    Update 4: link between tasks with arrows.
    Update 5: Gantt for Sub-task View.
    Update 6: Done on Gantt, Ghosts bar on Gantt. Manufacture support.
    fix: Sorted if more that 10.
    Update 7: Autosheduling support and constraint for tasks.
    fix: Can't change project if predecessor or parent_id for sub-task exist
    fix: predessort - task_id if null.

""",
    "author": "Viktor Vorobjov",
    "license": "OPL-1",
    "website": "https://straga.github.io",
    "support": "vostraga@gmail.com",

    "depends": [
        "project",
        "hr_timesheet",
        "web_gantt_native",
        "web_widget_time_delta"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/project_task_view.xml',
        'security/ir.model.access.csv',
    ],
    "qweb": [],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
    "application": False,
}