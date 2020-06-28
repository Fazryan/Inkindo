from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class TaskTimesheetReport(models.TransientModel):
    _name = "task.timesheet.report"
    _description = "Task Timesheet Report"
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    #_mail_post_access = 'read'
    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    
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
    channel_ids = fields.Many2many('mail.channel', string='Channels', required=True)
    work_time = fields.Float(string='Today Work Time', compute='_compute_worktime',  readonly=True)
    istirahat = fields.Float(string='Break')
    effective_hours = fields.Float( string='Last Man Day(s)', readonly=True)
    planned_hours = fields.Float( string='Initially Planned Man Day(s).', readonly=True)
    total_effective = fields.Float(compute='_total_effective', string=' Total Man Day(s)')
    
  
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
            if len(follow_ids_list)!= 0 :
                for x in follow_ids_list :
                    user.append(x.channel_id.id)
                    self.channel_ids = user
            else :
                user_channel = []
                channel_obj=self.env['mail.channel.partner']
                channel_ids_list =  channel_obj.search([('partner_id.name','=', self.user_id.name)])
                for x in channel_ids_list :
                    user_channel.append(x.channel_id.id) 
                    self.channel_ids = user_channel
    
    
    
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
        res = super(TaskTimesheetReport, self).default_get(fields)
        if not res.get('task_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'project.task' and self.env.context.get('active_id'):
            res['task_id'] = self.env['project.task'].browse(self.env.context['active_id']).id
            res['project_id'] = self.env['project.task'].browse(self.env.context['active_id']).project_id.id
            res['actual_today'] = self.env['project.task'].browse(self.env.context['active_id']).actual_today
            res['effective_hours'] = self.env['project.task'].browse(self.env.context['active_id']).effective_hours
            res['planned_hours'] = self.env['project.task'].browse(self.env.context['active_id']).planned_hours
        return res

    

    @api.multi
    def create_report(self):
        timesheet= self.env['account.analytic.line']
        progres =  self.env['project.progres']
        message = self.env['mail.message']
        #attachment = self.env['ir.attachment']
        for wizard in self:
            actual = str(wizard.actual_today)
            prog = str(wizard.progres)
            totprog = str(wizard.total_progres)
            durasi = str(wizard.work_time)
            s_jam = wizard.start_time_jam
            effective = str(wizard.effective_hours)
            tot_effective = str(wizard.total_effective)
            planned = str(wizard.planned_hours)
            date_now = datetime.now()
            tgl = date_now.strftime('%d-%m-%Y')
            
            if wizard.start_time_menit == '0.50':
                s_menit = '30'
            else :
                s_menit = '00'
            e_jam = wizard.end_time_jam
            if wizard.end_time_menit == '0.50':
                e_menit = '30'
            else :
                e_menit = '00'
                
            #jam = s_jam+':'+s_menit+' -- '+e_jam+':'+e_menit
            if wizard.note == False:
                note = ' '
            else :
                note = wizard.note
            if wizard.next_activity == False :
                act = ' '
            else :
                act = wizard.next_activity
            if wizard.problem_solution == False :
                pros = ' '
            else :
                pros = wizard.problem_solution 
                 
            tampung = '## Project Report '+tgl+' ##<br><br>'+'Project Name :'+' '+wizard.project_id.name+'<br>Task Name :'+' '+wizard.task_id.name \
            +'<br><br>Time :'+' '+s_jam+':'+s_menit+' -- '+e_jam+':'+e_menit+'<br>Today Work Time :'+' '+durasi+' '+'hours'+'<br>Total Work Time :'+' '+tot_effective+' '+'hours / '+planned+' '+'hours' \
            +'<br><br>Progres :'+'<br>-Last Progress :'+' '+actual+' '+'%'+'<br>-Today Progress :'+' '+prog+' '+'%'+'<br>-Total Progress :'+' '+totprog+' '+'%' \
            +'<br><br> Note :'+note+'<br>Problem & Solution :'+pros+'<br> Next Activity :'+act
            store_message = tampung.encode('utf-8').strip()
            
            print '=============store message==============', store_message
              
            
            progres.create({
                    'task_id':wizard.task_id.id,
                    'date': wizard.date_report,
                    'progres': wizard.progres
                    })
            timesheet.create({
                    'task_id':wizard.task_id.id,
                    'date': wizard.date_report,
                    'user_id': wizard.user_id.id,
                    'name': wizard.name,
                    'unit_amount': wizard.work_time,
                    'account_id' : wizard.project_id.analytic_account_id.id,
                    'project_id' : wizard.project_id.id
                    })
            
            if len(wizard.partner_ids) :
                if len(wizard.attachment_ids):
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
                else :
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
                    
                if len(wizard.attachment_ids) : 
                    message.create({
                            'res_id':wizard.task_id.id,
                            'record_name': wizard.task_id.name,
                            'model': 'project.task',
                            'message_type' : 'comment',
                            'body':  store_message,
                            'attachment_ids':[( 4, wizard.attachment_ids.ids)],
                            'channel_ids' : [( 4, wizard.channel_ids.ids)]
                            })
                else :
                    message.create({
                            'res_id':wizard.task_id.id,
                            'record_name': wizard.task_id.name,
                            'model': 'project.task',
                            'message_type' : 'comment',
                            'body':  store_message, 
                            'channel_ids' : [( 4, wizard.channel_ids.ids)]
                            })
                
#             attachment.create({
#                     'res_id':wizard.task_id.id,
#                     'res_name': wizard.task_id.name,
#                     'res_model': 'project.task',
#                     'name' : 'tessss',
#                     'datas_fname' : 'tessssssssssss',
#                     })

#             for record in self.env['project.task'].browse(self._context.get('active_ids', [])):
#                 record.jam = jam
#                 record.note = tools.html2plaintext(tampung)
#                 record.next_activity = self.next_activity
#                 record.problem_solution = self.problem_solution
#             picking_obj = self.env['project.task'].browse(wizard.task_id.id)
        return {'type': 'ir.actions.act_window_close'}


    

    