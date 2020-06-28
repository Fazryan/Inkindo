# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
import requests
from odoo.exceptions import UserError, Warning
import re

class WhatsappGroup(models.Model):
    _name = 'whatsapp.group'
    _description = "Send Message Group"
    _rec_name ="group_admin"
    
    
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp', default="whatsmate")
    group_admin = fields.Char('Group Admin Number')
    group_id = fields.Char('GroupID')
    group_name = fields.Char('Group Name')
    message = fields.Text('Message')
    
    @api.onchange('group_admin')
    def Onchange_no_wa(self):
        if self.group_admin:
            no = self.group_admin[0:3]
            print '==============no wa=============', no
            if no != '+62' :
                mobile = self.group_admin[1:]
                no_wa = '+62'+ mobile
                self.group_admin = no_wa
                
    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text
    
    
    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    

    def send_message(self, groupA, groupN, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate'), ('aktif','=', True)],limit=1)
        if kon :
            instanceId = kon.instance_id
            clientId = kon.client_id
            clientSecret = kon.client_scret
             
            groupAdmin = groupA
            groupName  = groupN
            message  = isi
             
            headers = {
                'X-WM-CLIENT-ID': clientId, 
                'X-WM-CLIENT-SECRET': clientSecret
            }
             
            jsonBody = {
                'group_admin': groupAdmin,
                'group_name': groupName,
                'message': message
            }
             
            r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
                headers=headers,
                json=jsonBody)
            
            kode = str(r.status_code)
            if kode == '200' :
                status = 'sent'
            else :
                status = 'fail'
                            
                            
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'group_name': groupName,
                                'message': message,
                                'state' : status,
                                'type_api' : 'whatsmate',
                                'type_send' : 'group',
                                'date_report': fields.Datetime.now(),
                                'response' : str(r.content)
                            })
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Whatsmate not Found or Not Active....!!!"))
            
        
    def send_message_wablas(self, groupA, groupID, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
        if kon :
            token = kon.token
             
            groupAdmin = groupA
            groupID  = groupID
            message  = isi
             
            headers = {
                'Authorization': token
            }
             
            jsonBody = {
                'phone': groupAdmin,
                'groupId': groupID,
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
                            
                            
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'group_name': groupID,
                                'message': message,
                                'state' : status,
                                'type_api' : 'wablas',
                                'type_send' : 'group',
                                'date_report': fields.Datetime.now(),
                                'response' : str(r.content)
                            })
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Wablas not Found or Not Active....!!!"))
        
    def send_wa(self):
        groupA = self.group_admin
        groupN = self.group_name
        groupID = self.group_id
        isi = self.message
        if self.type_api == 'whatsmate':
            self.send_message(groupA, groupN, isi )
        elif self.type_api == 'wablas':
            self.send_message_wablas(groupA, groupID, isi)
        else :
            print '==============tidak ada type yg dipilih================='
            
    def send_message_log(self, groupA, groupN, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate'), ('aktif','=', True)],limit=1)
        if kon :
            groupAdmin = groupA
            groupName  = groupN
            message  = isi
            #now = datetime.now() 
               
            obj_log = self.env['log.wa']
            log_sama = obj_log.search([('message','=', message)])
            if not log_sama:
                obj_log.create({
                                    'number_admin':groupAdmin,
                                    'group_name': groupName,
                                    'message': message,
                                    'state' : 'fail',
                                    'type_api' : 'whatsmate',
                                    'type_send' : 'group',
                                    'date_report': fields.Datetime.now()
                                })
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Whatsmate not Found or Not Active....!!!"))
            
        
    def send_message_wablas_log(self, groupA, groupID, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
        if kon :
            groupAdmin = groupA
            groupID  = groupID
            message  = isi
#            now = datetime.now() 
                           
                            
            obj_log = self.env['log.wa']
            log_sama = obj_log.search([('message','=', message)])
            if not log_sama :
                obj_log.create({
                                    'number_admin':groupAdmin,
                                    'group_name': groupID,
                                    'message': message,
                                    'state' : 'fail',
                                    'type_api' : 'wablas',
                                    'type_send' : 'group',
                                    'date_report': fields.Datetime.now()
                                })
                
#             if log_sama:
#                 for log in log_sama:
#                     date_log = datetime.strptime(log.date_report, "%Y-%m-%d %H:%M:%S")
#                     tgl_log = date_log.strftime('%Y-%m-%d')
#                     date_now = now.strftime('%Y-%m-%d')
#                     print '====================selisih==================', date_now, tgl_log
#                     if date_now == tgl_log :                        
#                         diff = relativedelta(now, date_log)
#                         minute = int(diff.minutes) 
#                         print '====================selisih==================', diff , diff.minutes
#                         
#                         if minute >= 5 : 
#                             obj_log.create({
#                                                 'number_admin':groupAdmin,
#                                                 'group_name': groupID,
#                                                 'message': message,
#                                                 'state' : 'fail',
#                                                 'type_api' : 'wablas',
#                                                 'type_send' : 'group',
#                                                 'date_report': fields.Datetime.now()
#                                             })
#                         else :
#                             print '==================sudah ada===================='
                   
                
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Wablas not Found or Not Active....!!!"))
        
    def send_wa_log(self):
        groupA = self.group_admin
        groupN = self.group_name
        groupID = self.group_id
        isi = self.message
        if self.type_api == 'whatsmate':
            self.send_message_log(groupA, groupN, isi )
        elif self.type_api == 'wablas':
            self.send_message_wablas_log(groupA, groupID, isi)
        else :
            print '==============tidak ada type yg dipilih================='
            
class WhatsapPersonal(models.Model):
    _name = 'whatsapp.personal'
    _description = "Send Message Personal"
    _rec_name ="group_admin"
    
    
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp', default="whatsmate")
    group_admin = fields.Char('Number')
    message = fields.Text('Message')
    
    @api.onchange('group_admin')
    def Onchange_no_wa(self):
        if self.group_admin:
            no = self.group_admin[0:3]
            print '==============no wa=============', no
            if no != '+62' :
                mobile = self.group_admin[1:]
                no_wa = '+62'+ mobile
                self.group_admin = no_wa
                
    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text
    
    
    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    

    def send_message_personal(self, groupA, isi):
        print '============================belum dibuat isinya=================='
#         kon = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate'), ('aktif','=', True)],limit=1)
#         if kon :
#             instanceId = kon.instance_id
#             clientId = kon.client_id
#             clientSecret = kon.client_scret
#              
#             groupAdmin = groupA
#             groupName  = groupN
#             message  = isi
#              
#             headers = {
#                 'X-WM-CLIENT-ID': clientId, 
#                 'X-WM-CLIENT-SECRET': clientSecret
#             }
#              
#             jsonBody = {
#                 'group_admin': groupAdmin,
#                 'group_name': groupName,
#                 'message': message
#             }
#              
#             r = requests.post("http://api.whatsmate.net/v3/whatsapp/group/text/message/%s" % instanceId, 
#                 headers=headers,
#                 json=jsonBody)
#             
#             kode = str(r.status_code)
#             if kode == '200' :
#                 status = 'sent'
#             else :
#                 status = 'fail'
#                             
#                             
#                             
#             obj_log = self.env['log.wa']
#             obj_log.create({
#                                 'number_admin':groupAdmin,
#                                 'group_name': groupName,
#                                 'message': message,
#                                 'state' : status,
#                                 'type_api' : 'whatsmate',
#                                 'date_report': fields.Datetime.now(),
#                                 'response' : str(r.content)
#                             })
#         else :
#             print '================tidak ada Account===================='
#             #raise Warning(_("Account Whatsmate not Found or Not Active....!!!"))
            
        
    def send_message_personal_wablas(self, groupA, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
        if kon :
            token = kon.token
             
            groupAdmin = groupA
            message  = isi
             
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
                            
                            
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'message': message,
                                'state' : status,
                                'type_api' : 'wablas',
                                'type_send' : 'personal',
                                'date_report': fields.Datetime.now(),
                                'response' : str(r.content)
                            })
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Wablas not Found or Not Active....!!!"))
        
    def send_wa_personal(self):
        groupA = self.group_admin
        isi = self.message
        if self.type_api == 'whatsmate':
            self.send_message_personal(groupA, isi )
        elif self.type_api == 'wablas':
            self.send_message_personal_wablas(groupA, isi)
        else :
            print '==============tidak ada type yg dipilih================='
            
    def send_message_personal_log(self, groupA, isi):
        print '================belum ada isinya=============='
#         kon = self.env['whatsapp.konf'].search([('type_api','=', 'whatsmate'), ('aktif','=', True)],limit=1)
#         if kon :
#             groupAdmin = groupA
#             message  = isi
#              
#                             
#                             
#                             
#             obj_log = self.env['log.wa']
#             obj_log.create({
#                                 'number_admin':groupAdmin,
#                                 'message': message,
#                                 'state' : 'fail',
#                                 'type_api' : 'whatsmate',
#                                 'date_report': fields.Datetime.now()
#                             })
#         else :
#             print '================tidak ada Account===================='
#             #raise Warning(_("Account Whatsmate not Found or Not Active....!!!"))
            
        
    def send_message_personal_wablas_log(self, groupA, isi):
        kon = self.env['whatsapp.konf'].search([('type_api','=', 'wablas'), ('aktif','=', True)],limit=1)
        if kon :
            groupAdmin = groupA
            message  = isi
                           
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'message': message,
                                'state' : 'fail',
                                'type_api' : 'wablas',
                                'type_send' : 'personal',
                                'date_report': fields.Datetime.now()
                            })
        else :
            print '================tidak ada Account===================='
            #raise Warning(_("Account Wablas not Found or Not Active....!!!"))
        
    def send_wa_personal_log(self):
        groupA = self.group_admin
        isi = self.message
        if self.type_api == 'whatsmate':
            self.send_message_personal_log(groupA, isi )
        elif self.type_api == 'wablas':
            self.send_message_personal_wablas_log(groupA, isi)
        else :
            print '==============tidak ada type yg dipilih================='
        
class WhatsappKonf(models.Model):
    _name = 'whatsapp.konf'
    _description = "Konfigurasi Whatsapp"
    _rec_name ="type_api"
    
    
    type_api = fields.Selection([
        ('whatsmate', 'Whatsmate'), ('wablas', 'Wablas')], string='API WhatsApp', default="whatsmate")
    aktif = fields.Boolean(string="Active", default = False)
    instance_id = fields.Char('InstanceId')
    client_id = fields.Char('ClientId')
    client_scret = fields.Char('ClientSecret')
    token = fields.Char("Token")
    
    @api.onchange('aktif')
    def active_onchange(self):
        if self.aktif == True :
            aktif = self.search([('aktif','=', True)])
            if aktif :
                return {'value':{'aktif' : False},'warning':{'title':'Peringatan','message':"Sudah ada Account yang active tidak boleh ada 2 account yang Active....!!!"}}
                
            
        
        

        

    
    
    