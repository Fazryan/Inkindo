# -*- coding: utf-8 -*-
{
    "name": "Payroll - Attandance Timesheet",
    "version": "1.01",
    "author": "Fits! Team - by PT.Fujicon Priangan Perdana",
    "license": "LGPL-3",
    "category": "Payroll",
    "website": "http://fujicon-japan.com",
    "depends": ["hr_payroll","hr","hr_attendance", "resource","hr_public_holidays","hr_timesheet_attendance"],
    "data": ['views/hr_view.xml',
             'views/payslip.xml',
             'views/calendar_views.xml',
             'views/hr_timesheet_sheet_view.xml',
             'views/asset_view.xml',
             'data/salary_rule_data.xml'
             
             ],
    'qweb': [
             'static/src/xml/*.xml'
             ],
    'installable': True,
    'auto_install': False,
}