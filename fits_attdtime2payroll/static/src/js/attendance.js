odoo.define('fits_attdtime2payroll.attendance', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var Attendance = require('hr_attendance.my_attendances');


var QWeb = core.qweb;
var _t = core._t;


Attendance.include({
                    events: {
					        "click .o_hr_attendance_sign_in_out_icon": function() {
					         if (this.$('input.o_hr_boolean').prop('checked')) {
					            	this.update_attendance_site();
					        	} else {
					            	this.update_attendance()
					        	}
					        
					            
					        },
					    },
					    
				 update_attendance_site: function () {
				        var self = this;
				        var hr_employee = new Model('hr.employee');
				        hr_employee.call('attendance_manual_site', [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'])
				            .then(function(result) {
				                if (result.action) {
				                    self.do_action(result.action);
				                } else if (result.warning) {
				                    self.do_warn(result.warning);
				                }
			            });
			    },	    
					    
         });

         
});