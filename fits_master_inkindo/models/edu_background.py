# -*- coding: utf-8 -*-

from odoo import models, fields, api

#line
class EduBackgrounf(models.Model):
	_name = "edu.background"
	_rec_name = 'jenjang' 


	jenjang		= fields.Char(string="Jenjang")
	uraian		= fields.Char(string="Uraian")