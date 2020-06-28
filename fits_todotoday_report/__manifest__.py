# -*- coding: utf-8 -*-
{
    "name": "Project - To do Today Report",
    "version": "1.01",
    "author": "Fits! Team - by PT.Fujicon Priangan Perdana",
    "license": "",
    "category": "Project",
    "website": "http://fujicon-japan.com",
    "depends": ["hr_attendance","fit_task_report", "project","asa_project"],
    "data": [
             'security/ir.model.access.csv',
             'data/cron.xml',
             'data/seq_todo.xml',
             'wizard/send_report_view.xml',
             'wizard/finish_report_view.xml',
             'wizard/cancel_report_view.xml',
             'views/todo_today_view.xml',
             'views/project_view.xml',
             'views/config_whatsapp_view.xml',
             'views/log_todo_today_view.xml',
             'views/template_wa_view.xml',
             'views/employee_view.xml',
             #'views/todo_today_line_view.xml',
            
           
             ],
    'installable': True,
    'auto_install': False,
}