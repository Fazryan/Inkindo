# -*- coding: utf-8 -*-

from odoo import models, fields, api
 
class Task(models.Model):
    _inherit = 'project.task'
    

#     note = fields.Text('Note', default='', sanitize_style=True, strip_classes=True)
#     next_activity = fields.Text('Next Activity')
#     problem_solution = fields.Text('Problem & Solution')
#     
#     jam = fields.Char('Jam')
     
     
#     @api.multi
#     def action_sent_message(self):
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = ir_model_data.get_object_reference('fit_task_report', 'task_report_send_email')[1]
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#         except ValueError:
#             compose_form_id = False
#         ctx = dict()
#         ctx.update({
#             'default_model': 'project.task',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#               
#         })
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#             }
    


    
            