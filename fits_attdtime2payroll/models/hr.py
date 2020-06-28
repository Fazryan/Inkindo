# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Attendence(models.Model):
    _inherit = 'hr.attendance'
    
    month_attendance = fields.Char('Bulan',compute='_compute_bulan', store=False)
    tgl_attendance = fields.Char('Tanggal',compute='_compute_bulan', store=False)
    no_checkout = fields.Integer('No Checout', compute ='_compute_nocheck')
    checkin_float = fields.Float('CheckIn Jam',compute='_compute_jam', store=False)
    checkout_float = fields.Float('CheckOut Jam',compute='_compute_jam', store=False)
    hari = fields.Char('Hari', compute='_compute_hari', store=False)
    lambat = fields.Integer('Telambat', compute ='_compute_lambat')
    pla = fields.Integer('PLA', compute ='_compute_pla')
    hari_libur = fields.Integer('Holyday', compute ='_compute_holyday')
    hari_kerja = fields.Integer('Work Day', compute ='_compute_holyday')
    site_office = fields.Boolean(string='Site Office')
    
    
    @api.one
    @api.depends('check_in')
    def _compute_hari(self) :
        checkin = datetime.strptime(self.check_in, "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
        hari_checkin = checkin.strftime('%A')
        if hari_checkin == 'Monday':
            self.hari = '0'
        elif hari_checkin == 'Tuesday':
            self.hari = '1'
        elif hari_checkin == 'Wednesday':
            self.hari = '2'
        elif hari_checkin == 'Thursday':
            self.hari = '3'
        elif hari_checkin == 'Friday':
            self.hari = '4'
        elif hari_checkin == 'Saturday':
            self.hari = '5'
        elif hari_checkin == 'Sunday':
            self.hari = '6'    
        else :
            self.hari = 'uncategories'
            
            
    @api.one
    @api.depends('check_in')
    def _compute_holyday(self) :
        checkin = datetime.strptime(self.check_in, "%Y-%m-%d %H:%M:%S")
        year_checkin = checkin.strftime('%Y')
        year = int(year_checkin)
       
        calendar= self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.calendar_id.id)])
        holiday_obj=self.env['hr.holidays.public.line'].search([('year_id.year','=', year)])
        
        tgl_holiday = []
        for h in holiday_obj :
            tgl_holiday.append(h.date)
            if self.tgl_attendance in tgl_holiday :
                self.hari_kerja = 0
                self.hari_libur = 1
            else :
                day_calendar = []
                for day in calendar :
                    day_calendar.append(day.dayofweek)
                    hari_hari = list(set(day_calendar))
                    if self.hari in hari_hari :
                        self.hari_kerja = 1
                        self.hari_libur = 0
                    else :
                        self.hari_kerja = 0
                        self.hari_libur = 1
    
    
    @api.one
    @api.depends('check_in','check_out')
    def _compute_jam(self) :
        #self.checkin_float = float(self.check_in[11:13])+ 7
        #self.checkout_float = float(self.check_out[11:13])+ 7
        checkout = False
        if  self.check_out:
            checkin = datetime.strptime(self.check_in, "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
            checkout  = datetime.strptime(self.check_out, "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
            checkin_jam = checkin.strftime('%H.%M')
            checkout_jam = checkout.strftime('%H.%M')
            self.checkin_float = float(checkin_jam)
            self.checkout_float = float(checkout_jam)  
       
    
    @api.one
    @api.depends('check_in','check_out')
    def _compute_nocheck(self) :
        cek_out = False
        if  self.check_out:
            cek_in = datetime.strptime(self.check_in, "%Y-%m-%d %H:%M:%S")+ timedelta(hours=7)
            cek_out = datetime.strptime(self.check_out, "%Y-%m-%d %H:%M:%S")+ timedelta(hours=7)
            tgl_checkin = cek_in.strftime('%Y-%m-%d')
            tgl_checkout = cek_out.strftime('%Y-%m-%d')
            if tgl_checkout != tgl_checkin :
                self.no_checkout = 1
            else:
                self.no_checkout = 0
    
    
    @api.one
    @api.depends('check_in')
    def _compute_bulan(self) :
        #self.month_attendance = int(self.check_in[5:7])
        month_year = datetime.strptime(self.check_in, "%Y-%m-%d %H:%M:%S")+ timedelta(hours=7)
        self.month_attendance = month_year.strftime('%Y-%m')
        self.tgl_attendance = month_year.strftime('%Y-%m-%d')
        
    @api.one
    @api.depends('check_in')
    def _compute_lambat(self) :
        calendar_check = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.calendar_id.id),
                                                                      ('dayofweek','=',self.hari),('date_from','=', False )])
        
        calendar_tgl = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.calendar_id.id),
                                                                      ('dayofweek','=',self.hari),
                                                                      ('date_from','!=', False )])
        
        
        masuk = []
        if len(calendar_tgl) :
            for tgl in calendar_tgl:
                if self.check_in >= tgl.date_from and self.check_in <= tgl.date_to :            
                    masuk.append(tgl.hours_from_float) 
                    jam_min = min(masuk)
                    if self.checkin_float > jam_min :
                            self.lambat = 1
                    else :
                            self.lambat = 0
                else :
                    masuk_jam = []
                    for o in calendar_check :
                        masuk_jam.append(o.hours_from_float)
                        min_jam1 = min(masuk_jam)
                        if self.checkin_float > min_jam1 :
                            self.lambat = 1
                        else :
                            self.lambat = 0
                    
        else :
            jam_masuk = []
            for jam in calendar_check :
                jam_masuk.append(jam.hours_from_float)
                min_jam = min(jam_masuk)
                if self.checkin_float > min_jam :
                    self.lambat = 1
                else :
                    self.lambat = 0
                    
                    
                         
        
        
        
        
        
        
#         jam_masuk = []
#         for jam in calendar_check :
#             jam_masuk.append(jam.hour_from)
#             min_jam = min(jam_masuk)
#             print '============min=============', min_jam
#             if self.checkin_float > min_jam :
#                 self.lambat = 1
#             else :
#                 self.lambat = 0
       
        
        
       
#         for jam in calendar_check :
#             if jam.date_from :
#                 masuk = []
#                 if self.check_in >= jam.date_from and self.check_in <= jam.date_to:
#                     print '=============jammmmm=========', jam.hour_from
#                     
#                     
#             if not jam.date_from :
#                 jam_masuk = []
#                 jam_masuk.append(jam.hour_from)
#                 min_jam = min(jam_masuk)
#                 print '============min=============', min_jam , jam.hour_from
#                 if self.checkin_float > min_jam :
#                     self.lambat = 1
#                 else :
#                     self.lambat = 0
                
    @api.one
    @api.depends('check_out')
    def _compute_pla(self) :
        calendar_check = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.calendar_id.id),
                                                                      ('dayofweek','=',self.hari), ('date_from','=', False )])
        
        calendar_tgl = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.calendar_id.id),
                                                                      ('dayofweek','=',self.hari),
                                                                      ('date_from','!=', False )])
        
        
        keluar = []
        if len(calendar_tgl) :
            for tgl in calendar_tgl:
                if self.check_out >= tgl.date_from and self.check_out <= tgl.date_to :               
                    keluar.append(tgl.hours_to_float) 
                    jam_max = max(keluar)
                    if self.checkout_float < jam_max :
                            self.pla = 1
                    else :
                            self.pla = 0
                else :
                    keluar_jam = []
                    for o in calendar_check :
                        keluar_jam.append(o.hours_to_float)
                        max_jam1 = max(keluar_jam)
                        if self.checkout_float < max_jam1 :
                            self.pla = 1
                        else :
                            self.pla = 0
                    
        else :
            jam_keluar = []
            for jam in calendar_check :
                jam_keluar.append(jam.hours_to_float)
                max_jam = max(jam_keluar)
                if self.checkout_float < max_jam :
                    self.pla = 1
                else :
                    self.pla = 0
        
        
       
      
    
