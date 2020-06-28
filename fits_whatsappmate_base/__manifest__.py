# -*- coding: utf-8 -*-
{
    "name": "Whatsapp Base - Using Whatsmate Api",
    "version": "1.01",
    "author": "Fits! Team - by PT. Fujicon Priangan Perdana",
    'images': ['static/description/icon.png'],
    "license": "",
    "category": "Custom",
    "website": "http://fujicon-japan.com",
    "depends": ["base"],
    "data": [
             'data/cron.xml',
             'security/ir.model.access.csv',
             'views/whatsapp_view.xml',
             'views/whatsapp_personal_view.xml',
             'views/konfig_view.xml',
             'views/log_wa_view.xml'
             ],
    'installable': True,
    'auto_install': False,
}