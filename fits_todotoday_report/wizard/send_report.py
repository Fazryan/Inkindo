from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import re


class TodoTodayReport(models.TransientModel):
    _name = "today.report"
    _description = "To do Today Report"

    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    
    todoline_id = fields.Many2one('todo.today.line', string='Line Id', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users', string='User', default=_default_user)
    desc = fields.Char('Description')
    stage = fields.Char('Stage')
    duration = fields.Float(string='Duration')
    partner_ids = fields.Many2many('res.partner', string='Recipients')
    channel_ids = fields.Many2many('mail.channel', string='Channels', required=False)
    effective_hours = fields.Float( string='Last Man Day(s)', readonly=True)
    planned_hours = fields.Float( string='Initially Planned Man Day(s).', readonly=True)
    total_effective = fields.Float(compute='_total_effective', string=' Total Man Day(s)')
    partner_id = fields.Many2one('res.partner', string='Customer')
    send_group_wa = fields.Selection([
        ('employee', 'Group Employee'), ('channel', 'Group Channel'), ('double', 'Group Employee and Channel')], string='Send To WhatsApp', 
                                     default='employee', required=True)
    
    
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
            res['desc'] = self.env['todo.today.line'].browse(self.env.context['active_id']).desc
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
            durasi = str(wizard.duration)
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
            total_efektif = round(wizard.total_effective,2)
            tot_effective = str(total_efektif)
            planned = str(wizard.planned_hours)
            proj_planned = str(wizard.project_id.total_planned)
            proj_efec = round(wizard.project_id.total_efective, 2)
            proj_efective = str(proj_efec)
            actual = str(wizard.task_id.actual_today)
            expected = str(wizard.project_id.expected_hours)
            
            
            if  proj_efec <= wizard.project_id.total_planned <= wizard.project_id.expected_hours : 
                sip = '\U00002705'
                emot = sip.decode('unicode-escape')
            elif proj_efec > wizard.project_id.expected_hours :
                no = '\U0000274C'
                emot = no.decode('unicode-escape')
            elif wizard.project_id.total_planned <= wizard.project_id.expected_hours :
                war = '\U000026A0'
                emot = war.decode('unicode-escape')
            else:
                war = '\U000026A0'
                emot = war.decode('unicode-escape')
                
            if wizard.total_effective <= wizard.planned_hours : 
                sip = '\U00002705'
                emot_task = sip.decode('unicode-escape')
            else :
                war = '\U000026A0'
                emot_task = war.decode('unicode-escape')
            
             
            if wizard.stage == False:
                stage = ' '
            else :
                stage = wizard.stage
                
            if wizard.partner_id.name == False:
                customer = ''
            else :
                customer = wizard.partner_id.name
             
                   
            tampung = '## Project Report '+tgl+' ##<br><br>'+'Project Name :'+' '+project+' ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+'<br>Task Name :'+' '+task \
            +'<br>Customer :'+' '+customer+'<br>Date :'+' '+date+'<br><br>Duration : '+durasi+'<br>Total Work Time :'+' '+tot_effective+' '+'hours / '+planned+' '+'hours'+'<br>Last Progress :'+' '+actual+' '+'%' \
            +'<br>Stage :'+' '+stage+'<br><br>Description :'+' '+desc
             
            tampung_wa = '## Project Report Start '+'- *'+pengirim+'* '+tgl+' ## \n\n'+'Project Name :'+' *'+project+'* ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+emot+'\nTask Name :'+' *'+task \
            +'*\nCustomer :'+' '+customer+'\nDate :'+' '+date+'\n\nDuration : '+durasi+'\nTotal Work Time :'+' '+tot_effective+' '+'hours / '+planned+' '+'hours '+emot_task+'\nLast Progress :'+' '+actual+' '+'%' \
            +'\nStage :'+' '+stage+'\n\nDescription :\n'+desc_wa
             
            store_message = tampung.encode('utf-8').strip()
            store_message_wa = tampung_wa.encode('utf-8').strip()
              
                
              
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
             
            self.mapped('todoline_id').write({'state': 'start','start_date': fields.Datetime.now()})
             
             
            obj_task = self.env['project.task'].search([('id', '=', wizard.task_id.id)])
            for t in obj_task :
                if t.stage_id.id == 1 :
                    t.stage_id = 16
                     
             
             
            emp = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
            kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
            if not kon :
                raise Warning(_("Account Whatsapp not Found or Not Active....!!!"))
            else :
                if kon.type_api == 'whatsmate' :
                    if emp.manager == True :
                        admin = self.env['wa.group.todotoday'].search([('type_api', '=', 'whatsmate'), ('group_manager', '=', True)],limit=1)
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
                                    'type_api' : 'whatsmate',
                                    'user_id': self.env.user.id,
                                    'date_report': fields.Datetime.now(),
                                    'status_report' : 'start',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                          
                    else :
                        admin = self.env['wa.group.todotoday'].search([('type_api', '=', 'whatsmate'),('group_manager', '=', False)],limit=1)
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
                                    'type_api' : 'whatsmate',
                                    'user_id': self.env.user.id,
                                    'date_report': fields.Datetime.now(),
                                    'status_report' : 'start',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                   
                 
                else :        
                    if wizard.send_group_wa == 'employee' :
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
    

    