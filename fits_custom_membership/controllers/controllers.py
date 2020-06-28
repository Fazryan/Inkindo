# -*- coding: utf-8 -*-
from odoo import http

# class FitsCustomMembership(http.Controller):
#     @http.route('/fits_custom_membership/fits_custom_membership/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_custom_membership/fits_custom_membership/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_custom_membership.listing', {
#             'root': '/fits_custom_membership/fits_custom_membership',
#             'objects': http.request.env['fits_custom_membership.fits_custom_membership'].search([]),
#         })

#     @http.route('/fits_custom_membership/fits_custom_membership/objects/<model("fits_custom_membership.fits_custom_membership"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_custom_membership.object', {
#             'object': obj
#         })