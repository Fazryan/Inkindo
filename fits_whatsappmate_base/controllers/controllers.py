# -*- coding: utf-8 -*-
from odoo import http

# class FitsWhatsappmateBase(http.Controller):
#     @http.route('/fits_whatsappmate_base/fits_whatsappmate_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_whatsappmate_base/fits_whatsappmate_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_whatsappmate_base.listing', {
#             'root': '/fits_whatsappmate_base/fits_whatsappmate_base',
#             'objects': http.request.env['fits_whatsappmate_base.fits_whatsappmate_base'].search([]),
#         })

#     @http.route('/fits_whatsappmate_base/fits_whatsappmate_base/objects/<model("fits_whatsappmate_base.fits_whatsappmate_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_whatsappmate_base.object', {
#             'object': obj
#         })