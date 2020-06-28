from odoo import _, api, fields, models, tools
import requests
from odoo.exceptions import UserError, Warning

    
class Department(models.Model):
    _inherit = 'hr.department'
    
    wagroup_manager     = fields.Many2one('wa.group.todotoday', string="WhatsApp Group Manager")
    wagroup_department  = fields.Many2one('wa.group.todotoday', string="WhatsApp Group Emloyee")
    
    
    
    