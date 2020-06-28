# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class asa_html_in_tree(models.Model):
#     _name = 'asa_html_in_tree.asa_html_in_tree'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100