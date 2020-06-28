# -*- coding: utf-8 -*-
from odoo import http

# class AsaHtmlInTree(http.Controller):
#     @http.route('/asa_html_in_tree/asa_html_in_tree/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asa_html_in_tree/asa_html_in_tree/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asa_html_in_tree.listing', {
#             'root': '/asa_html_in_tree/asa_html_in_tree',
#             'objects': http.request.env['asa_html_in_tree.asa_html_in_tree'].search([]),
#         })

#     @http.route('/asa_html_in_tree/asa_html_in_tree/objects/<model("asa_html_in_tree.asa_html_in_tree"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asa_html_in_tree.object', {
#             'object': obj
#         })