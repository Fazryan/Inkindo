# -*- coding: utf-8 -*-
from odoo import http

# class FitTaskReport(http.Controller):
#     @http.route('/fit_task_report/fit_task_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fit_task_report/fit_task_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fit_task_report.listing', {
#             'root': '/fit_task_report/fit_task_report',
#             'objects': http.request.env['fit_task_report.fit_task_report'].search([]),
#         })

#     @http.route('/fit_task_report/fit_task_report/objects/<model("fit_task_report.fit_task_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fit_task_report.object', {
#             'object': obj
#         })