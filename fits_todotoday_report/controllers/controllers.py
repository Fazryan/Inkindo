# -*- coding: utf-8 -*-
from odoo import http

# class FitsTodotodayReport(http.Controller):
#     @http.route('/fits_todotoday_report/fits_todotoday_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_todotoday_report/fits_todotoday_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_todotoday_report.listing', {
#             'root': '/fits_todotoday_report/fits_todotoday_report',
#             'objects': http.request.env['fits_todotoday_report.fits_todotoday_report'].search([]),
#         })

#     @http.route('/fits_todotoday_report/fits_todotoday_report/objects/<model("fits_todotoday_report.fits_todotoday_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_todotoday_report.object', {
#             'object': obj
#         })