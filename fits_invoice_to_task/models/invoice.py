# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    tasks_ids = fields.Many2many('project.task', compute='_compute_tasks_ids', string='Tasks associated to this Invoice')
    tasks_count = fields.Integer(string='Tasks', compute='_compute_tasks_ids')
    test = fields.Char('Test')
    convert_status = fields.Selection([
        ('no', 'No Convert Task'),
        ('convert', 'Convert to Task'),
        ], string='Convert Status', readonly=True, default = 'no')

    
    
    @api.multi
    def _compute_tasks_ids(self):
        for invoice in self:
            invoice.tasks_ids = self.env['project.task'].search([('invoice_line_id', 'in', invoice.invoice_line_ids.ids)])
            invoice.tasks_count = len(invoice.tasks_ids)
            
    @api.multi
    def action_view_task(self):
        self.ensure_one()
        action = self.env.ref('project.action_view_task')
        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot'], [False, 'graph']],
            'target': action.target,
            'context': "{'group_by':'stage_id'}",
            'res_model': action.res_model,
        }
        if len(self.tasks_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % self.tasks_ids.ids
        elif len(self.tasks_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = self.tasks_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
