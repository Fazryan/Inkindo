# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource
from itertools import groupby
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

          

class ProjectDaily(models.Model):
    _name = 'project.daily'
    _description = "Daily Report"
    _order = "date_daily desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    project_id = fields.Many2one('project.project', string='Project', required=True,)
    name = fields.Char('Report Name')
    location = fields.Char(string='Location',store=True,related='project_id.location', readonly=True)
    consultan = fields.Char('Consultan')
    partner_id = fields.Many2one('res.partner',string='Client/Owner')
    company_id = fields.Many2one('res.company',string='Company')
    description = fields.Char(string='Project Description',store=True,related='project_id.description', readonly=True)
    galery_ids = fields.One2many('project.galery', 'daily_id', string='Photo Galery', copy=True)
    material_ids = fields.One2many('project.material', 'daily_id', string='Material & Equipment', copy=True)
    activity_ids = fields.One2many('project.activity', 'daily_id', string='Activity', copy=True)
    issue_ids = fields.One2many('project.problem', 'daily_id', string='Problem', copy=True)
    manpower_ids = fields.One2many('project.manpower', 'daily_id', string='Manpower', copy=True)
    weather_ids = fields.One2many('project.weather', 'daily_id', string='Weather', copy=True)
    date_daily = fields.Date(string='Date', default=fields.Date.context_today)
    start_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='Start Time')
    start_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='Start Time', default='00')
    end_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='End Time')
    end_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='End Time', default='00')
    start = fields.Float(string='Start Time', compute='_compute_duration', store=True, readonly=True)
    end = fields.Float(string='End Time', compute='_compute_duration', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('sent', 'Sent'),
        
        ], string='Status', readonly=True,  default='draft')
    total_person = fields.Integer(string='Total Person', store=True, readonly=True, compute='_person_all')
    total_durasi = fields.Float(string='Total Duration', store=True, readonly=True, compute='_durasi_all')
    notes = fields.Html(string='Notes')
    
    @api.depends('start_time_jam','start_time_menit','end_time_jam','end_time_menit')
    def _compute_duration(self):
        for o in self:
            start = float(int(o.start_time_jam)+float(o.start_time_menit))
            end = float(int(o.end_time_jam)+float(o.end_time_menit))
            o.start = start
            o.end = end
           
   
    
    @api.depends('manpower_ids.person')
    def _person_all(self):
        for order in self:
            for line in order.manpower_ids:
                order.total_person += line.person
                
    @api.depends('weather_ids.duration')
    def _durasi_all(self):
        for order in self:
            for line in order.weather_ids:
                order.total_durasi += line.duration
                
    
    @api.multi
    def action_valid(self):
        self.write({'state': 'validate'})
        
    @api.multi
    def action_sent(self):
        #self.write({'state': 'sent'})
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('asa_project', 'daily_send_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'project.daily',
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
        
    @api.multi
    def action_sent_const(self):
        #self.write({'state': 'sent'})
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('asa_project', 'const_send_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'project.daily',
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
        

   
    @api.onchange('project_id','partner_id')                     
    def _get_partner(self):
        for o in self:
            o.partner_id = o.project_id.partner_id.id
            
    @api.multi
    def project_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.manpower_ids, lambda l: l.parent_id):
           
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'lines': list(lines)
            })

        return report_pages
    
    @api.multi
    def project_weather_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.weather_ids, lambda l: l.categ_weather_id):
           
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'lines': list(lines)
            })

        return report_pages
           
           
class PhotoGalery(models.Model):
    _name = 'photo.galery'
    

    name = fields.Char('Photo Name')
    image = fields.Binary(
        "Photo", help="Image of the product variant (Big-sized image of product template if false). It is automatically "
             "resized as a 1024x1024px image, with aspect ratio preserved.")
    image_small = fields.Binary(
        "Small-sized image", compute='_compute_images', inverse='_set_image_small',
        help="Image of the product variant (Small-sized image of product template if false).")
    image_medium = fields.Binary(
        "Medium-sized image", compute='_compute_images', inverse='_set_image_medium',
        help="Image of the product variant (Medium-sized image of product template if false).")
    descrip = fields.Char('Description')
    picture_date = fields.Date(string='Picture Date')
    project_id = fields.Many2one('project.project', string='Project',required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True,)
    
    
    
    
    
    @api.one
    def _compute_images(self):
        if self._context.get('bin_size'):
            self.image_medium = self.image
            self.image_small = self.image
            
        else:
            resized_images = tools.image_get_resized_images(self.image, return_big=True, avoid_resize_medium=True)
            self.image_medium = resized_images['image_medium']
            self.image_small = resized_images['image_small']
           
        if not self.image_medium:
            self.image_medium = self.image_medium
        if not self.image_small:
            self.image_small = self.image_small
        

    @api.one
    def _set_image_medium(self):
        self._set_image_value(self.image_medium)

    @api.one
    def _set_image_small(self):
        self._set_image_value(self.image_small)

    @api.one
    def _set_image_value(self, value):
        image = tools.image_resize_image_big(value)
        if self.image:
            self.image = image
            
    
    
class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'project.daily' and self._context.get('default_res_id'):
            if not self.filtered('subtype_id.internal'):
                order = self.env['project.daily'].browse([self._context['default_res_id']])
                if order.state == 'validate':
                    order.state = 'sent'
        return super(MailComposeMessage, self.with_context(mail_post_autofollow=True)).send_mail(auto_commit=auto_commit)           
    
        
class Material(models.Model):
    _name = 'project.material'
    _rec_name = 'product_id'
    _order = 'sequence'

    product_id = fields.Many2one('product.product', string='Description', change_default=True, ondelete='restrict', required=True)
    product_uom = fields.Many2one('product.uom', string='Unit', required=True)
    qty = fields.Float(string='Quantity', required=True, default=1.0)
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    sequence = fields.Integer(string='Sequence', default=10)
    
    @api.multi
    @api.onchange('product_id','product_uom')
    def product_id_onchange(self):
        for o in self:
            o.product_uom= o.product_id.uom_id.id
              

            
class Activity(models.Model):
    _name = 'project.activity'
    _rec_name = 'task_id'
    _order = 'sequence'

    task_id = fields.Many2one('project.task', string='Description', required=True,)
    progres = fields.Float(compute='_progres_get', store=True, string='Actual (%)')
    #actual = fields.Float(compute='_actual_get', store=True, string='Plan (%)')
    plan = fields.Float(compute='_plan_get', store=True, string='Plan (%)')
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    sequence = fields.Integer(string='Sequence', default=10)
    deviasi = fields.Float(compute='_compute_deviasi', string='Deviasi (%)')
    
    @api.depends('plan','progres')
    def _compute_deviasi(self):
        for obj in self :
            obj.deviasi = obj.progres - obj.plan
    
    #sekarang Actual
    @api.multi
    @api.depends('task_id.progres_ids')
    def _progres_get(self):
        #self.ensure_one()
        for activity in self:  
            if activity.task_id:
                    domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    obj_prog = self.env['project.progres'].search(domain)
                    for o in obj_prog:
                        activity.progres += o.progres
                        
    #@api.multi
    #@api.depends('task_id.progres_ids')
    #def _actual_get(self):
        #self.ensure_one()
        #for activity in self:  
            #if activity.task_id:
                    #domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    #obj_prog = self.env['project.progres'].search(domain)
                    #for o in obj_prog:
                        #activity.actual += o.actual
                        
    @api.multi
    @api.depends('task_id.progres_ids')
    def _plan_get(self):
        #self.ensure_one()
        for activity in self:  
            if activity.task_id:
                    domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    obj_prog = self.env['project.progres'].search(domain)
                    for o in obj_prog:
                        activity.plan += o.plan
                        
                        
                        
    
class Problem(models.Model):
    _name = 'project.problem'
    _order = 'sequence'
    

    name = fields.Char(string='Item')
    solution = fields.Text('Solutions')
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    issue_id = fields.Many2one('project.issue', string='Reference')
    check = fields.Boolean('Skip on Report', default=False)
    sequence = fields.Integer(string='Sequence', default=10)
    
    @api.multi
    def action_convert(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        issue_form_id = ir_model_data.get_object_reference('project_issue', 'project_issue_form_view')[1]
         
        ctx = dict()
        ctx.update({
            'default_model': 'project.problem',
            'default_res_id': self.ids[0],
            'default_name': self.name,
            'default_project_id': self.daily_id.project_id.id,
            'default_description': self.solution,
            
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.issue',
            'views': [(issue_form_id, 'form')],
            'view_id': issue_form_id,
            'target': 'new',
            'context': ctx,
            
        }
        
    
    
    
    
class ProjectDesignation(models.Model):
    _name = "project.designation"

    name = fields.Char(required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Designation name already exists !"),
    ]
    
    

class Manpower(models.Model):
    _name = 'project.manpower'
    _rec_name = 'designation_id'
    _order = 'sequence'

    designation_id = fields.Many2one('project.designation', string='Designation')
    partner_id = fields.Many2one('res.partner',string='Name')
    parent_id = fields.Many2one('res.partner',string='Company')
    person = fields.Integer(string='Person')   
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    sequence = fields.Integer(string='Sequence', default=10)
           
    @api.multi
    @api.onchange('partner_id','parent_id')
    def partner_id_onchange(self):
        for o in self:
            o.parent_id= o.partner_id.parent_id.id 
            
class Galery(models.Model):
    _name = 'project.galery'
    _rec_name = 'photo_id'
    _order = 'sequence'

    photo_id = fields.Many2one('photo.galery', string='Photo Name', required=True,)
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    descrip = fields.Char(string='Description',store=True,related='photo_id.descrip', readonly=True)
    date = fields.Date(string='Picture Date',store=True,related='photo_id.picture_date', readonly=True)
    project_id = fields.Many2one('project.project', string='Project',required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True,)
    sequence = fields.Integer(string='Sequence', default=10)
    progres = fields.Float(compute='_progres_get', store=True, string='Actual (%)')
    #actual = fields.Float(compute='_actual_get', store=True, string='Plan (%)')
    plan = fields.Float(compute='_plan_get', store=True, string='Plan (%)')
    
    @api.multi
    @api.onchange('photo_id','task_id')
    def partner_id_onchange(self):
        for o in self:
            o.task_id= o.photo_id.task_id.id 
            o.project_id = o.photo_id.project_id.id
            
    #sekarang Actual
    @api.multi
    @api.depends('task_id.progres_ids')
    def _progres_get(self):
        #self.ensure_one()
        for activity in self:  
            if activity.task_id:
                    domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    obj_prog = self.env['project.progres'].search(domain)
                    for o in obj_prog:
                        activity.progres += o.progres
                        
    #@api.multi
    #@api.depends('task_id.progres_ids')
    #def _actual_get(self):
        #self.ensure_one()
        #for activity in self:  
            #if activity.task_id:
                    #domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    #obj_prog = self.env['project.progres'].search(domain)
                    #for o in obj_prog:
                        #activity.actual += o.actual
                        
    @api.multi
    @api.depends('task_id.progres_ids')
    def _plan_get(self):
        #self.ensure_one()
        for activity in self:  
            if activity.task_id:
                    domain = [('date', '<=', activity.daily_id.date_daily),('task_id', '=', activity.task_id.id)]
                    obj_prog = self.env['project.progres'].search(domain)
                    for o in obj_prog:
                        activity.plan += o.plan
    
    
class Weather(models.Model):
    _name = 'project.weather'
    _order = 'sequence'
    
    
    start_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='Start Time')
    start_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='Start Time', default='00')
    end_time_jam = fields.Selection([
        ('1', '01'),('2', '02'),('3', '03'),('4', '04'),('5', '05'),('6', '06'),('7', '07'),
        ('8', '08'),('9', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),
        ('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),
        ('22', '22'),('23', '23'),('24', '24')
        ], string='End Time')
    end_time_menit = fields.Selection([
        ('00', '00'),('0.50', '30')
        ], string='End Time', default='00')
    daily_id = fields.Many2one('project.daily', string='Daily Reference')
    duration = fields.Float(string='Duration', compute='_compute_duration', store=True, readonly=True)
    #weather = fields.Selection([
        #('drizzle', 'Drizzle'),
        #('pourdown', 'Pour down'),
        #], string='Weather')
    categ_weather_id = fields.Many2one('project.weather.categ',string='Weather')
    start = fields.Float(string='Start Time', compute='_compute_duration', store=True, readonly=True)
    end = fields.Float(string='End Time', compute='_compute_duration', store=True, readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    
    @api.depends('start_time_jam','start_time_menit','end_time_jam','end_time_menit')
    def _compute_duration(self):
        for o in self:
            start = float(int(o.start_time_jam)+float(o.start_time_menit))
            end = float(int(o.end_time_jam)+float(o.end_time_menit))
            o.start = start
            o.end = end
            o.duration = end - start
            
        
    
class Progress(models.Model):
    _name = "project.progres"
    _order = 'date desc'

    date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
    #sekarang actual
    progres = fields.Float('Actual (%)')
    #tdk dipakai
    actual = fields.Float('Plan (%)')
    #yg dipakai
    plan = fields.Float('Plan (%)')
    task_id = fields.Many2one('project.task', string='Task')
    bobot_actual_line = fields.Float(compute='_compute_bobot_actual_line', string='Actual Weight (%)',  store=True)
    bobot_plan_line = fields.Float(compute='_compute_bobot_plan_line', string='Plan Weight (%)',  store=True)
    
    @api.onchange('date')                     
    def _chek_date(self):
        if self.date : 
            for task in self :
                obj_progres = self.env['project.progres'].search([('task_id','=',task.task_id.id)])
                print '=============1===========', obj_progres.date 
                for date in obj_progres:  
                    print '================2=============='    
                    if task.date in date.date :
                        print '===================3============='
                        self.date = datetime.now()
                        return {'value':{},'warning':{'title':'Warning','message':'You cannot input a progress recorded on the same date'}} 
                
                
                
    @api.one
    @api.depends('task_id.nilai_kegiatan','task_id.project_id.nilai', 'progres')
    def _compute_bobot_actual_line(self):
        prj = self.env['project.project'].search([('id','=',self.task_id.project_id.id)])
        for progres in self :
            for obj in prj:
                if obj.nilai == 0 :
                    progres.bobot_actual_line = 0
                else :   
                    progres.bobot_actual_line = (progres.task_id.nilai_kegiatan / obj.nilai) * progres.progres
                    
        
    @api.one
    @api.depends('task_id.nilai_kegiatan','task_id.project_id.nilai', 'plan')
    def _compute_bobot_plan_line(self):
        prj = self.env['project.project'].search([('id','=',self.task_id.project_id.id)])
        for progres in self :
            for obj in prj:
                if obj.nilai == 0 :
                    progres.bobot_plan_line = 0
                else :   
                    progres.bobot_plan_line = (progres.task_id.nilai_kegiatan / obj.nilai) * progres.plan  
            
        
    
class CategoryWeather(models.Model):
    _name = "project.weather.categ"

    name = fields.Char(string="Weather",required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Weather name already exists !"),
    ]
    




