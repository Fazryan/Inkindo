from odoo import api, fields, models, _


class MessageWhatsapp(models.Model):
    _name = "fits.wa.template"
    
    name = fields.Char(required=True, string='Template Name')
    type = fields.Selection([('tdt','Reminder To do Today'), ('att','Reminder Attandance'), ('no_cekout','Reminder No CheckOut')],
                                   required=True, string='Type Template')
    isi_pesan = fields.Text(required=True, string='Message')
    cek_in_out = fields.Selection([('cekin','Cek In'), ('cekout','Cek Out')], string='Action')