# -*- coding: utf-8 -*-
from odoo import http

# class FitsAttdtime2payroll(http.Controller):
#     @http.route('/fits_attdtime2payroll/fits_attdtime2payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_attdtime2payroll/fits_attdtime2payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_attdtime2payroll.listing', {
#             'root': '/fits_attdtime2payroll/fits_attdtime2payroll',
#             'objects': http.request.env['fits_attdtime2payroll.fits_attdtime2payroll'].search([]),
#         })

#     @http.route('/fits_attdtime2payroll/fits_attdtime2payroll/objects/<model("fits_attdtime2payroll.fits_attdtime2payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_attdtime2payroll.object', {
#             'object': obj
#         })