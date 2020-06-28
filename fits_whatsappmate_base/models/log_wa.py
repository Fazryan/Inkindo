from odoo import _, api, fields, models, tools
import time
import requests
import base64
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)
MAX_RETRY = 3

class LogWa(models.Model):
    _name = 'log.wa'
    _description = "Log WhatsApp"
    _rec_name ="state"
    
    
    number_admin = fields.Char('Number')
    group_name = fields.Char('Group Name/ID')
    message = fields.Text('Message')
    state = fields.Selection([
        ('sent', 'Delivered'),
        ('fail', 'Failled')
        ], string='Status Whatsapp', readonly=True)
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp')
    type_send = fields.Selection([
        ('group', 'Group'), ('personal', 'Personal')], string='Type Send')
    date_report = fields.Datetime('Date')
    response = fields.Char('Response')
    
    
    def send_wa_log(self):
        kon_whatsmate = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate')],limit=1)
        kon_wablas = self.env['whatsapp.konf'].search([('type_api','=', 'wablas')],limit=1)
 
        instanceId = kon_whatsmate.instance_id
        clientId = kon_whatsmate.client_id
        clientSecret = kon_whatsmate.client_scret
        token = kon_wablas.token
         
         
        for log in self.search([('state','=','fail'),
                                ('date_report','<',time.strftime('%Y-%m-%d %H:%M:%S'))]):
            if log.type_send == 'group' :
            
                if log.type_api == 'whatsmate' :
                
                    groupAdmin = log.number_admin
                    groupName = log.group_name
                    message = log.message
                     
                    headers = {
                        'X-WM-CLIENT-ID': clientId, 
                        'X-WM-CLIENT-SECRET': clientSecret
                    }
                     
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
                            
                    log.write({'state':status, 'response':str(r.content) })
                    
                elif log.type_api == 'wablas' :
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
                            
                    log.write({'state':status, 'response':str(r.content) })
                    
                else :
                    print '====================tdk ada type==================='
                    
            elif log.type_send == 'personal' :
                if log.type_api == 'whatsmate' :
                    print '================belum dibuat================='
                
#                     groupAdmin = log.number_admin
#                     message = log.message
#                      
#                     headers = {
#                         'X-WM-CLIENT-ID': clientId, 
#                         'X-WM-CLIENT-SECRET': clientSecret
#                     }
#                      
#                     jsonBody = {
#                             'group_admin': groupAdmin,
#                             'message': message
#                         }
#                         
#                     print'================send wa==================',groupAdmin, groupName
#                      
#                     r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
#                             headers=headers,
#                             json=jsonBody)
#                         
#                     kode = str(r.status_code)
#                     print '============kode==============', kode
#                     if kode == '200' :
#                         status = 'sent'
#                     else :
#                         status = 'fail'
#                             
#                     log.write({'state':status, 'response':str(r.content) })
                    
                elif log.type_api == 'wablas' :
                    groupAdmin = log.number_admin
                    message = log.message
                     
                    headers = {
                                    'Authorization': token
                                }
                               
                    jsonBody = {
                                    'phone': groupAdmin,
                                    'message': message
                                }
                               
                    r = requests.post("https://simo.wablas.com/api/send-message", 
                                              headers=headers,
                                              data=jsonBody)
                            
                    kode = str(r.status_code)
                    if kode == '200' :
                        status = 'sent'
                    else :
                        status = 'fail'
                            
                    log.write({'state':status, 'response':str(r.content) })
                    
                else :
                    print '====================tdk ada type==================='
                    
            else :
                print '=================tidak ada type send============================='
                
                
             
        
            
            
            