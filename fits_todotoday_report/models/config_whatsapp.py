from odoo import _, api, fields, models, tools
import requests
from odoo.exceptions import UserError, Warning

class WaGroupTodoToday(models.Model):
    _name = 'wa.group.todotoday'
    _description = "WhatsApp Group To do Today"
    _rec_name ="group_name"
    
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp', default="whatsmate")
    group_id = fields.Char('GroupID')
    number_admin = fields.Char('Number Admin Group To do Today ')
    group_name = fields.Char('Group Name To do Today')
    group_manager = fields.Boolean(string = 'Is a Manager Group')
    is_employee = fields.Boolean(string = 'Is a Group Employee')
    
    @api.onchange('number_admin')
    def Onchange_no_wa(self):
        if self.number_admin:
            no = self.number_admin[0:3]
            print '==============no wa=============', no
            if no != '+62' :
                mobile = self.number_admin[1:]
                no_wa = '+62'+ mobile
                self.number_admin = no_wa
                
class Channel(models.Model):
    _inherit = 'mail.channel'
    
    wagroup_id = fields.Many2one('wa.group.todotoday', string="WhatsApp Group")