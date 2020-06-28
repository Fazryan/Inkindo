# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SubbidangLayanan(models.Model):
	_name = 'subbidang'
	_rec_name = 'kode_sb'
	partner_id		= fields.Many2one('res.partner', string='Company')
	kode_sb			= fields.Many2one('master.subbidang', string="KODE SB")
	bidang			= fields.Char(string="BIDANG")
	subbidang		= fields.Char(string="SUBBIDANG")
	start_date		= fields.Date(string='Tanggal Berlaku')
	end_date		= fields.Date(string='Tanggal Berakhir')
	attachment_ids  = fields.Many2many('ir.attachment',string='Attachments')
	pjt_id				= fields.Many2one('res.partner',string = 'PJT')
	classification_id	= fields.Many2one('classification', string = 'Klasifikasi')
	sector_id = fields.Char('SEKTOR', related='kode_sb.sector_id.name', readonly="True")

	@api.onchange('kode_sb')
	def _onchange_addres(self):
		if self.kode_sb:
			self.bidang = self.kode_sb.bidang	
			self.subbidang = self.kode_sb.subbidang
		
class Sector(models.Model):
	_name='sector'
	name	=	fields.Char("SEKTOR")
	
class classification(models.Model):
	_name='classification'
	name	=	fields.Char('Klasifikasi')


class MasterSubbidang(models.Model):
	_name = 'master.subbidang'
	_rec_name = 'kode_sb'

	kode_sb			= fields.Char(string="KODE SB")
	bidang			= fields.Char(string="BIDANG")
	subbidang		= fields.Char(string="SUBBIDANG")
	attachment_ids  = attachment_ids = fields.Many2many('ir.attachment',string='Attachments')
	
	sector_id = fields.Many2one('sector', string="SEKTOR")	

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search([('subbidang', 'ilike', name + "%")] + args, limit=limit)
			if not recs:
				recs = self.search([('kode_sb', operator, name)] + args, limit=limit)
		else:
			recs = self.search(args, limit=limit)
		return recs.name_get()

	@api.one
	def name_get(self):
		return (self.id, self._get_full_name()[0])

	@api.one
	def _get_full_name(self):
		if self.kode_sb:
			if not self.subbidang:
				return '['+self.kode_sb +'] '
			else:
				return '['+self.kode_sb +'] '+self.subbidang
		return self.kode_sb

		