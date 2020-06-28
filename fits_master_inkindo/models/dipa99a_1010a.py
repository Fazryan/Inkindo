# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TenagaAhli(models.Model):
	_name = "tenaga.ahli"
	_rec_name = 'partner_id'

	partner_id			= fields.Many2one('res.partner', string="Karyawan")
	company_id			= fields.Many2one('res.partner', string="Company")
	alamat_perusahaan	= fields.Char(string="Alamat Perusahaan")
	addres				= fields.Char(string="Alamat")
	kota				= fields.Char(string="Kota")
	kode_pos			= fields.Char(string="Kode Pos")
	category			= fields.Selection([('tetap','Tetap'),('ttetap','Tidak Tetap')],string='Category')
	pendidikan_terakhir	= fields.Many2one('edu.background', string="Pendidikan Terakhir")
	thn_lulus			= fields.Date(string="Tahun Lulus")
	skill				= fields.Char(string="Keahlian")
	kewarganegaraan		= fields.Many2one('res.country',string="kewarganegaraan")
	attachment_ids  	= fields.Many2many('ir.attachment',string='Attachments')
	
	@api.onchange('partner_id')
	def _onchange_addres(self):
		if self.partner_id:
			self.addres = self.partner_id.street
			self.kota = self.partner_id.city
			self.kode_pos = self.partner_id.zip
			self.kewarganegaraan = self.partner_id.kewarganegaraan.id	