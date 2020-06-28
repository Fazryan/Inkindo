from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import datetime
from dateutil.relativedelta import relativedelta
import math

class Task(models.Model):
    _inherit = 'project.task'

    progres_ids = fields.One2many('project.progres', 'task_id', 'Progress')
    total_progres = fields.Float(compute='_plan_get', store=True, string=' Total Plan (%)')
    total_actual = fields.Float(compute='_progres_get', store=True, string=' Total Actual (%)')
    is_cm = fields.Boolean('Is CM', default=False)
    nilai_kegiatan = fields.Integer('Task Cost')
    bobot = fields.Float(compute='_compute_bobot', string='Task Weight(%)', store=True)
    bobot_actual = fields.Float(compute='_compute_bobot_actual', string='Actual Weight (%)',  store=True)
    deviasi = fields.Float(compute='_compute_deviasi', string='Deviasi (%)')
    plan_today = fields.Float(compute='_plan_today', store=True, string=' Total Plan Today (%)')
    actual_today = fields.Float(compute='_actual_today', store=True, string=' Total Actual Today (%)')
    
    
    #@api.depends('total_progres','total_actual')
    #def _compute_deviasi(self):
        #for obj in self :
            #obj.deviasi = obj.total_actual - obj.total_progres
            
    @api.depends('plan_today','actual_today')
    def _compute_deviasi(self):
        for obj in self :
            obj.deviasi = obj.actual_today - obj.plan_today
    
    @api.one
    @api.depends('nilai_kegiatan','project_id.nilai')
    def _compute_bobot(self):
        prj = self.env['project.project'].search([('id','=',self.project_id.id)])
        for task in self :
            for obj in prj:
                if obj.nilai == 0 :
                    task.bobot = 0
                else :   
                    task.bobot = ((task.nilai_kegiatan / obj.nilai) * 100)
                    
    @api.multi
    @api.depends('nilai_kegiatan','project_id.nilai', 'total_actual')
    def _compute_bobot_actual(self):
        prj = self.env['project.project'].search([('id','=',self.project_id.id)])
        for task in self :
            for obj in prj:
                if obj.nilai == 0 :
                    task.bobot_actual = 0
                else :   
                    task.bobot_actual = (task.nilai_kegiatan / obj.nilai) * task.total_actual
                    
    @api.multi
    @api.depends('nilai_kegiatan','project_id.nilai', 'total_actual')
    def recompute_bobot(self):
        prj = self.env['project.project'].search([('id','=',self.project_id.id)])
        for task in self :
            for obj in prj:
                if obj.nilai == 0 :
                    task.bobot_actual = 0
                    task.bobot = 0
                else :   
                    task.bobot_actual = (task.nilai_kegiatan / obj.nilai) * task.total_actual
                    task.bobot = ((task.nilai_kegiatan / obj.nilai) * 100)
    
    #sekarang jadi Actual
    @api.depends('progres_ids.progres')
    def _progres_get(self):
        for task in self:
            for line in task.progres_ids:
                task.total_actual += line.progres
                if task.total_actual > 100 :
                    raise ValidationError('You cannot input progress actual more than 100%')
                

    @api.depends('progres_ids.plan')
    def _plan_today(self):
        now = datetime.datetime.now()
        date_now = now.strftime('%Y-%m-%d')
        for task in self:
            for line in task.progres_ids:
                if line.date <= date_now :
                    task.plan_today += line.plan
                    
    @api.depends('progres_ids.progres')
    def _actual_today(self):
        now = datetime.datetime.now()
        date_now = now.strftime('%Y-%m-%d')
        for task in self:
            for line in task.progres_ids:
                if line.date <= date_now :
                    task.actual_today += line.progres
                
    #sekarang Plan            
    @api.depends('progres_ids.plan')
    def _plan_get(self):
        for task in self:
            for line in task.progres_ids:
                task.total_progres += line.plan
                if task.total_progres > 100 :
                    raise ValidationError('You cannot input progress plan more than 100%')
                
    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        task = super(Task, self.with_context(context)).create(vals)
        
        if self._context.get('default_model') == 'project.meeting.line' and self._context.get('default_res_id'):
                order = self.env['project.meeting.line'].browse([self._context['default_res_id']])
                order.task_id = task.id
        return task

    @api.multi
    def test(self):
        task_obj = self.env['project.progres']
        dtstart=fields.Date.from_string(self.date_start)
        dtend=fields.Date.from_string(self.date_end)
        d1 = datetime.datetime.strptime(self.date_start,'%Y-%m-%d %H:%M:%S')
        start = d1.date()
        d2 = datetime.datetime.strptime(self.date_end,'%Y-%m-%d %H:%M:%S')
        end = d2.date()
        #end_date = end + timedelta(days=1)
        #print '======end===========', end_date
        kurang = end - start
        day = (float(kurang.days)+1)
        #print '=================day================', day
        #print '===============date===========', start , end, kurang.days
        if not self.date_end :
            raise ValidationError('Ending Date not filled')
            
        if self.progres_ids :
            raise ValidationError('There is Progress Line found.' 
            '\n This function is only for task with no progress line inputed.')
        else :
            #diff = fields.Datetime.from_string(self.date_end) - fields.Datetime.from_string(self.date_start)
            #day = float(diff.days)
            #print '==================diff================', day
            x = 100/day
            data = (math.floor(x*100)/100)
            print '===============data============', data
            while start <= end :
                task_obj.create({
                    'task_id':self.id,
                    'date':start,
                    'plan':data
                    
                    })
                start += timedelta(days=1)
        if self.total_progres < 100 :
            print self.total_progres
            return {'value':{},'warning':{'title':'Warning','message':'The Total of Calculated weight is xx.xx%. You need edit the line to make the total become 100%'}} 
        
        return True


    
        


    
