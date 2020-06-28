# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    #@api.constrains('timesheet_cost')
    #def _check_cost(self):
        #if self.timesheet_cost == 0:
            #raise exceptions.ValidationError("Timesheet Cost should not be 0.....!!")