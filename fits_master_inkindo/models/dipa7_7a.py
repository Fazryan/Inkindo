# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TenagaAdministrasiTetap(models.Model):
	_name = "tenaga.administrasi.tetap"
	_rec_name = 'partner_id'

	company_id			= fields.Many2one('res.partner', string="Company")
	alamat_perusahaan	= fields.Char(string="Alamat Perusahaan")
	partner_id			= fields.Many2one('res.partner', string="Karyawan")
	addres				= fields.Char(string="Alamat")
	kota				= fields.Char(string="Kota")
	kode_pos			= fields.Char(string="Kode Pos")
	no_surat_penetepan	= fields.Char(string="Nomor Surat Penetapan")
	position			= fields.Selection([('ku','Komisaris Utama'),('k','Komisaris'),('dirut','Direktur Utama'),
						('dir','Direktur'),('l','Lainnya')],string='Position')
	pendidikan_terakhir	= fields.Many2one('edu.background', string="Pendidikan Terakhir")
	skill				= fields.Char(string="Keahlian")
	attachment_ids  	= fields.Many2many('ir.attachment',string='Attachments')

	@api.onchange('partner_id')
	def _onchange_addres(self):
		if self.partner_id:
			self.addres = self.partner_id.street
			self.kota = self.partner_id.city
			self.kode_pos = self.partner_id.zip

		