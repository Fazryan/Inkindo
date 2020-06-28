# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Owner(models.Model):
	_name = "owner"
	_rec_name = 'partner_id'

	owner_id				= fields.Many2one('res.partner')
	partner_id				= fields.Many2one('res.partner', string="Owner")
	addres					= fields.Char(string="Alamat")
	citizenship				= fields.Many2one('res.country',string="Kewarganegaraan")
	pemilik_saham_rp		= fields.Float(string="Saham (Rupiah)")
	pemilik_saham_persen	= fields.Float(string="Saham (%)")
	position				= fields.Selection([('ku','Komisaris Utama'),('k','Komisaris'),('dirut','Direktur Utama'),
								('dir','Direktur'),('l','Lainnya')],string='Position')
	keterangan				= fields.Text(string="Keterangan")
	attachment_ids  = fields.Many2many('ir.attachment',string='Attachments')


	@api.onchange('partner_id')
	def _onchange_addres(self):
		if self.partner_id:
			self.addres = self.partner_id.street
			self.citizenship = self.partner_id.kewarganegaraan.id	
		