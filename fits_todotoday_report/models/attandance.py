from openerp import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class Attendence(models.Model):
    _inherit = 'hr.attendance'
    
    
    def set_template(self, isi, location, ip, cekin, cekout):
        
        if self.site_office == True :
            site_office = " *(Site Office)*"
        else:
            site_office = "" 
            
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        print '========isi==============', emp.name, location, ip, cekin
        
        res = isi.isi_pesan.replace('{name employee}', emp.name.upper())
        res = res.replace('{check in}', cekin)
        res = res.replace('{site office}', site_office)
        res = res.replace('{location}', location)
        res = res.replace('{ip}', ip)
        res = res.replace('{check out}', cekout if cekout != False else '')
        return res        
    
    
    def send_wa_notif_in(self, location, ip, cekin, cekout):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp.manager == True :
            if emp.department_id :  
                if emp.department_id.wagroup_manager :
                    print '===============Location=============', location, ip
                    template = self.env['fits.wa.template'].search([('type','=', 'att'), ('cek_in_out','=', 'cekin')],limit=1)
                    message = self.set_template(template, location, ip, cekin, cekout)
                    pesan = message
                    groupA = emp.department_id.wagroup_manager.number_admin
                    groupID  = emp.department_id.wagroup_manager.group_id
                    isi  = pesan
                    self.env['whatsapp.group'].send_message_wablas(groupA, groupID, isi) 
        else :
            if emp.department_id :
                if emp.department_id.wagroup_department :
                    template = self.env['fits.wa.template'].search([('type','=', 'att'), ('cek_in_out','=', 'cekin')],limit=1)
                    message = self.set_template(template, location, ip, cekin, cekout)
                    pesan = message
                    groupA = emp.department_id.wagroup_department.number_admin
                    groupID  = emp.department_id.wagroup_department.group_id
                    isi  = pesan
                    self.env['whatsapp.group'].send_message_wablas(groupA, groupID, isi) 
                    
            
    def send_wa_notif_out(self, location, ip, cekin, cekout):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp.manager == True :
            if emp.department_id :  
                if emp.department_id.wagroup_manager :
                    print '===============Location=============', location, ip, cekin
                    template = self.env['fits.wa.template'].search([('type','=', 'att'), ('cek_in_out','=', 'cekout')],limit=1)
                    message = self.set_template(template, location, ip, cekin, cekout)
                    pesan = message 
                    groupA = emp.department_id.wagroup_manager.number_admin
                    groupID  = emp.department_id.wagroup_manager.group_id
                    isi  = pesan
                    self.env['whatsapp.group'].send_message_wablas(groupA, groupID, isi)
        else :
            if emp.department_id :
                if emp.department_id.wagroup_department :
                    template = self.env['fits.wa.template'].search([('type','=', 'att'), ('cek_in_out','=', 'cekout')],limit=1)
                    message = self.set_template(template, location, ip, cekin, cekout)
                    pesan = message
                    groupA = emp.department_id.wagroup_department.number_admin
                    groupID  = emp.department_id.wagroup_department.group_id
                    isi  = pesan
                    self.env['whatsapp.group'].send_message_wablas(groupA, groupID, isi)
                  
            
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
               
    
    @api.model
    def create(self, vals):
        res = super(Attendence, self).create(vals) 
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        user_tz = self.env.user.tz or 'Asia/Jakarta'
        format_tgl = '%Y-%m-%d %H:%M:%S'
        jam_sekarang = datetime.now()
        tgl_jam = jam_sekarang.strftime(format_tgl)
        cek_in = datetime.strptime(tgl_jam, '%Y-%m-%d %H:%M:%S')
        jam_now =cek_in
        jam_now = pytz.timezone('UTC').localize(jam_now)
        jam_now =jam_now.astimezone(pytz.timezone(user_tz))
        cekin_now = jam_now.strftime("%d-%m-%Y %H:%M:%S")
        cekin = cekin_now
        location = vals.get('location')
        ip = vals.get('ip')
        cekout = False
        if emp.department_id:
            self.send_wa_notif_in(location, ip, cekin, cekout)
        return res
    
    @api.multi
    def write(self, vals):
        if self.check_out == False :
            emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            user_tz = self.env.user.tz or 'Asia/Jakarta'
            format_tgl = '%Y-%m-%d %H:%M:%S'
            jam_sekarang = datetime.now()
            tgl_jam = jam_sekarang.strftime(format_tgl)
            cek_out = datetime.strptime(tgl_jam, '%Y-%m-%d %H:%M:%S')
            jam_now =cek_out
            jam_now = pytz.timezone('UTC').localize(jam_now)
            jam_now =jam_now.astimezone(pytz.timezone(user_tz))
            cekout_now = jam_now.strftime("%d-%m-%Y %H:%M:%S")
            cekout = cekout_now
            location = self.location
            ip = self.ip
            cekin_server = self._convert_datetime_utc(emp, self.check_in)
            cekin_str = datetime.strptime(cekin_server, '%Y-%m-%d %H:%M:%S')
            cekin = cekin_str.strftime("%d-%m-%Y %H:%M:%S") 
            if emp.department_id :
                self.send_wa_notif_out(location, ip, cekin, cekout)
        return super(Attendence, self).write(vals)
    
    
    
    