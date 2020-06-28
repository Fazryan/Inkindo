# -*- coding: utf-8 -*-
from odoo import http

# class AsaProject(http.Controller):
#     @http.route('/fits_project/fits_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_project/fits_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_project.listing', {
#             'root': '/fits_project/fits_project',
#             'objects': http.request.env['fits_project.fits_project'].search([]),
#         })

#     @http.route('/fits_project/fits_project/objects/<model("fits_project.fits_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_project.object', {
#             'object': obj
#         })