from odoo import fields, models, api
import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrTimesheetSheetSheetDay(models.Model):
    _inherit = "hr_timesheet_sheet.sheet.day"

    @api.multi
    def _convert_datetime_utc(self, employee, dt):
        self.ensure_one()
        convert_dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)

        if employee.user_id.tz:
            tz = pytz.timezone(employee.user_id.tz)
        else:
            return False

        convert_tz = tz.localize(convert_dt)
        convert_utc = convert_tz.astimezone(pytz.utc)
        format_utc = datetime.strftime(
            convert_utc,
            DEFAULT_SERVER_DATETIME_FORMAT
        )

        return format_utc

    @api.multi
    def _compute_summary_info(self):
        obj_hr_attendance = self.env['hr.attendance']
        for sheet_day in self:
            first_sign_in = False
            last_sign_out = False

            employee = sheet_day.sheet_id.employee_id
            utc_date_1 = sheet_day._convert_datetime_utc(
                dt=sheet_day.name + ' 00:00:00',
                employee=employee
            )
            utc_date_2 = sheet_day._convert_datetime_utc(
                dt=sheet_day.name + ' 23:59:59',
                employee=employee
            )
            if utc_date_1 and utc_date_2:
                criteria_first_sign_in = [
                    ('sheet_id', '=', sheet_day.sheet_id.id),
                    ('check_in', '>=', utc_date_1),
                    ('check_in', '<=', utc_date_2),
                ]
                list_sign_in =\
                    obj_hr_attendance.search(
                        criteria_first_sign_in,
                        order='check_in asc'
                    )
                if list_sign_in:
                    first_sign_in = list_sign_in[0].id
                

                criteria_last_sign_out = [
                    ('sheet_id', '=', sheet_day.sheet_id.id),
                    ('check_out', '>=', utc_date_1),
                    ('check_out', '<=', utc_date_2),
                ]
                list_sign_out =\
                    obj_hr_attendance.search(
                        criteria_last_sign_out,
                        order='check_out asc'
                    )
                if list_sign_out:
                    last_sign_out = list_sign_out[-1].id
               

            sheet_day.first_sign_in = first_sign_in
            sheet_day.last_sign_out = last_sign_out
          
            
    
    @api.one
    @api.depends('total_attendance')
    def _compute_jam(self) :
        minutes = self.total_attendance * 60
        hours, minutes = divmod(minutes, 60)
        jam_float = "%02d.%02d"%(hours, minutes) 
        self.attendance_float = float(jam_float)
            
    @api.one
    @api.depends('attendance_float')
    def _compute_hdl(self) :
        for h in self :
            if h.holiday == 1 :
                h.hdl = 0
            else :
                if h.attendance_float >= 0.15 and h.attendance_float <= 7.0 :
                    h.hdl = 1
                else :
                    h.hdl = 0
                
    @api.one
    @api.depends('attendance_float')
    def _compute_hadir(self) :
        for h in self :
            if h.attendance_float >= 0.15:
                h.hadir = 1
            else :
                h.hadir = 0
                
    @api.one
    @api.depends('first_sign_in','attendance_float')
    def _compute_lambat(self) :
        if self.holiday == 1 :
            self.lambat = 0
        else :
            if self.attendance_float >= 0.15 :
                if self.attendance_float >= 4.0 and self.attendance_float <= 7.0 :
                    self.lambat = 0
                else :
                    signin = self.first_sign_in.lambat
                    self.lambat = signin
            else :
                self.lambat = 0    
   
            
    @api.one
    @api.depends('last_sign_out','attendance_float')
    def _compute_pla(self) :
        if self.attendance_float >= 0.15 :
            if self.attendance_float >= 4.0 and self.attendance_float <= 7.0 :
                self.pla = 0
            else :
                signout = self.last_sign_out.pla
                self.pla = signout
        else :
            self.pla = 0
            
    @api.one
    @api.depends('last_sign_out','first_sign_in')
    def _compute_nocheck(self) :
        if self.holiday == 1 :
            self.no_checkout = 0
        else :
            if len(self.last_sign_out) == 0 and len(self.first_sign_in) != 0:
                self.no_checkout = 1
            else :
                self.no_checkout = 0
            
            
    @api.one
    @api.depends('first_sign_in','attendance_float')
    def _compute_holyday(self) :
        if self.first_sign_in:
            if self.attendance_float >= 0.15:
                self.work_day = self.first_sign_in.hari_kerja
                self.holiday = self.first_sign_in.hari_libur
                self.site_office = self.first_sign_in.site_office
            
       
            
       

    first_sign_in = fields.Many2one(
        string="First Sign In",
        comodel_name="hr.attendance",
        compute="_compute_summary_info"
    )

    last_sign_out = fields.Many2one(
        string="Last Sign Out",
        comodel_name="hr.attendance",
        compute="_compute_summary_info"
    )
    
    
    attendance_float = fields.Float('Hours Float',compute='_compute_jam')
    hdl = fields.Integer('HDL', compute ='_compute_hdl')
    hadir = fields.Integer('Hadir', compute ='_compute_hadir')
    lambat = fields.Integer('T', compute ='_compute_lambat')
    pla = fields.Integer('PLA', compute ='_compute_pla')
    work_day = fields.Integer('Work Day', compute ='_compute_holyday')
    holiday = fields.Integer('Holiday', compute ='_compute_holyday')
    site_office = fields.Integer('Site Office', compute ='_compute_holyday')
    no_checkout = fields.Integer('No Checkout', compute ='_compute_nocheck')
    

    
    
    
