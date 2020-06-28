import itertools
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta




class Payslip(models.Model):
    _inherit = 'hr.payslip'

    hours_timesheet = fields.Integer(string='Total Jam Timesheet',  states={'done': [('readonly', True)]},
                                     help='Total Timesheet hours approved for employee.')
    hours_attendance = fields.Integer(string='Total Jam Attendance',  states={'done': [('readonly', True)]},
                                     help='Total attendance hours approved for employee.')
    hours_difference = fields.Integer(string='Total Difference',  states={'done': [('readonly', True)]},
                                     help='Total Difference hours approved for employee.')
    
    kehadiran = fields.Integer('Kehadiran', states={'done': [('readonly', True)]})
    workday = fields.Integer('Workday (weekday)', states={'done': [('readonly', True)]})
    holiday = fields.Integer('Workday (Holiday)', states={'done': [('readonly', True)]})
    lbh_awal = fields.Integer('PLA', states={'done': [('readonly', True)]})
    terlambat = fields.Integer('Terlambat', states={'done': [('readonly', True)]})
    half_time = fields.Integer('HDL', states={'done': [('readonly', True)]})
    no_checkout = fields.Integer('No Checkout', states={'done': [('readonly', True)]})
    hari_calendar = fields.Integer('Workday', states={'done': [('readonly', True)]})
    leave = fields.Integer('Total Leave', states={'done': [('readonly', True)]})
    unapproved = fields.Integer('Unapproved', states={'done': [('readonly', True)]})
    site_office = fields.Integer('Site Office', states={'done': [('readonly', True)]})

    

    def compute_hours_timesheet(self, contract_id, date_from, date_to):
        if not contract_id:
            return {}
        env = self.env
        employee_id = contract_id.employee_id
        timesheet_object = env['hr_timesheet_sheet.sheet']
        hours_timesheet =  0.0
        hours_attendance =  0.0
        hours_difference =  0.0
        sheets = timesheet_object.search([
            ('employee_id', '=', employee_id.id),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
            ('state', '=', 'done')

        ])
        period_ids = []
        period_ids += [sheet.period_ids.ids for sheet in sheets]
        period_ids = list(itertools.chain.from_iterable(period_ids))
        if len(period_ids):
            self.env.cr.execute("""
                        SELECT
                               sum(total_timesheet) as total_timesheet,sum(total_attendance) as total_attendance, sum(total_difference) as total_difference 
                        FROM hr_timesheet_sheet_sheet_day
                        WHERE id IN %s
                    """, (tuple(period_ids),))
            data = self.env.cr.dictfetchall()
            for x in data:
                hours_timesheet = x.pop('total_timesheet')
                hours_attendance = x.pop('total_attendance')
                hours_difference = x.pop('total_difference')
        return {
            'hours_timesheet': hours_timesheet,
            'hours_attendance': hours_attendance,
            'hours_difference': hours_difference
            
        }


#     def compute_attendance(self, contract_id, date_from, date_to):
#         if not contract_id:
#             return {}
#         
#         employee_id = contract_id.employee_id
#         no_check = 0
#         #kehadiran = 0
#     
#         obj_absen = self.env['hr.attendance'].search([('employee_id','=',employee_id.id), ('check_in','>=',date_from), 
#                                                            ('check_in','<=',date_to)])
#         
#         #hadir = []
#         for ab in obj_absen :
#             #date_chek = datetime.strptime(ab.check_in,"%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
#             #checkin_str = date_chek.strftime('%Y-%m-%d')
#             #hadir.append(checkin_str)
#             #absen = list(set(hadir))
#             #kehadiran = len(absen)
#             no_check += ab.no_checkout 
#             
#             
# 
#         return {
#             #'kehadiran': kehadiran,
#             'no_checkout': no_check
#         }

    
  
    def compute_lambat(self, contract_id, date_from, date_to):
        if not contract_id:
            return {}
        
        date_f = fields.Datetime.from_string(date_from)
        year = int(date_f.year)
        date_t = fields.Datetime.from_string(date_to)
        year_to = int(date_t.year)
        terlambat = 0 
        lbh_awal = 0 
        half = 0
        kehadiran = 0
        no_check = 0
        workday = 0
        holiday = 0
        at_site = 0
        tot_leave = 0
        tot_unapp = 0
        
        employee_id = contract_id.employee_id
        obj_sheet = self.env['hr_timesheet_sheet.sheet'].search([('employee_id','=',employee_id.id), ('date_from','>=', date_from), 
                                                             ('date_to','<=',date_to), ('state', '=', 'done')])
        
#         obj_sheet_day = self.env['hr_timesheet_sheet.sheet.day'].search([('sheet_id.employee_id', '=', employee_id.id), ('name','>=',date_from), 
#                                                            ('name','<=',date_to),('sheet_id.state', '=', 'done')])
       
        
#         for sheet in obj_sheet :
#             for sheetday in sheet.period_ids:
#                 late = sheetday.first_sign_in.lambat
#                 awal = sheetday.last_sign_out.pla
#                 terlambat += late
#                 lbh_awal += awal
#                 half += sheetday.hdl
                
#         for sheet in obj_sheet :
#             for sheetday in sheet.period_ids:
#                 late = sheetday.first_sign_in.lambat
#                 awal = sheetday.last_sign_out.pla
#                 if sheetday.total_attendance > 4.0 and sheetday.total_attendance <= 7.0 :
#                     terlambat = 0
#                     lbh_awal = 0
#                     half += sheetday.hdl
#                 else :
#                     terlambat += late
#                     lbh_awal += awal
#                     half += sheetday.hdl

               
        for sheet in obj_sheet :
            obj_sheet_day = obj_sheet = self.env['hr_timesheet_sheet.sheet.day'].search([('sheet_id','=',sheet.id),('total_attendance','!=',0.0)])
            for sheetday in obj_sheet_day:
                terlambat += sheetday.lambat
                lbh_awal += sheetday.pla
                half += sheetday.hdl
                kehadiran += sheetday.hadir
                no_check += sheetday.no_checkout
                workday += sheetday.work_day
                holiday += sheetday.holiday
                at_site += sheetday.site_office
                
                
        holiday_obj=self.env['hr.holidays.public.line'].search([('year_id.year','=', year),('date','>=',date_f), 
                                                           ('date','<=',date_t)])
        
        holiday_next =self.env['hr.holidays.public.line'].search([('year_id.year','=', year_to),('date','>=',date_f), 
                                                           ('date','<=',date_t)])
         
     
        nb_of_days = (date_t - date_f).days + 1
        date_start = date_f - relativedelta(days=1)
        hari = []
        for day in range(0, nb_of_days):
            if not self.employee_id.calendar_id:
                hari_calendar = 0
            else :    
                working_day = self.employee_id.calendar_id.get_next_day(date_start + timedelta(days=day))
                hari.append(working_day)
                days = list(set(hari))
                workday_hadir = len(days)
                holiday_hadir = len(holiday_obj)
                holiday_to = len(holiday_next)
                hari_calendar = workday_hadir - (holiday_hadir + holiday_to)
                
                
        leave_obj=self.env['hr.holidays'].search([('employee_id','=',employee_id.id), ('date_from','>=', date_from), 
                                                             ('date_to','<=',date_to),('state','=','validate')])

        for x in leave_obj :
            tot_leave += x.number_of_days
        
        tot_unapp = hari_calendar  - (workday + tot_leave)
               
         
            
        return {
            'kehadiran': kehadiran,
            'terlambat': terlambat,
            'lbh_awal': lbh_awal,
            'half_time': half,
            'no_checkout': no_check,
            'workday': workday,
            'holiday': holiday,
            'site_office': at_site,
            'hari_calendar': hari_calendar,
            'leave': tot_leave,
            'unapproved':tot_unapp
        }
        
        

    @api.onchange('employee_id', 'date_from')
    def onchange_employee(self):
        super(Payslip, self).onchange_employee()
        if self.contract_id:
            datas = self.compute_hours_timesheet(self.contract_id, self.date_from, self.date_to)
            #absens = self.compute_attendance(self.contract_id, self.date_from, self.date_to)
            lates = self.compute_lambat(self.contract_id, self.date_from, self.date_to)
            self.hours_timesheet = datas.get('hours_timesheet') or 0.0
            self.hours_attendance = datas.get('hours_attendance') or 0.0
            self.hours_difference = datas.get('hours_difference') or 0.0
            self.kehadiran = lates.get('kehadiran') or 0.0
            self.no_checkout = lates.get('no_checkout') or 0.0
            self.terlambat = lates.get('terlambat') or 0.0
            self.lbh_awal = lates.get('lbh_awal') or 0.0
            self.half_time = lates.get('half_time') or 0.0
            self.workday = lates.get('workday') or 0.0
            self.holiday = lates.get('holiday') or 0.0
            self.site_office = lates.get('site_office') or 0.0
            self.hari_calendar = lates.get('hari_calendar') or 0.0
            self.leave = lates.get('leave') or 0.0
            self.unapproved = lates.get('unapproved') or 0.0
        return
    
    @api.multi
    def recompute_timeatt(self):
        if self.contract_id:
            datas = self.compute_hours_timesheet(self.contract_id, self.date_from, self.date_to)
            #absens = self.compute_attendance(self.contract_id, self.date_from, self.date_to)
            lates = self.compute_lambat(self.contract_id, self.date_from, self.date_to)
            self.hours_timesheet = datas.get('hours_timesheet') or 0.0
            self.hours_attendance = datas.get('hours_attendance') or 0.0
            self.hours_difference = datas.get('hours_difference') or 0.0
            self.kehadiran = lates.get('kehadiran') or 0.0
            self.no_checkout = lates.get('no_checkout') or 0.0
            self.terlambat = lates.get('terlambat') or 0.0
            self.lbh_awal = lates.get('lbh_awal') or 0.0
            self.half_time = lates.get('half_time') or 0.0
            self.workday = lates.get('workday') or 0.0
            self.holiday = lates.get('holiday') or 0.0
            self.site_office = lates.get('site_office') or 0.0
            self.hari_calendar = lates.get('hari_calendar') or 0.0
            self.leave = lates.get('leave') or 0.0
            self.unapproved = lates.get('unapproved') or 0.0
        return
       

