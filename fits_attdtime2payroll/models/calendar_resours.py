from openerp import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Attendence(models.Model):
    _inherit = 'resource.calendar.attendance'
    
    hours_from_float = fields.Float('Hours From Float',compute='_compute_jam')
    hours_to_float = fields.Float('Hours To Float Jam',compute='_compute_jam')
    
    @api.one
    @api.depends('hour_from','hour_to')
    def _compute_jam(self) :
        minutes_from = self.hour_from * 60
        hours_from, minutes_from = divmod(minutes_from, 60)
        jam_from_float = "%02d.%02d"%(hours_from, minutes_from) 
        self.hours_from_float = float(jam_from_float)
        minutes_to = self.hour_to * 60
        hours_to, minutes_to= divmod(minutes_to, 60)
        jam_to_float = "%02d.%02d"%(hours_to, minutes_to)
        self.hours_to_float = float(jam_to_float)  
