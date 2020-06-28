from odoo import models, fields, api, exceptions


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    todo_id = fields.Many2one('todo.today', string="To do Today")
    
class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'
 
    expected_hours = fields.Float(track_visibility='onchange')
     
    @api.constrains('expected_hours')
    def _expected_hours(self):
        if self.expected_hours == 0:
            raise exceptions.ValidationError("Expected Hours should not be 0.....!!")
    
class Task(models.Model):
    _inherit = 'project.task'
    
    
    @api.constrains('planned_hours')
    def _planned_hours(self):
        if self.planned_hours == 0:
            raise exceptions.ValidationError("Initially Planned Hours should not be 0.....!!")
        

class Project(models.Model):
    _inherit = 'project.project'
    
    
    total_planned = fields.Float(string='Total Planned Hours', compute='_get_total')
    total_efective = fields.Float(string='Total Actual Hours', compute='_get_total')
    
    
    #@api.multi
    #@api.depends('task_ids.planned_hours','task_ids.effective_hours')
    #def _get_total(self):
        #task = self.env['project.task'].search([('project_id','=',self.id)])
        #for x in task:
            #self.total_planned += x.planned_hours
            #self.total_efective += x.effective_hours 
            
            
    @api.multi
    @api.depends('task_ids.planned_hours','task_ids.effective_hours')
    def _get_total(self):
        for p in self :
            task = self.env['project.task'].search([('project_id','=',p.id)])
            for x in task:
                p.total_planned += x.planned_hours
                p.total_efective += x.effective_hours 