# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DokumenPerusahaan(models.Model):
	_name = "dokumen.perusahaan"
	_rec_name = 'no_dokumen'

	company_id		= fields.Many2one('res.partner', string="Company")
	name 			= fields.Char('Nama Dokumen')
	no_dokumen		= fields.Char('Nomor Dokumen')
	start_date		= fields.Date('Tanggal Terbit')
	end_date		= fields.Date('Berlaku Hingga')
	category		= fields.Selection([('situ','SITU'),('npwp','NPWP'),('siujk','SIUJK'),('siup','SIUP'), 
							('ref_bank','Referensi Bank'),('tdr','Tanda Daftar Rekanan')],string='Kategori')
	attachment_ids  = fields.Many2many('ir.attachment',string='Attachments')
		