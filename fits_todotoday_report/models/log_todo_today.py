from odoo import _, api, fields, models, tools
import time
import requests
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)
MAX_RETRY = 3

class LogTodoToday(models.Model):
    _name = 'log.todotoday'
    _description = "Log To do Today"
    _rec_name ="state"
    
    
    number_admin = fields.Char('Number Admin Group To do Today ')
    group_name = fields.Char('Group Name To do Today')
    message = fields.Text('Message')
    state = fields.Selection([
        ('sent', 'Delivered'),
        ('fail', 'Failled')
        ], string='Status Whatsapp', readonly=True)
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp')
    user_id = fields.Many2one('res.users','Employee')
    date_report = fields.Datetime('Date Report')
    status_report = fields.Char('Status Report')
    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    response = fields.Char('Response')
    
    
    def send_wa_todotoday(self):
        kon_whatsmate = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate')],limit=1)
        kon_wablas = self.env['whatsapp.konf'].search([('type_api','=', 'wablas')],limit=1)
 
        instanceId = kon_whatsmate.instance_id
        clientId = kon_whatsmate.client_id
        clientSecret = kon_whatsmate.client_scret
        token = kon_wablas.token
         
         
        for log in self.search([('state','=','fail'),
                                ('date_report','<',time.strftime('%Y-%m-%d %H:%M:%S'))]):
            
            if log.type_api == 'whatsmate' :
            
                groupAdmin = log.number_admin
                groupName = log.group_name
                message = log.message
                 
                headers = {
                    'X-WM-CLIENT-ID': clientId, 
                    'X-WM-CLIENT-SECRET': clientSecret
                }
                 
                if log.attachment_ids :
                    atth = log.attachment_ids[0]
                    image_attch = self.env['ir.attachment']
                    full_path = image_attch._full_path(atth.store_fname)
                    print '==================file atth============', full_path
                    image_base64 = None
                    with open(full_path, 'rb') as image:
                        print '=============image==============', image
                        image_base64 = base64.b64encode(image.read())
         
                    caption = log.message
                    jsonBody = {
                        'group_name': groupName,
                        'image': image_base64,
                        'caption': caption
                                    }
                             
                    r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/image/message/%s" % instanceId, 
                            headers=headers,
                            json=jsonBody)
                             
                    print("Status code: " + str(r.status_code))
                    print("RESPONSE : " + str(r.content))
                        
                    kode = str(r.status_code)
                    if kode == '200' :
                            status = 'sent'
                    else :
                            status = 'fail'
                    log.write({'state':status })
                    
                else :   
                     
                    jsonBody = {
                        'group_admin': groupAdmin,
                        'group_name': groupName,
                        'message': message
                    }
                    
                    print'================send wa==================',groupAdmin, groupName
                 
                    r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
                        headers=headers,
                        json=jsonBody)
                    
                    kode = str(r.status_code)
                    print '============kode==============', kode
                    if kode == '200' :
                        status = 'sent'
                    else :
                        status = 'fail'
                        
                    log.write({'state':status })
            else :
                groupAdmin = log.number_admin
                groupName = log.group_name
                message = log.message
                 
                headers = {
                                'Authorization': token
                            }
                           
                jsonBody = {
                                'phone': groupAdmin,
                                'groupId': groupName,
                                'message': message
                            }
                           
                r = requests.post("https://simo.wablas.com/api/send-group", 
                                          headers=headers,
                                          data=jsonBody)
                        
                kode = str(r.status_code)
                if kode == '200' :
                    status = 'sent'
                else :
                    status = 'fail'
                        
                log.write({'state':status })
                
class logAutodelete(models.TransientModel):
    _name = 'log.autodelete'
    _description = "Todo Log - Delete old logs"

    @api.model
    def autodelete(self, days):
        """Delete all logs older than ``days``. This includes:
            - CRUD logs (create, read, write, unlink)
            - HTTP requests
            - HTTP user sessions

        Called from a cron.
        """
        days = (days > 0) and int(days) or 0
        deadline = datetime.now() - timedelta(days=days)
        data_models = (
            'log.todotoday',
        )
        for data_model in data_models:
            records = self.env[data_model].search(
                [('create_date', '<=', fields.Datetime.to_string(deadline))])
            nb_records = len(records)
            records.unlink()
            _logger.info(
                u"AUTOVACUUM - %s '%s' records deleted",
                nb_records, data_model)
        return True
             
        
            
            
            