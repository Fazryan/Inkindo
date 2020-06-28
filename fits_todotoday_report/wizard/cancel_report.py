from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import re


class TodoTodayReport(models.TransientModel):
    _name = "cancel.report"
    _description = "To do Today Cancel Report"

    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    
    todoline_id = fields.Many2one('todo.today.line', string='Line Id', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users', string='User', default=_default_user)
    desc = fields.Html('Cancel Reason')
    stage = fields.Char('Stage')
    duration = fields.Float(string='Duration')
    partner_ids = fields.Many2many('res.partner', string='Recipients')
    channel_ids = fields.Many2many('mail.channel', string='Channels', required=False)
    effective_hours = fields.Float( string='Last Man Day(s)', readonly=True)
    planned_hours = fields.Float( string='Initially Planned Man Day(s).', readonly=True)
    total_effective = fields.Float(compute='_total_effective', string=' Total Man Day(s)')
    partner_id = fields.Many2one('res.partner', string='Customer')
    
    
    @api.depends('duration','effective_hours')
    def _total_effective(self):
        if self.duration:
            self.total_effective = self.effective_hours + self.duration
    
    
    
  
    @api.onchange('task_id')
    def task_id_onchange(self):
        if self.task_id:
            partner = []
            follow_obj=self.env['mail.followers']
            follow_ids_list =  follow_obj.search([('res_model','=', 'project.task'),('res_id','=',self.task_id.id),
                                                  ('channel_id','=', False)])
            for x in follow_ids_list :
                partner.append(x.partner_id.id) 
                self.partner_ids = partner
                 
    @api.onchange('user_id')
    def user_id_onchange(self):
        if self.user_id:
            user = []
            follow_obj=self.env['mail.followers']
            follow_ids_list =  follow_obj.search([('res_model','=', 'project.task'),('res_id','=',self.task_id.id),
                                                  ('partner_id','=', False)])

            for x in follow_ids_list :
                user.append(x.channel_id.id)
                self.channel_ids = user

    
   
    @api.model
    def default_get(self, fields):
        res = super(TodoTodayReport, self).default_get(fields)
        if self.env.context.get('active_model') == 'todo.today.line' and self.env.context.get('active_id'):
            res['todoline_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).id
            res['task_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.id
            res['project_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).project_id.id
            res['date'] = self.env['todo.today.line'].browse(self.env.context['active_id']).date
            res['stage'] = self.env['todo.today.line'].browse(self.env.context['active_id']).stage
            res['duration'] = self.env['todo.today.line'].browse(self.env.context['active_id']).duration
            res['effective_hours'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.effective_hours
            res['planned_hours'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.planned_hours
            res['partner_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).project_id.partner_id.id
        return res
    
    
    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text
    
    
    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    

    @api.multi
    def create_report(self):
        message = self.env['mail.message']
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(fields.Datetime.now(),
                            DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
      
        for wizard in self:
            task = wizard.task_id.name
            project = wizard.project_id.name
            date = wizard.date
            desc = wizard.desc
            reps = {'<br>':'', '</p>':'\n', '<p>':'', '&amp;':'&'}
            txt = self.replace_all(desc, reps)
            convert_txt = self.striphtml(txt)
            desc_wa = convert_txt
            tgl = display_date_result
            pengirim = self.env.user.name
            customer = wizard.partner_id.name
            proj_planned = str(wizard.project_id.total_planned)
            proj_efec = round(wizard.project_id.total_efective, 2)
            proj_efective = str(proj_efec)
            expected = str(wizard.project_id.expected_hours)
            
            
             
                
            if wizard.partner_id.name == False:
                customer = ''
            else :
                customer = wizard.partner_id.name
             
                   
            tampung = '## Project Report CANCELED '+tgl+' ##<br><br>'+'Project Name :'+' '+project+' ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+'<br>Task Name :'+' '+task \
            +'<br>Customer :'+' '+customer+'<br>Date :'+' '+date \
            +'<br><br>Cancel Reason :'+' '+desc
             
            tampung_wa = '## Project Report CANCELED '+'- *'+pengirim+'* '+tgl+' ## \n\n'+'Project Name :'+' *'+project+'* ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+'\nTask Name :'+' *'+task \
            +'*\nCustomer :'+' '+customer+'\nDate :'+' '+date \
            +'\n\nCancel Reason :\n'+desc_wa
             
            store_message = tampung.encode('utf-8').strip()
            store_message_wa = tampung_wa.encode('utf-8').strip()
              
            print '=============store message==============', store_message
                
              
            if len(wizard.partner_ids) :
                if len(wizard.channel_ids):
                    message.create({
                        'res_id':wizard.task_id.id,
                        'record_name': wizard.task_id.name,
                        'model': 'project.task',
                        'message_type' : 'comment',
                        'body':  store_message,
                        'partner_ids':[( 4, wizard.partner_ids.ids)],
                        'channel_ids' : [( 4, wizard.channel_ids.ids)]
                        })
                else :
                    message.create({
                        'res_id':wizard.task_id.id,
                        'record_name': wizard.task_id.name,
                        'model': 'project.task',
                        'message_type' : 'comment',
                        'body':  store_message,
                        'partner_ids':[( 4, wizard.partner_ids.ids)]
                        })
                    
            else :
                if len(wizard.channel_ids):
                    message.create({
                            'res_id':wizard.task_id.id,
                            'record_name': wizard.task_id.name,
                            'model': 'project.task',
                            'message_type' : 'comment',
                            'body':  store_message, 
                            'channel_ids' : [( 4, wizard.channel_ids.ids)]
                            })
                else :
                    message.create({
                            'res_id':wizard.task_id.id,
                            'record_name': wizard.task_id.name,
                            'model': 'project.task',
                            'message_type' : 'comment',
                            'body':  store_message
                            })
                    
             
            self.mapped('todoline_id').write({'state': 'cancel','cancel_date': fields.Datetime.now()})
             
                     
             
             
            emp = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
            kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
            if not kon :
                raise Warning(_("Account Whatsapp not Found or Not Active....!!!"))
            else :
                if kon.type_api == 'whatsmate' :
                    if emp.manager == True :
                        kon = self.env['whatsapp.konf'].search([],limit=1)
                        admin = self.env['wa.group.todotoday'].search([('group_manager', '=', True)],limit=1)
                        instanceId = kon.instance_id
                        clientId = kon.client_id
                        clientSecret = kon.client_scret
                           
                        groupAdmin = admin.number_admin
                        groupName  = admin.group_name
                        message  = store_message_wa
                           
                        headers = {
                            'X-WM-CLIENT-ID': clientId, 
                            'X-WM-CLIENT-SECRET': clientSecret
                        }
                           
                        jsonBody = {
                            'group_admin': groupAdmin,
                            'group_name': groupName,
                            'message': message
                        }
                           
                        r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
                            headers=headers,
                            json=jsonBody)
                          
                        print("Status code: " + str(r.status_code))
                        print("RESPONSE : " + str(r.content))
                        print("Message sent to %s" % groupName)
                        
                        kode = str(r.status_code)
                        if kode == '200' :
                            status = 'sent'
                        else :
                            status = 'fail'
                            
                            
                            
                        obj_log = self.env['log.todotoday']
                        obj_log.create({
                                    'number_admin':groupAdmin,
                                    'group_name': groupName,
                                    'message': message,
                                    'state' : status,
                                    'user_id': self.env.user.id,
                                    'date_report': fields.Datetime.now(),
                                    'status_report' : 'cancel',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                         
                    else :
                        kon = self.env['whatsapp.konf'].search([],limit=1)
                        admin = self.env['wa.group.todotoday'].search([('group_manager', '=', False)],limit=1)
                        instanceId = kon.instance_id
                        clientId = kon.client_id
                        clientSecret = kon.client_scret
                           
                        groupAdmin = admin.number_admin
                        groupName  = admin.group_name
                        message  = store_message_wa
                           
                        headers = {
                            'X-WM-CLIENT-ID': clientId, 
                            'X-WM-CLIENT-SECRET': clientSecret
                        }
                           
                        jsonBody = {
                            'group_admin': groupAdmin,
                            'group_name': groupName,
                            'message': message
                        }
                           
                        r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
                            headers=headers,
                            json=jsonBody)
                          
                        print("Status code: " + str(r.status_code))
                        print("RESPONSE : " + str(r.content))
                        print("Message sent to %s" % groupName)
                        
                        kode = str(r.status_code)
                        if kode == '200' :
                            status = 'sent'
                        else :
                            status = 'fail'
                            
                            
                        obj_log = self.env['log.todotoday']   
                        obj_log.create({
                                    'number_admin':groupAdmin,
                                    'group_name': groupName,
                                    'message': message,
                                    'state' : status,
                                    'user_id': self.env.user.id,
                                    'date_report': fields.Datetime.now(),
                                    'status_report' : 'cancel',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                        
                else :
                    if emp.manager == True :
                        if emp.department_id :          
                            if emp.department_id.wagroup_manager :
                                    
                                token       = kon.token
                                groupAdmin  = emp.department_id.wagroup_manager.number_admin
                                groupID     = emp.department_id.wagroup_manager.group_id
                                message     = store_message_wa
                                         
                                headers = {
                                            'Authorization': token
                                            }
                                         
                                jsonBody = {
                                            'phone': groupAdmin,
                                            'groupId': groupID,
                                            'message': message
                                            }
                                         
                                r = requests.post("https://simo.wablas.com/api/send-group", 
                                                      headers=headers,
                                                      data=jsonBody)
                                        
                                print("Status code: " + str(r.status_code))
                                print("RESPONSE : " + str(r.content))
                                print("Message sent to %s" % groupID)
                                      
                                kode = str(r.status_code)
                                if kode == '200' :
                                    status = 'sent'
                                else :
                                    status = 'fail'
                                          
                                          
                                          
                                obj_log = self.env['log.todotoday']
                                obj_log.create({
                                                'number_admin':groupAdmin,
                                                'group_name': groupID,
                                                'message': message,
                                                'state' : status,
                                                'type_api' : 'wablas',
                                                'user_id': self.env.user.id,
                                                'date_report': fields.Datetime.now(),
                                                'status_report' : 'start',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                                
                    else :
                        if emp.department_id :      
                            if emp.department_id.wagroup_department :
                                    
                                token       = kon.token
                                groupAdmin  = emp.department_id.wagroup_department.number_admin
                                groupID     = emp.department_id.wagroup_department.group_id
                                message     = store_message_wa
                                         
                                headers = {
                                            'Authorization': token
                                            }
                                         
                                jsonBody = {
                                            'phone'     : groupAdmin,
                                            'groupId'   : groupID,
                                            'message'   : message
                                            }
                                         
                                r = requests.post("https://simo.wablas.com/api/send-group", 
                                                    headers=headers,
                                                    data=jsonBody)
                                      
                                kode = str(r.status_code)
                                if kode == '200' :
                                    status = 'sent'
                                else :
                                    status = 'fail'
                                          
                                          
                                          
                                obj_log = self.env['log.todotoday']
                                obj_log.create({
                                                'number_admin':groupAdmin,
                                                'group_name': groupID,
                                                'message': message,
                                                'state' : status,
                                                'type_api' : 'wablas',
                                                'user_id': self.env.user.id,
                                                'date_report': fields.Datetime.now(),
                                                'status_report' : 'start',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                     
                    if len(wizard.channel_ids):
                        for c in wizard.channel_ids:
                            if c.wagroup_id :
                                token = kon.token
                                         
                                groupAdmin = c.wagroup_id.number_admin
                                groupID  = c.wagroup_id.group_id
                                message  = store_message_wa
     
                                headers = {
                                            'Authorization': token
                                            }
                                         
                                jsonBody = {
                                            'phone'     : groupAdmin,
                                            'groupId'   : groupID,
                                            'message'   : message
                                            }
                                         
                                r = requests.post("https://simo.wablas.com/api/send-group", 
                                                      headers=headers,
                                                      data=jsonBody)
                                      
                                kode = str(r.status_code)
                                if kode == '200' :
                                    status = 'sent'
                                else :
                                    status = 'fail'
                                          
                                          
                                          
                                obj_log = self.env['log.todotoday']
                                obj_log.create({
                                                'number_admin':groupAdmin,
                                                'group_name': groupID,
                                                'message': message,
                                                'state' : status,
                                                'type_api' : 'wablas',
                                                'user_id': self.env.user.id,
                                                'date_report': fields.Datetime.now(),
                                                'status_report' : 'start',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                     
            
                 

        return {'type': 'ir.actions.act_window_close'}
    

    

    