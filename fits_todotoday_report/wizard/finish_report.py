from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import re
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import base64


class FinishReport(models.TransientModel):
    _name = "finish.report"
    _description = "Finish To do Report"
   
    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    
    date = fields.Date(string='Date')
    todoline_id = fields.Many2one('todo.today.line', string='Line Id', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    date_report = fields.Date(string='Date', default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='User', default=_default_user)
    name = fields.Char('Description', required=True)
    start_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='Start Time', required=True)
    start_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='Start Time', default='00')
    end_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='End Time', required=True)
    end_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='End Time', default='00')
    unit_amount = fields.Float(string='Duration', compute='_compute_duration', readonly=True)
    start = fields.Float(string='Start Time', compute='_compute_duration',  readonly=True)
    end = fields.Float(string='End Time', compute='_compute_duration',  readonly=True)
    actual_today = fields.Float( string='Last Progres (%)', readonly=True)
    progres = fields.Float('Today Progres (%)')
    total_progres = fields.Float(compute='_total_progres', string=' Total Progres (%)')
    note = fields.Html('Note')
    next_activity = fields.Html('Next Activity')
    problem_solution = fields.Html('Problem & Solution')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    partner_ids = fields.Many2many('res.partner', string='Recipients')
    channel_ids = fields.Many2many('mail.channel', string='Channels', required=False)
    work_time = fields.Float(string='Work Time', compute='_compute_worktime',  readonly=True)
    istirahat = fields.Float(string='Break')
    effective_hours = fields.Float( string='Last Man Day(s)', readonly=True)
    planned_hours = fields.Float( string='Initially Planned Man Day(s).', readonly=True)
    total_effective = fields.Float(compute='_total_effective', string=' Total Man Day(s)')
    partner_id = fields.Many2one('res.partner', string='Customer')
    send_group_wa = fields.Selection([('employee', 'Group Employee'), ('channel', 'Group Channel'), ('double', 'Group Employee and Channel')], string='Send To WhatsApp', 
                                     default='employee', required=True)
    
  
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


#             if len(follow_ids_list)!= 0 :
#                 for x in follow_ids_list :
#                     user.append(x.channel_id.id)
#                     self.channel_ids = user
#             else :
#                 user_channel = []
#                 channel_obj=self.env['mail.channel.partner']
#                 channel_ids_list =  channel_obj.search([('partner_id.name','=', self.user_id.name)])
#                 for x in channel_ids_list :
#                     user_channel.append(x.channel_id.id) 
#                     self.channel_ids = user_channel
    
    
    
    @api.depends('actual_today','progres')
    def _total_progres(self):
        if self.progres:
            self.total_progres = self.actual_today + self.progres
            
    @api.depends('work_time','effective_hours')
    def _total_effective(self):
        if self.work_time:
            self.total_effective = self.effective_hours + self.work_time
    
    
    
    @api.depends('start_time_jam','start_time_menit','end_time_jam','end_time_menit')
    def _compute_duration(self):
        for o in self:
            start = float(int(o.start_time_jam)+float(o.start_time_menit))
            end = float(int(o.end_time_jam)+float(o.end_time_menit))
            o.start = start
            o.end = end
            o.unit_amount = end - start
            
            
    @api.onchange('unit_amount')
    def unit_amount_onchange(self):
        a = range(0,5)
        b = range(5,10)
        c = range(10,15)
        d = range(15,25)
        x = int(self.unit_amount)
        if self.unit_amount:
            if x in a :
                self.istirahat = 0
            elif x in b :
                self.istirahat = 1
            elif x in c :
                self.istirahat = 2
            elif x in d :
                self.istirahat = 3
            else :
                self.istirahat = 0
                
            
            
    @api.depends('unit_amount','istirahat')
    def _compute_worktime(self):
        for o in self:
            o.work_time = o.unit_amount - o.istirahat
    
    
    @api.model
    def default_get(self, fields):
        res = super(FinishReport, self).default_get(fields)
        if self.env.context.get('active_model') == 'todo.today.line' and self.env.context.get('active_id'):
            res['todoline_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).id
            res['task_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.id
            res['project_id'] = self.env['todo.today.line'].browse(self.env.context['active_id']).project_id.id
            res['actual_today'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.actual_today
            res['effective_hours'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.effective_hours
            res['planned_hours'] = self.env['todo.today.line'].browse(self.env.context['active_id']).task_id.planned_hours
            res['date'] = self.env['todo.today.line'].browse(self.env.context['active_id']).date
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
        timesheet= self.env['account.analytic.line']
        progres =  self.env['project.progres']
        message = self.env['mail.message']
        
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(fields.Datetime.now(),
                            DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        

        for wizard in self:
            actual = str(wizard.actual_today)
            prog = str(wizard.progres)
            totprog = str(wizard.total_progres)
            durasi = str(wizard.work_time)
            s_jam = wizard.start_time_jam
            effective = str(wizard.effective_hours)
            total_efektif = round(wizard.total_effective,2)
            tot_effective = str(total_efektif)
            planned = str(wizard.planned_hours)
            date = wizard.date
            tgl = display_date_result
            pengirim = self.env.user.name
            proj_planned = str(wizard.project_id.total_planned)
            proj_efec = round(wizard.project_id.total_efective, 2) + wizard.work_time
            proj_efective = str(proj_efec)
            expected = str(wizard.project_id.expected_hours)
            desc = wizard.name
            
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
            
            
            if wizard.start_time_menit == '0.50':
                s_menit = '30'
            else :
                s_menit = '00'
            e_jam = wizard.end_time_jam
            if wizard.end_time_menit == '0.50':
                e_menit = '30'
            else :
                e_menit = '00'
                
                
          
            if wizard.note == False:
                note = ' '
                note_wa = ''
            else :
                note = wizard.note
                reps = {'<br>':'', '</p>':'*\n', '<p>':'*', '&amp;':'&'}
                txt = self.replace_all(wizard.note, reps)
                txt_wa = txt.replace('</p>','*')
                convert_txt = self.striphtml(txt_wa)
                note_wa = convert_txt
            if wizard.next_activity == False :
                act = ' '
                act_wa = ''
            else :
                act = wizard.next_activity
                reps = {'<br>':'', '</p>':'\n', '<p>':'', '&amp;':'&'}
                txt = self.replace_all(wizard.next_activity, reps)
                convert_txt = self.striphtml(txt)
                act_wa = convert_txt
            if wizard.problem_solution == False :
                pros = ' '
                pros_wa = ''
            else :
                pros = wizard.problem_solution
                reps = {'<br>':'', '</p>':'\n', '<p>':'', '&amp;':'&'}
                txt = self.replace_all(wizard.problem_solution, reps)
                convert_txt = self.striphtml(txt) 
                pros_wa = convert_txt
            if wizard.partner_id.name == False:
                customer = ''
            else :
                customer = wizard.partner_id.name
                
                 
            tampung = '## Project Report '+tgl+' ##<br><br>'+'Project Name :'+' '+wizard.project_id.name+' ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+'<br>Task Name :'+' '+wizard.task_id.name+'<br>Customer :'+' '+customer+'<br>Date :'+' '+date \
            +'<br><br>Time :'+' '+s_jam+':'+s_menit+' -- '+e_jam+':'+e_menit+'<br>Today Work Time :'+' '+durasi+' '+'hours'+'<br>Total Work Time :'+' '+tot_effective+' '+'hours / '+planned+' '+'hours' \
            + '<br>Description :'+' '+desc+'<br><br>Progres :'+'<br>-Last Progress :'+' '+actual+' '+'%'+'<br>-Today Progress :'+' '+prog+' '+'%'+'<br>-Total Progress :'+' '+totprog+' '+'%' \
            +'<br><br> Note :'+note+'<br>Problem & Solution :'+pros+'<br> Next Activity :'+act
            store_message = tampung.encode('utf-8').strip()
            
            tampung_wa = '## Project Report Finish '+'- *'+pengirim+'* '+tgl+' ##\n\n'+'Project Name :'+' *'+wizard.project_id.name+'* ('+proj_efective+' / '+proj_planned+' / '+expected+' hours) '+emot+'\nTask Name :'+' *'+wizard.task_id.name +'*\nCustomer :'+' '+customer+'\nDate :'+' '+date \
            +'\n\nTime :'+' '+s_jam+':'+s_menit+' -- '+e_jam+':'+e_menit+'\nToday Work Time :'+' '+durasi+' '+'hours'+'\nTotal Work Time :'+' '+tot_effective+' '+'hours / '+planned+' '+'hours '+emot_task \
            +'\nDescription :'+' '+desc+'\n\nProgres :'+'\n-Last Progress :'+' '+actual+' '+'%'+'\n-Today Progress :'+' '+prog+' '+'%'+'\n-Total Progress :'+' '+totprog+' '+'%' \
            +'\n\nNote :\n'+note_wa+'\nProblem & Solution :\n'+pros_wa+'\nNext Activity :\n'+act_wa
            store_message_wa = tampung_wa.encode('utf-8').strip()
            
            print '=============store message==============', store_message
              
            
            progres.create({
                    'task_id':wizard.task_id.id,
                    'date': wizard.date_report,
                    'progres': wizard.progres
                    })
            timesheet.create({
                    'task_id':wizard.task_id.id,
                    'todo_id':wizard.todoline_id.todo_id.id,
                    'date': wizard.date_report,
                    'user_id': wizard.user_id.id,
                    'name': wizard.name,
                    'unit_amount': wizard.work_time,
                    'account_id' : wizard.project_id.analytic_account_id.id,
                    'project_id' : wizard.project_id.id
                    })
            
            if len(wizard.partner_ids) :
                if len(wizard.attachment_ids) and  len(wizard.channel_ids):
                    message.create({
                        'res_id':wizard.task_id.id,
                        'record_name': wizard.task_id.name,
                        'model': 'project.task',
                        'message_type' : 'comment',
                        'body':  store_message,
                        'partner_ids':[( 4, wizard.partner_ids.ids)],
                        'channel_ids' : [( 4, wizard.channel_ids.ids)],
                        'attachment_ids':[( 4, wizard.attachment_ids.ids)]
                        })
                elif len(wizard.channel_ids) :
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
                if len(wizard.attachment_ids) and  len(wizard.channel_ids) : 
                    message.create({
                            'res_id':wizard.task_id.id,
                            'record_name': wizard.task_id.name,
                            'model': 'project.task',
                            'message_type' : 'comment',
                            'body':  store_message,
                            'attachment_ids':[( 4, wizard.attachment_ids.ids)],
                            'channel_ids' : [( 4, wizard.channel_ids.ids)]
                            })
                elif len(wizard.channel_ids) :
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
            self.mapped('todoline_id').write({'state': 'finish', 'finish_date': fields.Datetime.now()})
            
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
                                    'status_report' : 'finish',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                        
                        if len(wizard.attachment_ids) :
                            atth = wizard.attachment_ids[0]
                            image_attch = self.env['ir.attachment']
                            full_path = image_attch._full_path(atth.store_fname)
                            image_base64 = None
                            with open(full_path, 'rb') as image:
                                image_base64 = base64.b64encode(image.read())
             
                            caption = pengirim +'/ '+wizard.project_id.name+'/ '+ wizard.task_id.name+'/ '+totprog+' %'
                            jsonBody = {
                                'group_name': groupName,
                                'image': image_base64,
                                'caption': caption
                                        }
                                 
                            r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/image/message/%s" % instanceId, 
                                headers=headers,
                                json=jsonBody)
                                 
                            print("Status code: " + str(r.status_code))
                            print("RESPONSE : " + str(r.content))
                            
                            kode = str(r.status_code)
                            if kode == '200' :
                                status = 'sent'
                            else :
                                status = 'fail'
                                  
                                  
                                  
                            obj_log = self.env['log.todotoday']
                            obj_log.create({
                                        'number_admin':groupAdmin,
                                        'group_name': groupName,
                                        'message': caption,
                                        'state' : status,
                                        'user_id': self.env.user.id,
                                        'date_report': fields.Datetime.now(),
                                        'status_report' : 'finish',
                                        'project_id': wizard.project_id.id,
                                        'task_id' : wizard.task_id.id,
                                        'attachment_ids' : [( 4, wizard.attachment_ids.ids)],
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
                                    'status_report' : 'finish',
                                    'project_id': wizard.project_id.id,
                                    'task_id' : wizard.task_id.id,
                                    'response' : str(r.content)
                                    })
                               
                               
                        if len(wizard.attachment_ids) :
                            atth = wizard.attachment_ids[0]
                            image_attch = self.env['ir.attachment']
                            full_path = image_attch._full_path(atth.store_fname)
                            image_base64 = None
                            with open(full_path, 'rb') as image:
                                image_base64 = base64.b64encode(image.read())
             
                            caption = pengirim +'/ '+wizard.project_id.name+'/ '+ wizard.task_id.name+'/ '+totprog+' %'
                            jsonBody = {
                                'group_name': groupName,
                                'image': image_base64,
                                'caption': caption
                                        }
                                 
                            r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/image/message/%s" % instanceId, 
                                headers=headers,
                                json=jsonBody)
                                 
                            print("Status code: " + str(r.status_code))
                            print("RESPONSE : " + str(r.content))
                            
                            kode = str(r.status_code)
                            if kode == '200' :
                                status = 'sent'
                            else :
                                status = 'fail'
                                  
                                  
                                  
                            obj_log = self.env['log.todotoday']
                            obj_log.create({
                                        'number_admin':groupAdmin,
                                        'group_name': groupName,
                                        'message': caption,
                                        'state' : status,
                                        'user_id': self.env.user.id,
                                        'date_report': fields.Datetime.now(),
                                        'status_report' : 'finish',
                                        'project_id': wizard.project_id.id,
                                        'task_id' : wizard.task_id.id,
                                        'attachment_ids' : [( 4, wizard.attachment_ids.ids)],
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
                                                'status_report' : 'finish',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                            
#                             if len(wizard.attachment_ids) :
#                                 atth = wizard.attachment_ids[0]
#                                 image_attch = self.env['ir.attachment']
#                                 full_path = image_attch._full_path(atth.store_fname)
#                                 print '==================file atth============', full_path
#                                 image_base64 = None
#                                 with open(full_path, 'rb') as image:
#                                     print '=============image==============', image
#                                     image_base64 = base64.b64encode(image.read())
#                  
#                                 caption = pengirim +'/ '+wizard.project_id.name+'/ '+ wizard.task_id.name+'/ '+totprog+' %'
#                                 jsonBody = {
#                                     'phone': groupAdmin,
#                                     'groupId': groupID,
#                                     'file': image_base64,
#                                     'data': image_base64,
#                                     'caption': caption
#                                             }
#                                      
#                                 r = requests.post("https://wablas.com/api/send-image-from-local", 
#                                               headers=headers,
#                                               data=jsonBody)
#                                      
#                                 print("Status code: " + str(r.status_code))
#                                 print("RESPONSE : " + str(r.content))
#                                 
#                                 kode = str(r.status_code)
#                                 if kode == '200' :
#                                     status = 'sent'
#                                 else :
#                                     status = 'fail'
#                                       
#                                       
#                                       
#                                 obj_log = self.env['log.todotoday']
#                                 obj_log.create({
#                                             'number_admin':groupAdmin,
#                                             'group_name': groupID,
#                                             'message': caption,
#                                             'state' : status,
#                                             'type_api' : 'wablas',
#                                             'user_id': self.env.user.id,
#                                             'date_report': fields.Datetime.now(),
#                                             'status_report' : 'finish',
#                                             'project_id': wizard.project_id.id,
#                                             'task_id' : wizard.task_id.id,
#                                             'attachment_ids' : [( 4, wizard.attachment_ids.ids)],
#                                             'response' : str(r.content)
#                                             })
                        
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
                                                'phone': groupAdmin,
                                                'groupId': groupID,
                                                'message': message
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
                                                'status_report' : 'finish',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                            
#                             if len(wizard.attachment_ids) :
#                                 atth = wizard.attachment_ids[0]
#                                 image_attch = self.env['ir.attachment']
#                                 full_path = image_attch._full_path(atth.store_fname)
#                                 print '==================file atth============', full_path
#                                 image_base64 = None
#                                 with open(full_path, 'rb') as image:
#                                     print '=============image==============', image
#                                     image_base64 = base64.b64encode(image.read())
#                   
#                                 caption = pengirim +'/ '+wizard.project_id.name+'/ '+ wizard.task_id.name+'/ '+totprog+' %'
#                                 jsonBody = {
#                                     'phone': groupAdmin,
#                                     'groupId': groupID,
#                                     'file': atth.store_fname,
#                                     'data': image_base64,
#                                     'caption': caption
#                                             }
#                                       
#                                 r = requests.post("https://wablas.com/api/send-image-from-local", 
#                                               headers=headers,
#                                               data=jsonBody)
#                                       
#                                 print("Status code: " + str(r.status_code))
#                                 print("RESPONSE : " + str(r.content))
#                                  
#                                 kode = str(r.status_code)
#                                 if kode == '200' :
#                                     status = 'sent'
#                                 else :
#                                     status = 'fail'
#                                        
#                                        
#                                        
#                                 obj_log = self.env['log.todotoday']
#                                 obj_log.create({
#                                             'number_admin':groupAdmin,
#                                             'group_name': groupID,
#                                             'message': caption,
#                                             'state' : status,
#                                             'type_api' : 'wablas',
#                                             'user_id': self.env.user.id,
#                                             'date_report': fields.Datetime.now(),
#                                             'status_report' : 'finish',
#                                             'project_id': wizard.project_id.id,
#                                             'task_id' : wizard.task_id.id,
#                                             'attachment_ids' : [( 4, wizard.attachment_ids.ids)],
#                                             'response' : str(r.content)
#                                             })
                            
                        if len(wizard.channel_ids):
                            for c in wizard.channel_ids:
                                if c.wagroup_id :
                                    print '=========================cahnnel group================', c.wagroup_id.group_id,c.wagroup_id.group_name,c.wagroup_id.number_admin  
                             
                                    token = kon.token
                                       
                                    groupAdmin = c.wagroup_id.number_admin
                                    groupID  = c.wagroup_id.group_id
                                    message  = store_message_wa
                                       
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
                                                'status_report' : 'finish',
                                                'project_id': wizard.project_id.id,
                                                'task_id' : wizard.task_id.id,
                                                'response' : str(r.content)
                                                })
                            
                        
                        
                
        return {'type': 'ir.actions.act_window_close'}


    

    