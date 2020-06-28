# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Asset(models.Model):
	_name = "asset"
	_rec_name = 'name'

	company_id			= fields.Many2one('res.partner', string="Company")
	name				= fields.Char(string="Jenis Alat")
	category			= fields.Selection([('kantor','Peralatan Kantor'),('studio','Peralatan Studio'),
							('lapangan','Peralatan Lapangan')],string='Category')
	qty					= fields.Float(string="Quantity")
	status				= fields.Selection([('ms','Milik Sendiri'),('s','Sewa')],string='Status')
	attachment_ids  	= fields.Many2many('ir.attachment',string='Attachments')
