from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    
    street = fields.Char(track_visibility='onchange')
    website = fields.Char(help="Website of Partner or Company", track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    comment = fields.Text(string='Notes', track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    #no_wa = fields.Char("WhatsApp Number", track_visibility='onchange')