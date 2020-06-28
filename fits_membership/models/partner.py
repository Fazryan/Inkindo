from odoo import api, fields, models, _
import time
import logging
_logger = logging.getLogger(__name__)

class partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    kota_id        = fields.Many2one(comodel_name="vit.kota", string="Kota/Kab", required=False, )


class kota(models.Model):
    _name = 'vit.kota'
    name = fields.Char('Kota/Kab', index=1)
    jenis = fields.Selection(string="Jenis", selection=[('kota', 'Kota'), ('kab', 'Kab.'), ], required=False, index=1)
    state_id = fields.Many2one(comodel_name="res.country.state", string="State", required=False, )

