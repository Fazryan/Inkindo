
from odoo import models, fields, api, exceptions

class todotodayline(models.Model):
    _name = 'todo.today.line'
    _description = "To do Today Report"
    _order = 'sequence'
    

    project_id = fields.Many2one('project.project', string='Project',required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    stage = fields.Char(string='Stage',related='task_id.stage_id.name', readonly=True)
    pm = fields.Many2one(string='Project Manager',related='project_id.user_id', readonly=True)
    desc = fields.Html('Description', required=True) 
    duration = fields.Float('Duration')
    state = fields.Selection([
        ('draft', 'PREPARATION'),
        ('start', 'ON GOING'),
        ('cancel', 'CANCEL'),
        ('finish', 'DONE')
        ], string='Status', readonly=True,  default='draft', track_visibility='onchange')
    todo_id = fields.Many2one('todo.today', ondelete='cascade', string="To do Today", required=True)
    employee_id = fields.Many2one('res.users',related='todo_id.employee_id',string='Employee',
                                      store=True, readonly=True)
    date = fields.Date(string='Date', related='todo_id.date',
                                      store=True, readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    start_date = fields.Datetime(string='Datetime Start',readonly=True, copy=False)
    finish_date = fields.Datetime(string='Datetime Finish',readonly=True, copy=False)
    cancel_date = fields.Datetime(string='Datetime Cancel',readonly=True, copy=False)
    
    
    @api.constrains('duration')
    def _check_duration(self):
        for r in self:
            if r.duration == 0 :
                raise exceptions.ValidationError("Duration must not be 00:00")