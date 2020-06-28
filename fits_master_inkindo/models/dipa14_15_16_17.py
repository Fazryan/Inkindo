# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Office(models.Model):
	_name = "office"
	_rec_name = 'name'

	company_id		= fields.Many2one('res.partner', string="Company")
	name			= fields.Char(string="Nama Dokumen")
	category		= fields.Selection([('slk','Sketsa Lokasi Kantor'),('dk','Denah Kantor'),('fdk','Foto Denah Kantor')
							,('frdk','Foto Ruang Dalam Kantor')],string='Category')
	addres			= fields.Char(related='company_id.street',string="Alamat Perusahaan")
	attachment_ids  = fields.Many2many('ir.attachment',string='Attachments')
		