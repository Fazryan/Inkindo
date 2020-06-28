# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import requests

class todotoday(models.Model):
    _name = 'todo.today'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "To do Today Report"
    _rec_name = 'date' 
    
    
    @api.model
    def _employee_get(self):
        ids = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        if ids:
            return ids
        

    
    employee_id = fields.Many2one('res.users','Employee',readonly = True, default=lambda self: self.env.user.id)
    date = fields.Date(string='Date', default=fields.Date.context_today, readonly=True)
    today_line_ids = fields.One2many('todo.today.line', 'todo_id', string="To do Today Line")
    timesheet_ids = fields.One2many('account.analytic.line', 'todo_id', string = "Timesheets")
    date_valid = fields.Date(string='Date')
    total_task = fields.Float(compute='_get_total_task', string=' Total Task')
    total_durasi = fields.Float(compute='_get_total_durasi', string=' Total Duration')
    employee = fields.Many2one('hr.employee', string="Employee", default=_employee_get)
    manager_id = fields.Many2one(string='Manager', store=True, related='employee.parent_id', readonly=True)
    coach_id = fields.Many2one(string='Coach', store=True, related='employee.coach_id', readonly=True)
    attendance = fields.Float(compute='_get_attendance', string="Last Duration")
    att_onprogres = fields.Float(compute='_compute_summary_info', string="Duration On Progress")
    att_state = fields.Selection(string="Attendance", compute='_get_status', selection=[('checked_out', "Checked out"), ('checked_in', "Checked in")])
    last_sign_in = fields.Char(string="Last Sign In",compute="_compute_summary_info")
    first_sign_in = fields.Char(string="First Sign In",compute="_compute_summary_info")
    last_sign_out = fields.Char(string="Last Sign Out",compute="_compute_summary_info")
    tot_att = fields.Float(compute='_get_attendance', string="Total Duration")
    task_to_be = fields.Integer(compute='_task_to_be', string='Task To be Done')
    task_ids = fields.One2many(string="Task To be Done",comodel_name='project.task',
                                   inverse_name='user_id')
    task_wait = fields.Integer(compute='_task_waiting', string='Awaiting')
    task_wait_ids = fields.One2many(string="Awaiting",comodel_name='project.task',
                                   inverse_name='user_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)
    
    @api.multi
    @api.depends('employee_id')
    def _task_to_be(self):
        for each in self:
            format_tgl = "%Y-%m-%d %H:%M:%S"
            user_tz = self.env.user.tz or 'Asia/Jakarta'
            jam_now = datetime.now()
            jam_now = pytz.timezone('UTC').localize(jam_now)
            jam_now =jam_now.astimezone(pytz.timezone(user_tz))
            tgl_jam = jam_now.strftime(format_tgl)
            print '=================date==============', tgl_jam, self.date
            task_ids = self.env['project.task'].search([('user_id', '=', each.employee_id.id),('stage_id.name', 'not in', ['Done','Cancelled']),
                                                        ('date_start', '<=', tgl_jam)]) 
            each.task_to_be = len(task_ids)

    @api.multi
    def task_tobe_view(self):
        self.ensure_one()
        format_tgl = "%Y-%m-%d %H:%M:%S"
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        jam_now = datetime.now()
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        tgl_jam = jam_now.strftime(format_tgl)
        domain = [
            ('user_id', '=', self.employee_id.id),('stage_id.name', 'not in', ['Done','Cancelled']),
            ('date_start', '<=', tgl_jam)]
        return {
            'name': _('Task To be Done'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Task
                        </p>'''),
            'limit': 80,
            'context': {'default_user_id': self.employee_id.id}
        }
    
    
    @api.multi
    @api.depends('employee_id')
    def _task_waiting(self):
        for each in self:
            format_tgl = "%Y-%m-%d %H:%M:%S"
            user_tz = self.env.user.tz or 'Asia/Jakarta'
            jam_now = datetime.now()
            jam_now = pytz.timezone('UTC').localize(jam_now)
            jam_now =jam_now.astimezone(pytz.timezone(user_tz))
            tgl_jam = jam_now.strftime(format_tgl)
            print '=================date==============', tgl_jam, self.date
            task_ids = self.env['project.task'].search([('user_id', '=', each.employee_id.id),('stage_id.name', 'not in', ['Done','Cancelled']),
                                                        ('date_start', '>', tgl_jam)]) 
            each.task_wait = len(task_ids)

    @api.multi
    def task_waiting_view(self):
        self.ensure_one()
        format_tgl = "%Y-%m-%d %H:%M:%S"
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        jam_now = datetime.now()
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        tgl_jam = jam_now.strftime(format_tgl)
        domain = [
            ('user_id', '=', self.employee_id.id),('stage_id.name', 'not in', ['Done','Cancelled']),
            ('date_start', '>', tgl_jam)]
        return {
            'name': _('Awaiting'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Task
                        </p>'''),
            'limit': 80,
            'context': {'default_user_id': self.employee_id.id}
        }
    
    
    
    
    
    @api.multi
    def _convert_datetime_utc(self, employee, dt):
        self.ensure_one()
        convert_dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)
        
        user_tz = employee.user_id.tz
        if user_tz:
            convert_tz = pytz.timezone('UTC').localize(convert_dt)
        else:
            return False

        convert_utc = convert_tz.astimezone(pytz.timezone(user_tz))
        format_utc = datetime.strftime(
            convert_utc,
            DEFAULT_SERVER_DATETIME_FORMAT
        )

        return format_utc
    
    @api.multi
    def _compute_summary_info(self):
        for x in self :
            format_tgl = "%Y-%m-%d"
            employee = x.employee
            user_tz = x.employee_id.tz or 'Asia/Jakarta'
            jam_now = datetime.now()
            jam_now = pytz.timezone('UTC').localize(jam_now)
            jam_now =jam_now.astimezone(pytz.timezone(user_tz))
            tgl_jam = jam_now.strftime(format_tgl)
            att_now = jam_now.strftime("%Y-%m-%d %H:%M:%S")
            attd_obj = self.env['hr.attendance']
            utc_date_1 = x.date + ' 00:00:00'
            utc_date_2 = x.date + ' 23:59:59'
            criteria_sign_in = [('employee_id', '=', x.employee.id),
                                      ('check_in', '>=', utc_date_1),
                                      ('check_in', '<=', utc_date_2),
                    ]
            list_sign_in = attd_obj.search(criteria_sign_in, order='check_in asc')
            
            list_att = attd_obj.search([('employee_id', '=', x.employee.id)], order='check_in asc')
            att = []
            for l in list_att :
                dt_now = x._convert_datetime_utc(employee, l.check_in)
                if dt_now >= utc_date_1 and dt_now <= utc_date_2 :
                    att.append(dt_now)
                    string_in = datetime.strptime(att[0], "%Y-%m-%d %H:%M:%S")
                    jam_in = string_in.strftime('%H:%M:%S')
                    x.first_sign_in = jam_in
            
            if list_sign_in:
                last_chekin = list_sign_in[-1].check_in
                utc_cekin = x._convert_datetime_utc(employee, last_chekin)
                string_chekin = datetime.strptime(utc_cekin, "%Y-%m-%d %H:%M:%S")
                jam = string_chekin.strftime('%H:%M:%S')
                #x.last_sign_in = jam
                
#                 first_chekin = list_sign_in[0].check_in
#                 utc_cekin = x._convert_datetime_utc(employee, first_chekin)
#                 string_chekin = datetime.strptime(utc_cekin, "%Y-%m-%d %H:%M:%S")
#                 jam = string_chekin.strftime('%H:%M:%S')
#                 x.first_sign_in = jam
                
                #diff = datetime.strptime(att_now,"%Y-%m-%d %H:%M:%S" )- datetime.strptime(utc_cekin, "%Y-%m-%d %H:%M:%S")
                #second = diff.seconds
                #duration = second/3600.0
                
                #today = self.search([('date', '=', tgl_jam)], limit = 1)
                #if today :
                    #if today.att_state == 'checked_in' :
                        #today.att_onprogres = duration
                    #else :
                        #today.att_onprogres = 0.0
                
            criteria_sign_out = [('employee_id', '=', x.employee.id),
                                      ('check_out', '>=', utc_date_1),
                                      ('check_out', '<=', utc_date_2),
                    ]
            list_sign_out = attd_obj.search(criteria_sign_out, order='check_out asc')
            
            list_att = attd_obj.search([('employee_id', '=', x.employee.id),('check_out', '!=', False)], order='check_out asc')
            att = []
            for l in list_att :
                dt_now = x._convert_datetime_utc(employee, l.check_out)
                if dt_now >= utc_date_1 and dt_now <= utc_date_2 :
                    att.append(dt_now)
                    string_out = datetime.strptime(att[-1], "%Y-%m-%d %H:%M:%S")
                    jam_out = string_out.strftime('%H:%M:%S')
                    x.last_sign_out = jam_out
            
#             if list_sign_out:
#                 last_chekout = list_sign_out[-1].check_out
#                 utc_cekout = x._convert_datetime_utc(employee, last_chekout)
#                 string_chekout = datetime.strptime(utc_cekout, "%Y-%m-%d %H:%M:%S")
#                 jam = string_chekout.strftime('%H:%M:%S')
#                 x.last_sign_out = jam
    
    
    
    
    @api.multi
    def get_todo_line(self):
        format_tgl = "%Y-%m-%d %H:%M:%S"
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        jam_now = datetime.now()
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        tgl_jam = jam_now.strftime(format_tgl)
        print '=================date==============', tgl_jam, self.date
        task_obj = self.env['project.task'].search([('user_id', '=', self.employee_id.id),('stage_id.name', 'not in', ['Done','Cancelled']),
                                                    ('date_start', '<=', tgl_jam),'|',('date_end', '>=', tgl_jam),
                                                    ('date_deadline', '>=', self.date)])   
        
        
        line_list = []
        for x in task_obj :
            vals = {
                    'todo_id'       : self.id,
                    'project_id'    : x.project_id.id,
                    'task_id'       : x.id,
                      'desc'          : '',
                      'state'         : 'draft'
                }
            line_list.append((0, 0, vals))
           
        self.today_line_ids = line_list
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.get_todo_line()
    
#     @api.onchange('employee_id')
#     def onchange_employee_id(self):
#         if self.employee_id:
#             obj_employee = self.env['hr.employee'].search([('user_id', '=', self.employee_id.id)])
#             for x in obj_employee :
#                 self.manager_id = x.parent_id.id
#                 self.coach_id = x.coach_id.id
    
    
    @api.multi
    @api.depends('attendance','att_onprogres')
    def _get_attendance(self):
        for x in self :
            obj_sheet_day = self.env['hr_timesheet_sheet.sheet.day'].search([('sheet_id.employee_id','=',x.employee.id),
                                                    ('name','=',x.date)])
            

            if obj_sheet_day:
                for att in obj_sheet_day :
                    x.attendance = att.total_attendance
                    #print '==============total attandance================', x.attendance, x.att_onprogres
                    #x.tot_att = x.attendance + x.att_onprogres
            #else :
                #x.tot_att = x.att_onprogres
                #print '==================no timesheet===============',x.att_onprogres
                

                
    @api.one
    def _get_status(self):
        for x in self :
            utc_date_1 = x.date + ' 00:00:00'
            utc_date_2 = x.date + ' 23:59:59'
            attendance = self.env['hr.attendance'].search([('employee_id', '=', x.employee.id), ('check_out', '=', False),
                                                           ('check_in', '>=', utc_date_1),
                                                           ('check_in', '<=', utc_date_2),], limit=1)
            
            list_att = self.env['hr.attendance'].search([('employee_id', '=', x.employee.id), ('check_out', '=', False)], limit=1)
            if list_att :
                dt_now = x._convert_datetime_utc(x.employee, list_att.check_in)
                if dt_now >= utc_date_1 and dt_now <= utc_date_2 :
                    x.att_state = 'checked_in'
                else :
                    x.att_state ='checked_out'
                    
            else :
                x.att_state ='checked_out' 
            
            
#             if attendance:
#                 convert_cekin= x._convert_datetime_utc(x.employee, attendance.check_in)
#                 print '=====================cekin===========', attendance.check_in, convert_cekin
#                 x.att_state = 'checked_in'
#             else :
#                 x.att_state ='checked_out'

    
    @api.one
    @api.depends('today_line_ids.duration')
    def _get_total_durasi(self):
        for x in self:
            for line in x.today_line_ids :
                if line.state != 'cancel' :
                    x.total_durasi += line.duration
                
    @api.one
    @api.depends('today_line_ids')
    def _get_total_task(self):
        for x in self:
            task = []
            for line in x.today_line_ids :
                if line.state != 'cancel' :
                    task.append(line.task_id)
                    x.total_task = len(task)

    
    
    @api.onchange('date')
    def onchange_date(self):
        if self.date :
            todo_obj = self.env['todo.today'].search([('employee_id', '=', self.employee_id.id),
                                                     ('date', '=',self.date)])
        
            for d in todo_obj :
                if d.date == self.date:
                    return {'value':{'date_valid' : self.date},'warning':{'title':'Warning','message':"To do Today in today is created, You Can't create two To do Today in one Day "}}
    
    
    
    @api.constrains('date','date_valid')
    def _check_tgl(self):
        if self.date_valid :
            if self.date_valid == self.date:
                raise exceptions.ValidationError("To do Today in today is created, You Can't create two To do Today in one Day ")
                
                
    def set_template(self, isi, obj, duration):
        if obj.site_office == True :
            site_office = " *(Site Office)*"
        else:
            site_office = ""
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        cek_in = datetime.strptime(obj.check_in, '%Y-%m-%d %H:%M:%S')
        jam_now =cek_in
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        cekin = jam_now.strftime("%d-%m-%Y %H:%M:%S")
        location = obj.location
        ip = obj.ip
        res = isi.isi_pesan.replace('{name employee}', obj.employee_id.name.upper())
        res = res.replace('{check in}', cekin)
        res = res.replace('{duration}', duration)
        res = res.replace('{site office}', site_office)
        res = res.replace('{location}', location)
        res = res.replace('{ip}', ip)
        return res                  
            
            
    @api.model
    def reminder_wa(self):
        format_tgl = "%Y-%m-%d"
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        jam_now = datetime.now()
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        tgl_jam = jam_now.strftime(format_tgl)
        utc_date_1 = tgl_jam + ' 00:00:00'
        utc_date_2 = tgl_jam + ' 23:59:59'
        attendance = self.env['hr.attendance'].search([('check_in', '>=', utc_date_1),
                                                       ('check_in', '<=', utc_date_2)])
        
        for att in attendance :
            if not att.employee_id.no_todo_today :
                tdtoday = self.env['todo.today'].search([('date', '=', tgl_jam),('employee', '=', att.employee_id.id)], limit=1)
                line_start = self.env['todo.today.line'].search([('todo_id', '=', tdtoday.id),('state', '!=', 'draft')])
                if not line_start :
                    att_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    diff = datetime.strptime(att_now,"%Y-%m-%d %H:%M:%S" )- datetime.strptime(att.check_in, "%Y-%m-%d %H:%M:%S")
                    second = diff.seconds
                    duration = second/3600.0
                    
                    if duration > 0.5 :
                        kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
                        if kon :
                            token = kon.token
                            
                            template = self.env['fits.wa.template'].search([('type','=', 'tdt')],limit=1)
                            durasi = ""
                            isi = self.set_template(template, att, durasi)
                            
                            if att.employee_id.mobile_phone.startswith("0"):
                                mobile ="62" + att.employee_id.mobile_phone[1:]
                            else:
                                mobile = att.employee_id.mobile_phone
                              
                            number = mobile
                            message  = isi
               
                              
                            headers = {
                                'Authorization': token
                            }
                              
                            jsonBody = {
                                'phone': number,
                                'message': message
                            }
                              
                            r = requests.post("https://simo.wablas.com/api/send-message", 
                                headers=headers,
                                data=jsonBody)
                        
                            print("Status code: " + str(r.status_code))
                            print("RESPONSE : " + str(r.content))
                            
    @api.model
    def reminder_att(self):
        attendance = self.env['hr.attendance'].search([('check_out', '=', False)])
        for att in attendance :
            att_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            diff = datetime.strptime(att_now,"%Y-%m-%d %H:%M:%S" )- datetime.strptime(att.check_in, "%Y-%m-%d %H:%M:%S")
            second = diff.seconds
            duration = second//3600.0
            minutes = (second - duration*3600)/60
            
                    
            if duration > 0:
                jam = str(int(round(duration,0))) + " jam "
            else:
                jam = ""
                        
                        
            durasi = jam + str(int(round(minutes,0))) + " menit"
                    
            if duration > 12 :
                kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
                if kon :
                    token = kon.token
                             
                    template = self.env['fits.wa.template'].search([('type','=', 'no_cekout')],limit=1)
                    isi = self.set_template(template, att, durasi)
                             
                    if att.employee_id.mobile_phone.startswith("0"):
                        mobile ="62" + att.employee_id.mobile_phone[1:]
                    else:
                        mobile = att.employee_id.mobile_phone
                               
                        number = mobile
                        message  = isi
                
                               
                        headers = {
                                'Authorization': token
                            }
                               
                        jsonBody = {
                                'phone': number,
                                'message': message
                            }
                               
                        r = requests.post("https://simo.wablas.com/api/send-message", 
                                headers=headers,
                                data=jsonBody)
                         
                        print("Status code: " + str(r.status_code))
                        print("RESPONSE : " + str(r.content))
                        
                    if att.employee_id.department_id :
                        if att.employee_id.department_id.wagroup_department :
                            template = self.env['fits.wa.template'].search([('type','=', 'no_cekout')],limit=1)
                            isi = self.set_template(template, att, durasi)
                            pesan = isi
                            groupA = att.employee_id.department_id.wagroup_department.number_admin
                            groupID  = att.employee_id.department_id.wagroup_department.group_id
                            message  = pesan
                            self.env['whatsapp.group'].send_message_wablas(groupA, groupID, message)
                
    