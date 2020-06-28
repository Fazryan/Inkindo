# -*- coding: utf-8 -*-
from odoo import http

# class FitsInvoiceToTask(http.Controller):
#     @http.route('/fits_invoice_to_task/fits_invoice_to_task/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_invoice_to_task/fits_invoice_to_task/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_invoice_to_task.listing', {
#             'root': '/fits_invoice_to_task/fits_invoice_to_task',
#             'objects': http.request.env['fits_invoice_to_task.fits_invoice_to_task'].search([]),
#         })

#     @http.route('/fits_invoice_to_task/fits_invoice_to_task/objects/<model("fits_invoice_to_task.fits_invoice_to_task"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_invoice_to_task.object', {
#             'object': obj
#         })