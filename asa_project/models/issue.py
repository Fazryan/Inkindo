from odoo import api, fields, models, tools, _

class Issue(models.Model):
    _inherit = 'project.issue'
    
    
    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        if vals.get('project_id') and not self.env.context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        if vals.get('user_id') and not vals.get('date_open'):
            vals['date_open'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals.update(self.update_date_closed(vals['stage_id']))

        # context: no_log, because subtype already handle this
        context['mail_create_nolog'] = True
        issue = super(Issue, self.with_context(context)).create(vals)
        if self._context.get('default_model') == 'project.problem' and self._context.get('default_res_id'):
                order = self.env['project.problem'].browse([self._context['default_res_id']])
                order.issue_id = issue.id
        return issue