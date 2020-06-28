from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from itertools import groupby

class ProjectMeeting(models.Model):
    _name = "project.meeting"
    _description = "Minutes of Meeting"
    _order = "date_from desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
   
    
    project_id = fields.Many2one('project.project', string='Project', required=True,)
    project_location = fields.Char(string=' Project Location',store=True,related='project_id.location', readonly=True)
    consultan = fields.Char('Consultan')
    owner_id = fields.Many2one('res.partner',string='Client/Owner')
    company_id = fields.Many2one('res.company',string='Company')
    description = fields.Char(string='Project Description',store=True,related='project_id.description', readonly=True)
    name = fields.Char('Meeting Name')
    meeting_location = fields.Char(string=' Meeting Location')
    date_from = fields.Datetime(string="Date From", default=fields.Datetime.now, required=True)
    date_to = fields.Datetime(string="Date To")
    line_ids = fields.One2many('project.meeting.line', 'meeting_id', string='Meeting Line', copy=True)
    attendence_ids = fields.One2many('project.attenden', 'meeting_id', string='Attendees', copy=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('sent', 'Sent'),
        
        ], string='Status', readonly=True,  default='draft')
    
    
    
    @api.multi
    def project_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.line_ids, lambda l: l.categ_id):
           
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'lines': list(lines)
            })

        return report_pages
    
    @api.multi
    def project_meeting_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.attendence_ids, lambda l: l.parent_id):
           
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'lines': list(lines)
            })

        return report_pages
    
    @api.onchange('project_id','partner_id')                     
    def _get_partner(self):
        for o in self:
            o.owner_id = o.project_id.partner_id.id
            
    @api.multi
    def action_valid(self):
        self.write({'state': 'validate'})
            
    @api.multi
    def action_sent(self):
        #self.write({'state': 'sent'})
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('asa_project', 'meeting_send_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'project.meeting',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
            
        }
            
            
class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'project.meeting' and self._context.get('default_res_id'):
            if not self.filtered('subtype_id.internal'):
                order = self.env['project.meeting'].browse([self._context['default_res_id']])
                if order.state == 'validate':
                    order.state = 'sent'
        return super(MailComposeMessage, self.with_context(mail_post_autofollow=True)).send_mail(auto_commit=auto_commit) 
    
class ProjectMeetingLine(models.Model):
    _name = "project.meeting.line"
    _order = 'sequence'
    

    number = fields.Char('No')
    item = fields.Char(string='Item')
    description = fields.Html(string='Description')
    partner_id = fields.Many2one('res.partner',string='PIC')
    date = fields.Date(string='Date')
    due_date = fields.Date(string="Due Date")
    meeting_id = fields.Many2one('project.meeting', string='Meeting Reference')
    categ_id = fields.Many2one('project.meeting.categ',string='Category')
    task_id = fields.Many2one('project.task', string='Reference')
    sequence = fields.Integer(string='Sequence', default=10)

                    
    
    
    @api.multi
    def action_convert(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        task_form_id = ir_model_data.get_object_reference('project', 'view_task_form2')[1]
         
        ctx = dict()
        ctx.update({
            'default_model': 'project.meeting.line',
            'default_res_id': self.ids[0],
            'default_name': self.item,
            'default_date_deadline': self.due_date,
            'default_project_id': self.meeting_id.project_id.id,
            
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'views': [(task_form_id, 'form')],
            'view_id': task_form_id,
            'target': 'new',
            'context': ctx,
            
        }
        
            

    
class CategoryMeet(models.Model):
    _name = "project.meeting.categ"

    name = fields.Char(string="Category",required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Category name already exists !"),
    ]
    
class Attendees(models.Model):
    _name = "project.attenden"
    _order = 'sequence'

    partner_id = fields.Many2one('res.partner',string='Attendees')
    parent_id = fields.Many2one('res.partner',string='Company')
    meeting_id = fields.Many2one('project.meeting', string='Meeting Reference')
    sequence = fields.Integer(string='Sequence', default=10)
    
    @api.multi
    @api.onchange('partner_id','parent_id')
    def partner_id_onchange(self):
        for o in self:
            o.parent_id= o.partner_id.parent_id.id 