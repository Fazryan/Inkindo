# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Recommendation(models.Model):
	_name = "recommendation"
	_rec_name = 'name'

	company_id		= fields.Many2one('res.partner', string="Company")
	partner_id		= fields.Many2one('res.partner', string="Karyawan")
	name			= fields.Char(string="Nomor Surat")
	date			= fields.Date(string="Tanggal")
	position		= fields.Selection([('ku','Komisaris Utama'),('k','Komisaris'),('dirut','Direktur Utama'),
						('dir','Direktur'),('l','Lainnya')],string='Position')
	attachment_ids  = fields.Many2many('ir.attachment',string='Attachments')



		