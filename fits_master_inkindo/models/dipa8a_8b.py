# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PJTeknis(models.Model):
	_name = "pj.teknis"
	_rec_name = 'partner_id'

	company_id			= fields.Many2one('res.partner', string="Company")
	partner_id			= fields.Many2one('res.partner', string="Karyawan")
	alamat_perusahaan	= fields.Char(string="Alamat Perusahaan")
	addres				= fields.Char(string="Alamat")
	kota				= fields.Char(string="Kota")
	kode_pos			= fields.Char(string="Kode Pos")
	no_surat_penetepan	= fields.Char(string="Nomor Surat Penetapan")
	tgl_penetapan		= fields.Date(string="Tanggal")
	pendidikan_terakhir	= fields.Many2one('edu.background', string="Pendidikan Terakhir")
	attachment_ids  	= fields.Many2many('ir.attachment',string='Attachments')

	@api.onchange('partner_id')
	def _onchange_addres(self):
		if self.partner_id:
			self.addres = self.partner_id.street
			self.kota = self.partner_id.city
			self.kode_pos = self.partner_id.zip
		