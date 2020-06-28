odoo.define('fits_attdtime2payroll.kiosk_confirm', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var Kiosk = require('hr_attendance.kiosk_confirm');


var QWeb = core.qweb;
var _t = core._t;


Kiosk.include({
               events: {
        "click .o_hr_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_hr_attendance_sign_in_out_icon": function () {
            var self = this;
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            var hr_employee = new Model('hr.employee');
             if (this.$('input.o_hr_boolean').prop('checked')) {
					            	hr_employee.call('attendance_manual_site', [[this.employee_id], this.next_action])
						            .then(function(result) {
						                if (result.action) {
						                    self.do_action(result.action);
						                } else if (result.warning) {
						                    self.do_warn(result.warning);
						                    self.$('.o_hr_attendance_sign_in_out_icon').removeAttr("disabled");
						                }
						            });
					        	} else {
					            	hr_employee.call('attendance_manual', [[this.employee_id], this.next_action])
						            .then(function(result) {
						                if (result.action) {
						                    self.do_action(result.action);
						                } else if (result.warning) {
						                    self.do_warn(result.warning);
						                    self.$('.o_hr_attendance_sign_in_out_icon').removeAttr("disabled");
						                }
						            });
					        	}
            
		        },
		        'click .o_hr_attendance_pin_pad_button_0': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 0); },
		        'click .o_hr_attendance_pin_pad_button_1': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 1); },
		        'click .o_hr_attendance_pin_pad_button_2': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 2); },
		        'click .o_hr_attendance_pin_pad_button_3': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 3); },
		        'click .o_hr_attendance_pin_pad_button_4': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 4); },
		        'click .o_hr_attendance_pin_pad_button_5': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 5); },
		        'click .o_hr_attendance_pin_pad_button_6': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 6); },
		        'click .o_hr_attendance_pin_pad_button_7': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 7); },
		        'click .o_hr_attendance_pin_pad_button_8': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 8); },
		        'click .o_hr_attendance_pin_pad_button_9': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 9); },
		        'click .o_hr_attendance_pin_pad_button_C': function() { this.$('.o_hr_attendance_PINbox').val(''); },
		        'click .o_hr_attendance_pin_pad_button_ok': function() {
		            var self = this;
		            this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
		            var hr_employee = new Model('hr.employee');
		            hr_employee.call('attendance_manual', [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val()])
		            .then(function(result) {
		                if (result.action) {
		                    self.do_action(result.action);
		                } else if (result.warning) {
		                    self.do_warn(result.warning);
		                    setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
		                }
		            });
		        },
		    },
							    
         });

         
});