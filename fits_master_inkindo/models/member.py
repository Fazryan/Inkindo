# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
	_inherit = "res.partner"

	
	kewarganegaraan				= fields.Many2one('res.country',string='Kewarganegaraan')
	###DIPA 01
	nama_perusahaan				= fields.Char('Nama Perusahaan')
	bentuk_perusahaan			= fields.Char('Bentuk Perusahaan')
	status_perusahaan			= fields.Selection([('pusat','Pusat'),('cabang','Cabang')],string='Status Perusahan')
	###DIPA 03
	recomm_line 				= fields.One2many('recommendation','company_id')
	###DIPA 04
	sub_line 					= fields.One2many('subbidang','partner_id')
	sub_layanan_count 			= fields.Integer(compute='_compute_sub_layanan_count', string='# of SUBBIDANG LAYANAN')
	###DIPA 05 06
	owner_line 					= fields.One2many('owner','owner_id')
	###DIPA 07 07A
	tat_line 					= fields.One2many('tenaga.administrasi.tetap','company_id')
	###DIPA 08A 08B
	pjt_line 					= fields.One2many('pj.teknis','company_id')
	###DIPA 08A 08B
	ta_line 					= fields.One2many('tenaga.ahli','company_id')
	###DIPA 11 12 13
	asset_line 					= fields.One2many('asset','company_id')
	###DIPA 14 15 16 17
	office_line 				= fields.One2many('office','company_id')
	###AKte
	akte_line 					= fields.One2many('akte.perusahaan','company_id')
	###Dokumen
	dok_line 					= fields.One2many('dokumen.perusahaan','company_id')

	def _compute_sub_layanan_count(self):
		sublay_data = self.env['subbidang'].read_group(domain=[('partner_id', 'child_of', self.ids)],
													  fields=['partner_id'], groupby=['partner_id'])
		# read to keep the child/parent relation while aggregating the read_group result in the loop
		partner_child_ids = self.read(['child_ids'])
		mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in sublay_data])
		for partner in self:
			# let's obtain the partner id and all its child ids from the read up there
			partner_ids = filter(lambda r: r['id'] == partner.id, partner_child_ids)[0]
			partner_ids = [partner_ids.get('id')] + partner_ids.get('child_ids')
			# then we can sum for all the partner's child
			partner.sub_layanan_count = sum(mapped_data.get(child, 0) for child in partner_ids)

