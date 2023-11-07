# -*- coding: utf-8 -*-
#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time

from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang, format_date

from collections import defaultdict

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

import logging

_logger = logging.getLogger(__name__)


from odoo.addons.account.models.account_payment import AccountPayment as payment

class AccountPayment(models.Model):
    _inherit = 'account.payment'


    @api.model
    def default_get(self, fields):
        res = super(AccountPayment, self).default_get(fields)
        if self.env.company.is_branch:
            invoice_defaults = self.reconciled_invoice_ids
            default_branch = self.env.user.branch_id
            if invoice_defaults and len(invoice_defaults) == 1:
                invoice = invoice_defaults[0]
                res['branch_id'] = invoice.branch_id.id,
                res['branch_group_id'] = invoice.branch_id.group_id.id,
                res['branch_type_id'] = invoice.branch_id.type_id.id,
                res['branch_state_id'] = invoice.branch_id.state_id.id,
            if not invoice_defaults:
                branch_id = False
                if self._context.get('default_branch_id'):
                    branch_id = self._context.get('default_branch_id')
                res.update({'branch_id' : branch_id})
                self._onchange_branch_id()
                if self._context.get('branch_id'):
                    branch_id = self._context.get('branch_id')
                res.update({'branch_id' : branch_id})
                self._onchange_branch_id()
                if not self._context.get('default_branch_id') or not self._context.get('branch_id'):
                    if default_branch:
                        branch_id = default_branch.id
                    if not default_branch:
                        branches = self.env['res.branch'].search([('user_ids', '=', self.env.user.id),('company_id', '=', self.env.company.id)])
                        if branches:
                            branch_id = branches[0].id
                res.update({'branch_id' : branch_id})
                self._onchange_branch_id()
        return res


    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
    branch_id = fields.Many2one("res.branch", string='Branch', tracking=True, store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')


    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        store=True, readonly=False, ondelete='restrict',
        compute='_compute_partner_id',
        domain="[('branch_ids', 'in', (False, branch_id)),'|', ('parent_id','=', False), ('is_company','=', True)]",
        tracking=True,
        check_company=True)


    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if not self.branch_id:
            self.update({
                'journal_id': False,
                'partner_id': False,
            })
            return
        if self.branch_id:
            journal = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),'|',('branch_ids','=',self.branch_id.id),('branch_ids', '=', False)])
            partner = self.env['res.partner'].search([('company_id', 'in', (False, self.company_id.id)),('branch_ids', 'in', (False, self.branch_id.id))])
            self.journal_id = False
            self.partner_id = False
            if journal:
                self.journal_id = journal[0]
            return {'domain': {'journal_id': [('id', 'in', journal.ids)]}}
            if partner:
                self.partner_id = partner[0].id

    def _get_valid_liquidity_accounts(self):
        result = super()._get_valid_liquidity_accounts()
        return result + (self.branch_id,self.branch_id.group_id,self.branch_id.type_id,self.branch_id.state_id)


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'branch_id': self.branch_id.id,
                'branch_group_id': self.branch_id.group_id.id,
                'branch_type_id': self.branch_id.type_id.id,
                'branch_state_id': self.branch_id.state_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'branch_id': self.branch_id.id,
                'branch_group_id': self.branch_id.group_id.id,
                'branch_type_id': self.branch_id.type_id.id,
                'branch_state_id': self.branch_id.state_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        return line_vals_list + write_off_line_vals_list


class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register mass Payment with branches'

    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_id = fields.Many2one('res.branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        compute='_compute_journal_id', store=True, readonly=False, precompute=True,
        domain="[('id', 'in', available_journal_ids),'|',('branch_ids','=',branch_id),('branch_ids','=',False)]")

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        for payment in self:
            if payment.branch_id:
                journal = self.env['account.journal'].search([('id', 'in', self.available_journal_ids.ids),'|',('branch_ids','=',self.branch_id.id),('branch_ids','=',False)])
                payment.journal_id = False
                if payment.branch_id and journal:
                    payment.journal_id = journal[0]
                return {'domain': {'journal_id': [('id', 'in', journal.ids)]}}

    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),'|',('branch_ids','=',wizard.branch_id.id),('branch_ids','=',False),
                    ('id', 'in', self.available_journal_ids.ids)
                ], limit=1)

    # def _create_payment_vals_from_wizard(self, batch_result):
    #     vals = super()._create_payment_vals_from_wizard(batch_result)
    #     vals.update({'branch_id': self.line_ids.move_id[0].branch_id.id})
    #     return vals

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(payment_register, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({'branch_id': batch_result['lines'][0].branch_id.id,'branch_group_id': batch_result['lines'][0].branch_id.group_id.id,'branch_type_id': batch_result['lines'][0].branch_id.type_id.id,'branch_state_id': batch_result['lines'][0].branch_id.state_id.id})
        return payment_vals


    def _create_payment_vals_from_batch(self, batch_result):
        payment_vals = super(payment_register, self)._create_payment_vals_from_batch(batch_result)
        payment_vals.update({'branch_id': batch_result['lines'][0].branch_id.id,'branch_group_id': batch_result['lines'][0].branch_id.group_id.id,'branch_type_id': batch_result['lines'][0].branch_id.type_id.id,'branch_state_id': batch_result['lines'][0].branch_id.state_id.id})
        return payment_vals

    @api.model
    def _get_batch_journal(self, batch_result):
        """ Helper to compute the journal based on the batch.

        :param batch_result:    A batch returned by '_get_batches'.
        :return:                An account.journal record.
        """
        payment_values = batch_result['payment_values']
        foreign_currency_id = payment_values['currency_id']
        partner_bank_id = payment_values['partner_bank_id']

        currency_domain = [('currency_id', '=', foreign_currency_id)]
        partner_bank_domain = [('bank_account_id', '=', partner_bank_id)]

        default_domain = [
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', batch_result['lines'].company_id.id),'|',('branch_ids', '=', batch_result['lines'].branch_id.id),
            ('id', 'in', self.available_journal_ids.ids)
        ]

        if partner_bank_id:
            extra_domains = (
                currency_domain + partner_bank_domain,
                partner_bank_domain,
                currency_domain,
                [],
            )
        else:
            extra_domains = (
                currency_domain,
                [],
            )

        for extra_domain in extra_domains:
            journal = self.env['account.journal'].search(default_domain + extra_domain, limit=1)
            if journal:
                return journal

        return self.env['account.journal']

    @api.model
    def _get_line_batch_key(self, line):
        values = super(payment_register, self)._get_line_batch_key(line)
        values.update({'branch_id': line.branch_id.id})
        return values
 
    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        payment_vals = super(payment_register, self)._get_wizard_values_from_batch(batch_result)
        lines = batch_result['lines']
        branch = lines[0].branch_id
        branch_group_id = lines[0].branch_id.group_id
        branch_type_id = lines[0].branch_id.type_id
        branch_state_id = lines[0].branch_id.state_id
        payment_vals.update({'branch_id': batch_result['lines'][0].branch_id.id,'branch_group_id': batch_result['lines'][0].branch_id.group_id.id,'branch_type_id': batch_result['lines'][0].branch_id.type_id.id,'branch_state_id': batch_result['lines'][0].branch_id.state_id.id})
        return payment_vals


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def default_get(self, fields):
        res = super(AccountBankStatement, self).default_get(fields)
        if self.env.company.is_branch:
            default_branch = self.env.user.branch_id
            branch_id = False
            if self._context.get('default_branch_id'):
                branch_id = self._context.get('default_branch_id')
            res.update({'branch_id' : branch_id})
            if self._context.get('branch_id'):
                branch_id = self._context.get('branch_id')
            res.update({'branch_id' : branch_id})
            if not self._context.get('default_branch_id') or not self._context.get('branch_id'):
                if default_branch:
                    branch_id = default_branch.id
                if not default_branch:
                    branches = self.env['res.branch'].search([('user_ids', '=', self.env.user.id),('company_id', '=', self.env.company.id)])
                    if branches:
                        branch_id = branches[0].id
            res.update({'branch_id' : branch_id})
        return res


    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_id = fields.Many2one('res.branch',string="Branch", store=True)   
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )



    def _check_balance_end_real_same_as_computed(self):
        ''' Check the balance_end_real (encoded manually by the user) is equals to the balance_end (computed by odoo).
        In case of a cash statement, the different is set automatically to a profit/loss account.
        '''
        for stmt in self:
            if not stmt.currency_id.is_zero(stmt.difference):
                if stmt.journal_type == 'cash':
                    st_line_vals = {
                        'statement_id': stmt.id,
                        'journal_id': stmt.journal_id.id,
                        'branch_id': stmt.branch_id.id,
                        'branch_group_id': stmt.branch_id.group_id.id,
                        'branch_type_id': stmt.branch_id.type_id.id,
                        'branch_state_id': stmt.branch_id.state_id.id,
                        'amount': stmt.difference,
                        'date': stmt.date,
                    }

                    if stmt.difference < 0.0:
                        if not stmt.journal_id.loss_account_id:
                            raise UserError(_('Please go on the %s journal and define a Loss Account. This account will be used to record cash difference.', stmt.journal_id.name))

                        st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Loss)")
                        st_line_vals['counterpart_account_id'] = stmt.journal_id.loss_account_id.id
                    else:
                        # statement.difference > 0.0
                        if not stmt.journal_id.profit_account_id:
                            raise UserError(_('Please go on the %s journal and define a Profit Account. This account will be used to record cash difference.', stmt.journal_id.name))

                        st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Profit)")
                        st_line_vals['counterpart_account_id'] = stmt.journal_id.profit_account_id.id

                    self.env['account.bank.statement.line'].create(st_line_vals)
                else:
                    balance_end_real = formatLang(self.env, stmt.balance_end_real, currency_obj=stmt.currency_id)
                    balance_end = formatLang(self.env, stmt.balance_end, currency_obj=stmt.currency_id)
                    raise UserError(_(
                        'The ending balance is incorrect !\nThe expected balance (%(real_balance)s) is different from the computed one (%(computed_balance)s).',
                        real_balance=balance_end_real,
                        computed_balance=balance_end
                    ))
        return True

class account_bank_statement_line(models.Model):

    _inherit = 'account.bank.statement.line'


    branch_id = fields.Many2one('res.branch',related='statement_id.branch_id', string='Branch',readonly=False, store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


    @api.model
    def _prepare_liquidity_move_line_vals(self):
         # cash differance
        self.ensure_one()

        statement = self.statement_id
        journal = statement.journal_id
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id or company_currency

        if self.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            if self.foreign_currency_id == company_currency:
                amount_currency = self.amount
                balance = self.amount_currency
            else:
                amount_currency = self.amount
                balance = journal_currency._convert(amount_currency, company_currency, journal.company_id, self.date)
        elif self.foreign_currency_id and not journal_currency:
            amount_currency = self.amount_currency
            balance = self.amount
            currency_id = self.foreign_currency_id.id
        elif not self.foreign_currency_id and journal_currency:
            currency_id = journal_currency.id
            amount_currency = self.amount
            balance = journal_currency._convert(amount_currency, journal.company_id.currency_id, journal.company_id, self.date)
        else:
            currency_id = company_currency.id
            amount_currency = self.amount
            balance = self.amount

        return {
            'name': self.payment_ref,
            'move_id': self.move_id.id,
            'partner_id': self.partner_id.id,
            'branch_id': statement.branch_id.id,
            'branch_group_id': statement.branch_id.group_id.id,
            'branch_type_id': statement.branch_id.type_id.id,
            'branch_state_id': statement.branch_id.state_id.id,
            'currency_id': currency_id,
            'account_id': journal.default_account_id.id,
            'debit': balance > 0 and balance or 0.0,
            'credit': balance < 0 and -balance or 0.0,
            'amount_currency': amount_currency,
        }
    @api.model
    def _prepare_counterpart_move_line_vals(self, counterpart_vals, move_line=None):
        self.ensure_one()

        statement = self.statement_id
        journal = statement.journal_id
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id or company_currency
        foreign_currency = self.foreign_currency_id or journal_currency or company_currency
        statement_line_rate = (self.amount_currency / self.amount) if self.amount else 0.0

        balance_to_reconcile = counterpart_vals.pop('balance', None)
        amount_residual = -counterpart_vals.pop('amount_residual', move_line.amount_residual if move_line else 0.0) \
            if balance_to_reconcile is None else balance_to_reconcile
        amount_residual_currency = -counterpart_vals.pop('amount_residual_currency', move_line.amount_residual_currency if move_line else 0.0)\
            if balance_to_reconcile is None else balance_to_reconcile

        if 'currency_id' in counterpart_vals:
            currency_id = counterpart_vals['currency_id'] or company_currency.id
        elif move_line:
            currency_id = move_line.currency_id.id or company_currency.id
        else:
            currency_id = foreign_currency.id

        if currency_id not in (foreign_currency.id, journal_currency.id):
            currency_id = company_currency.id
            amount_residual_currency = 0.0

        amounts = {
            company_currency.id: 0.0,
            journal_currency.id: 0.0,
            foreign_currency.id: 0.0,
        }

        amounts[currency_id] = amount_residual_currency
        amounts[company_currency.id] = amount_residual

        if currency_id == journal_currency.id and journal_currency != company_currency:
            if foreign_currency != company_currency:
                amounts[company_currency.id] = journal_currency._convert(amounts[currency_id], company_currency, journal.company_id, self.date)
            if statement_line_rate:
                amounts[foreign_currency.id] = amounts[currency_id] * statement_line_rate
        elif currency_id == foreign_currency.id and self.foreign_currency_id:
            if statement_line_rate:
                amounts[journal_currency.id] = amounts[foreign_currency.id] / statement_line_rate
                if foreign_currency != company_currency:
                    amounts[company_currency.id] = journal_currency._convert(amounts[journal_currency.id], company_currency, journal.company_id, self.date)
        else:
            amounts[journal_currency.id] = company_currency._convert(amounts[company_currency.id], journal_currency, journal.company_id, self.date)
            if statement_line_rate:
                amounts[foreign_currency.id] = amounts[journal_currency.id] * statement_line_rate

        if foreign_currency == company_currency and journal_currency != company_currency and self.foreign_currency_id:
            balance = amounts[foreign_currency.id]
        else:
            balance = amounts[company_currency.id]

        if foreign_currency != company_currency and self.foreign_currency_id:
            amount_currency = amounts[foreign_currency.id]
            currency_id = foreign_currency.id
        elif journal_currency != company_currency and not self.foreign_currency_id:
            amount_currency = amounts[journal_currency.id]
            currency_id = journal_currency.id
        else:
            amount_currency = amounts[company_currency.id]
            currency_id = company_currency.id

        return {
            **counterpart_vals,
            'name': counterpart_vals.get('name', move_line.name if move_line else ''),
            'move_id': self.move_id.id,
            'partner_id': self.partner_id.id or counterpart_vals.get('partner_id', move_line.partner_id.id if move_line else False),
            'currency_id': currency_id,
            'account_id': counterpart_vals.get('account_id', move_line.account_id.id if move_line else False),
            'branch_id': self.branch_id.id or counterpart_vals.get('branch_id', move_line.branch_id.id if move_line else self.branch_id.id),
            'branch_group_id': self.branch_id.group_id.id or counterpart_vals.get('branch_group_id', move_line.branch_id.group_id.id if move_line else self.branch_id.group_id.id),
            'branch_type_id': self.branch_id.type_id.id or counterpart_vals.get('branch_type_id', move_line.branch_id.type_id.id if move_line else self.branch_id.type_id.id),
            'branch_state_id': self.branch_id.state_id.id or counterpart_vals.get('branch_state_id', move_line.branch_id.state_id.id if move_line else self.branch_id.state_id.id),
            'debit': balance if balance > 0.0 else 0.0,
            'credit': -balance if balance < 0.0 else 0.0,
            'amount_currency': amount_currency,
        }
