# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    invoice_line_id = fields.Many2one('account.invoice.line', string = 'Account Invoice Line')

    @api.multi
    def unlink(self):
        if any(task.invoice_line_id for task in self):
            raise ValidationError(_('You cannot delete a task related to a Account Invoice'))
        return super(ProjectTask, self).unlink()


