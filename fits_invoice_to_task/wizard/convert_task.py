from odoo import api, models, fields, tools, _

class ConvertTask(models.TransientModel):
    _name = "convert.task"
    _description = "Convert To Task"
    
    name = fields.Many2one('project.project', string ='Project Name',  required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference')
    convert_task_ids = fields.One2many('line.invoice.task', 'convert_id', string="Invoice Line")
    invoice_line = fields.Boolean('Invoice Line', default=True)
    
    @api.model
    def default_get(self, fields):
        res = super(ConvertTask, self).default_get(fields)
        if self.env.context.get('active_model') == 'account.invoice' and self.env.context.get('active_id'):
            res['invoice_id'] = self.env['account.invoice'].browse(self.env.context['active_id']).id
            res['partner_id'] = self.env['account.invoice'].browse(self.env.context['active_id']).partner_id.id
        return res
    
    @api.multi
    def get_invoice_line(self):
        order_line_obj = self.env['account.invoice.line'].search([('invoice_id', '=', self.invoice_id.id)])
        line_list = []
        for x in order_line_obj :
            vals = {
                'convert_id': self.id,
                'product': x.product_id.name,
                'invoice_line_id' : x.id 
                }
            line_list.append((0, 0, vals))
        self.convert_task_ids = line_list
        
    
    @api.onchange('invoice_line')
    def _onchange_invoice_task(self):
        if self.invoice_line:                
            self.get_invoice_line()
            
   
    @api.multi
    def convert_task(self):
        if len(self.convert_task_ids) != 0 :
            for x in self.convert_task_ids :
                task = self.env['project.task']
                task.create({
                    'name': x.product,
                    'partner_id': self.partner_id.id,
                    'user_id': self.env.uid,
                    'project_id': self.name.id,
                    'invoice_line_id': x.invoice_line_id.id,
                    'flag_stage': True
                    })
            self.mapped('invoice_id').write({'convert_status': 'convert'})
             
        return {'type': 'ir.actions.act_window_close'}
    
class LineInvoiceTask(models.TransientModel):
    _name = "line.invoice.task"
    _description = "Line Invoice Task"
    
    convert_id = fields.Many2one('convert.task', string="Invoice")
    product = fields.Char(string='Product Name')
    invoice_line_id = fields.Many2one('account.invoice.line', 'Account Invoice Line')
    
    