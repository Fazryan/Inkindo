# -*- coding: utf-8 -*-
from odoo import http

# class FitsProductDl(http.Controller):
#     @http.route('/fits_product_dl/fits_product_dl/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_product_dl/fits_product_dl/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_product_dl.listing', {
#             'root': '/fits_product_dl/fits_product_dl',
#             'objects': http.request.env['fits_product_dl.fits_product_dl'].search([]),
#         })

#     @http.route('/fits_product_dl/fits_product_dl/objects/<model("fits_product_dl.fits_product_dl"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_product_dl.object', {
#             'object': obj
#         })