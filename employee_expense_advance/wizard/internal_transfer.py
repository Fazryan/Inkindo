# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

class HrExpenseInternalTransferWizard(models.TransientModel):
    _name = "hr.expense.internal.transfer.wizard"
    _description = "Hr Expense Internal Transfer wizard"


    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    destination_journal_id = fields.Many2one('account.journal', string='Transfer To', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_type = fields.Selection([('transfer', 'Internal Transfer')],
                                    default='transfer', string='Payment Type', required=True, readonly=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))
        
    @api.one
    @api.depends('payment_type', 'journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

   

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'payment_type':self.payment_type,
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_journal_id': self.destination_journal_id.id,
            'company_id': self.company_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication
        }

    @api.multi
    def internal_post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        advance_expense = self.env['employee.advance.expense'].browse(active_ids)
        # Create payment and post it
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        advance_expense.payment_id = payment.id
        advance_expense.state = 'paid'
        advance_expense.account_by_id = advance_expense.env.user.id
        advance_expense.account_validate_date = time.strftime('%Y-%m-%d')
        

        return {'type': 'ir.actions.act_window_close'}
