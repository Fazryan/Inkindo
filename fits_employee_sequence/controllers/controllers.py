# -*- coding: utf-8 -*-
from odoo import http

# class FitsEmployeeSequence(http.Controller):
#     @http.route('/fits_employee_sequence/fits_employee_sequence/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_employee_sequence/fits_employee_sequence/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_employee_sequence.listing', {
#             'root': '/fits_employee_sequence/fits_employee_sequence',
#             'objects': http.request.env['fits_employee_sequence.fits_employee_sequence'].search([]),
#         })

#     @http.route('/fits_employee_sequence/fits_employee_sequence/objects/<model("fits_employee_sequence.fits_employee_sequence"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_employee_sequence.object', {
#             'object': obj
#         })