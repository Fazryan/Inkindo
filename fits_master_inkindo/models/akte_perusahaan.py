# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AktePerusahaan(models.Model):
	_name = "akte.perusahaan"
	_rec_name = 'no_notaris'

	company_id			= fields.Many2one('res.partner', string="Company")
	nama_notaris		= fields.Char('Nama Notaris')
	no_notaris			= fields.Char('No. Notaris')
	tgl_notaris			= fields.Date('Tgl/Bln/Thn Notaris')
	pendaf_pn			= fields.Char('Pendaftaran di Pengadilan Negeri')
	no_pn 				= fields.Char('No. Pengadilan')
	tgl_pn 				= fields.Date('Tgl/Bln/Thn Pengadilan')
	no_pengesahan		= fields.Char('No. Pengesahan')
	tgl_pengesahan		= fields.Date('Tgl/Bln/Thn Pengesahan')
	jenis_akte			= fields.Selection([('pn','Akte Pendirian'),('ph','Akte Perubahan')],string='Jenis Akte')
	attachment_ids  	= fields.Many2many('ir.attachment',string='Attachments')
		