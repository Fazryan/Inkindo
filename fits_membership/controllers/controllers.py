# -*- coding: utf-8 -*-
from odoo import http

# class FitsMembership(http.Controller):
#     @http.route('/fits_membership/fits_membership/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_membership/fits_membership/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_membership.listing', {
#             'root': '/fits_membership/fits_membership',
#             'objects': http.request.env['fits_membership.fits_membership'].search([]),
#         })

#     @http.route('/fits_membership/fits_membership/objects/<model("fits_membership.fits_membership"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_membership.object', {
#             'object': obj
#         })