# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence', default=10)