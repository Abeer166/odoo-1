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
from odoo import api, fields, tools, models, _, Command
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
from collections import defaultdict
from itertools import groupby
from dateutil.relativedelta import relativedelta
import json
from odoo.tools.misc import formatLang

from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date
from odoo.tools import frozendict

import re
from psycopg2 import sql



class AccruedExpenseRevenue(models.TransientModel):
    _inherit = 'account.accrued.orders.wizard'

    branch_id = fields.Many2one("res.branch", string='Branch', )
    is_branch = fields.Boolean(related='company_id.is_branch')

 
    def _compute_move_vals(self):
        def _get_aml_vals(order, balance, amount_currency, account_id, label=""):
            if not is_purchase:
                balance *= -1
                amount_currency *= -1
            values = {
                'name': label,
                'debit': balance if balance > 0 else 0.0,
                'credit': balance * -1 if balance < 0 else 0.0,
                'account_id': account_id,
                'branch_id': order.branch_id[0].id,
            }
            if len(order) == 1 and self.company_id.currency_id != order.currency_id:
                values.update({
                    'amount_currency': amount_currency,
                    'currency_id': order.currency_id.id,
                        'branch_id': order.branch_id[0].id,
                })
            return values

        def _ellipsis(string, size):
            if len(string) > size:
                return string[0:size - 3] + '...'
            return string

        self.ensure_one()
        move_lines = []
        is_purchase = self.env.context.get('active_model') == 'purchase.order'
        orders = self.env[self._context['active_model']].with_company(self.company_id).browse(self._context['active_ids'])

        if orders.filtered(lambda o: o.company_id != self.company_id):
            raise UserError(_('Entries can only be created for a single company at a time.'))

        orders_with_entries = []
        fnames = []
        total_balance = 0.0
        for order in orders:
            if len(orders) == 1 and self.amount:
                total_balance = self.amount
                order_line = order.order_line[0]
                if is_purchase:
                    account = order_line.product_id.property_account_expense_id or order_line.product_id.categ_id.property_account_expense_categ_id
                else:
                    account = order_line.product_id.property_account_income_id or order_line.product_id.categ_id.property_account_income_categ_id
                values = _get_aml_vals(order, self.amount, 0, account.id, label=_('Manual entry'))
                move_lines.append(Command.create(values))
            else:
                other_currency = self.company_id.currency_id != order.currency_id
                rate = order.currency_id._get_rates(self.company_id, self.date).get(order.currency_id.id) if other_currency else 1.0
                # create a virtual order that will allow to recompute the qty delivered/received (and dependancies)
                # without actually writing anything on the real record (field is computed and stored)
                o = order.new(origin=order)
                if is_purchase:
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_qty_received()
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_qty_invoiced()
                else:
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_qty_delivered()
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_qty_invoiced()
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_untaxed_amount_invoiced()
                    o.order_line.with_context(accrual_entry_date=self.date)._compute_qty_to_invoice()
                lines = o.order_line.filtered(
                    lambda l: l.display_type not in ['line_section', 'line_note'] and
                    fields.Float.compare(
                        l.qty_to_invoice,
                        0,
                        precision_rounding=l.product_uom.rounding,
                    ) == 1
                )
                for order_line in lines:
                    if is_purchase:
                        account = order_line.product_id.property_account_expense_id or order_line.product_id.categ_id.property_account_expense_categ_id
                        amount = self.company_id.currency_id.round(order_line.qty_to_invoice * order_line.price_unit / rate)
                        amount_currency = order_line.currency_id.round(order_line.qty_to_invoice * order_line.price_unit)
                        fnames = ['qty_to_invoice', 'qty_received', 'qty_invoiced', 'invoice_lines']
                        label = _('%s - %s; %s Billed, %s Received at %s each', order.name, _ellipsis(order_line.name, 20), order_line.qty_invoiced, order_line.qty_received, formatLang(self.env, order_line.price_unit, currency_obj=order.currency_id))
                    else:
                        account = order_line.product_id.property_account_income_id or order_line.product_id.categ_id.property_account_income_categ_id
                        amount = self.company_id.currency_id.round(order_line.untaxed_amount_to_invoice / rate)
                        amount_currency = order_line.untaxed_amount_to_invoice
                        fnames = ['qty_to_invoice', 'untaxed_amount_to_invoice', 'qty_invoiced', 'qty_delivered', 'invoice_lines']
                        label = _('%s - %s; %s Invoiced, %s Delivered at %s each', order.name, _ellipsis(order_line.name, 20), order_line.qty_invoiced, order_line.qty_delivered, formatLang(self.env, order_line.price_unit, currency_obj=order.currency_id))
                    values = _get_aml_vals(order, amount, amount_currency, account.id, label=label)
                    move_lines.append(Command.create(values))
                    total_balance += amount
                # must invalidate cache or o can mess when _create_invoices().action_post() of original order after this
                order.order_line.invalidate_model(fnames)

        if not self.company_id.currency_id.is_zero(total_balance):
            # globalized counterpart for the whole orders selection
            values = _get_aml_vals(orders, -total_balance, 0.0, self.account_id.id, label=_('Accrued total'))
            move_lines.append(Command.create(values))

        move_type = _('Expense') if is_purchase else _('Revenue')
        move_vals = {
            'ref': _('Accrued %s entry as of %s', move_type, format_date(self.env, self.date)),
            'journal_id': self.journal_id.id,
            'date': self.date,
            'line_ids': move_lines,
        }
        return move_vals, orders_with_entries
   
    def create_entries(self):
        self.ensure_one()

        if self.reversal_date <= self.date:
            raise UserError(_('Reversal date must be posterior to date.'))

        move_vals, orders_with_entries = self._compute_move_vals()
        move = self.env['account.move'].create(move_vals)
        if self.branch_id:
            move.write({
                'branch_id': self.branch_id.id,
                'accrued_order': True,
            })
        move._post()
        reverse_move = move._reverse_moves(default_values_list=[{
            'ref': _('Reversal of: %s', move.ref),
            'date': self.reversal_date,
            'accrued_order': True,
        }])
        reverse_move._post()
        for order in orders_with_entries:
            body = _('Accrual entry created on %s: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>.\
                    And its <a href=# data-oe-model=account.move data-oe-id=%d>reverse entry</a>.') % (
                self.date,
                move.id,
                move.name,
                reverse_move.id,
            )
            order.message_post(body=body)
        return {
            'name': _('Accrual Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', (move.id, reverse_move.id))],
        }

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        if self.env.company.is_branch and not self.branch_id and not self.accrued_order:
            default_branch = self.env.user.branch_id
            reversed_entry_defaults = self.reversal_move_id
            if reversed_entry_defaults:
                reversed_branch = reversed_entry_defaults[0]
                res['branch_id'] = reversed_branch.branch_id.id
            if self._context.get('default_branch_id'):
                 res['branch_id'] = self._context.get('default_branch_id')
            if self._context.get('branch_id'):
                 res['branch_id'] = self._context.get('branch_id')
            if not self._context.get('default_branch_id') or not self._context.get('branch_id'):
                if default_branch:
                     res['branch_id'] = default_branch.id
                if not default_branch:
                    branches = self.env['res.branch'].search([('user_ids', '=', self.env.user.id),('company_id', '=', self.env.company.id)])
                    if branches:
                         res['branch_id'] = branches[0].id
        return res

    name = fields.Char(string='Number', required=True, readonly=False, copy=False, default='/')
    accrued_order = fields.Boolean("From Accured Order?")
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        compute='_compute_journal_id', store=True, readonly=False, precompute=True,
        required=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[('id', 'in', suitable_journal_ids),'|',('branch_ids', '=', branch_id),('branch_ids', '=', False)]",
    )

    @api.depends('move_type')
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = record._search_default_journal()
            if not record.company_id or record.company_id != record.journal_id.company_id:
                self.env.add_to_compute(self._fields['company_id'], record)
            if not record.currency_id or record.journal_id.currency_id and record.currency_id != record.journal_id.currency_id:
                self.env.add_to_compute(self._fields['currency_id'], record)
            if record.env.company.is_branch:
                if not record.branch_id or record.branch_id != record.journal_id.branch_ids:
                    self.env.add_to_compute(self._fields['branch_id'], record)

    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delivery Address',
        compute='_compute_partner_shipping_id', store=True, readonly=False, precompute=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),'|',('branch_ids', '=', branch_id),('branch_ids', '=', False)]",
        help="Delivery address for current invoice.",
    )
    branch_id = fields.Many2one("res.branch", string='Branch', tracking=True, store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    branch_readonly = fields.Boolean(string="Is A Branch readonly")
    between_branches = fields.Boolean(default=False)
    
    @api.model
    def _compute_is_branch(self):
        return self.env.company.is_branch

    is_branch = fields.Boolean(default=_compute_is_branch,store=True)

    @api.onchange('branch_id')
    def onchange_line_branch_id(self):
        for move in self:
            if move.branch_id:
                if move.line_ids:
                    for line in move.line_ids:
                        if not line.account_id or line.display_type in ('line_section', 'line_note'):
                            continue
                        if line.account_id or line.display_type not in ('line_section', 'line_note'):
                            if move.between_branches:
                                if not line.branch_id:
                                    line.update({'branch_id': move.branch_id.id})
                            if not move.between_branches:
                                if not line.branch_id or line.branch_id != move.branch_id:
                                    line.update({'branch_id': move.branch_id.id})
                if move.invoice_line_ids:
                    for line in move.invoice_line_ids:
                        if not line.product_id or line.display_type in ('line_section', 'line_note'):
                            continue
                        if line.product_id or line.display_type not in ('line_section', 'line_note'):
                            if not line.branch_id or line.branch_id != move.branch_id:
                                line.update({'branch_id': move.branch_id.id})
   
   
    def _post(self, soft=False):
        for move in self:
            if move.env.company.is_branch and not move.accrued_order:
                if not move.branch_id and move.statement_line_id:
                    move.branch_id = move.statement_line_id.branch_id.id
                if move.branch_id:
                    self.onchange_line_branch_id()
                    if move.branch_id.use_custom_sequence:
                        if move.move_type == 'out_invoice':
                            if move.branch_id.inv_custom_sequence and move.branch_id.inv_sequence_id:
                                move.name = move.branch_id.inv_sequence_id._next() or "/"
                            if move.branch_id.inv_custom_sequence and not move.branch_id.inv_sequence_id:
                                if move.company_id.gen_inv_sequence_id:
                                    move.name =  move.company_id.gen_inv_sequence_id._next() or "/"
                            if not move.branch_id.inv_custom_sequence:
                                if move.company_id.gen_inv_sequence_id:
                                    move.name =  move.company_id.gen_inv_sequence_id._next() or "/"

                        if move.move_type == 'out_refund':
                            if move.branch_id.credit_custom_sequence and move.branch_id.credit_sequence_id:
                                move.name = move.branch_id.credit_sequence_id._next() or "/"
                            if move.branch_id.credit_custom_sequence and not move.branch_id.credit_sequence_id:
                                if move.company_id.gen_credit_sequence_id:
                                    move.name =  move.company_id.gen_credit_sequence_id._next() or "/"
                            if not move.branch_id.credit_custom_sequence:
                                if move.company_id.gen_credit_sequence_id:
                                    move.name =  move.company_id.gen_credit_sequence_id._next() or "/"
                        if move.move_type == 'out_receipt':
                            if move.branch_id.out_receipt_custom_sequence and move.branch_id.out_receipt_sequence_id:
                                move.name = move.branch_id.out_receipt_sequence_id._next() or "/"
                            if move.branch_id.out_receipt_custom_sequence and not move.branch_id.out_receipt_sequence_id:
                                if move.company_id.gen_out_receipt_sequence_id:
                                    move.name =  move.company_id.gen_out_receipt_sequence_id._next() or "/"
                            if not move.branch_id.out_receipt_custom_sequence:
                                if move.company_id.gen_out_receipt_sequence_id:
                                    move.name =  move.company_id.gen_out_receipt_sequence_id._next() or "/"

                        if move.move_type == 'in_invoice':
                            if move.branch_id.bill_custom_sequence and move.branch_id.bill_sequence_id:
                                move.name = move.branch_id.bill_sequence_id._next() or "/"
                            if move.branch_id.bill_custom_sequence and not move.branch_id.bill_sequence_id:
                                if move.company_id.gen_bill_sequence_id:
                                    move.name =  move.company_id.gen_bill_sequence_id._next() or "/"
                            if not move.branch_id.bill_custom_sequence:
                                if move.company_id.gen_bill_sequence_id:
                                    move.name =  move.company_id.gen_bill_sequence_id._next() or "/"


                        if move.move_type == 'in_refund':
                            if move.branch_id.refund_custom_sequence and move.branch_id.refund_sequence_id:
                                move.name = move.branch_id.refund_sequence_id._next() or "/"
                            if move.branch_id.refund_custom_sequence and not move.branch_id.refund_sequence_id:
                                if move.company_id.gen_refund_sequence_id:
                                    move.name =  move.company_id.gen_refund_sequence_id._next() or "/"
                            if not move.branch_id.refund_custom_sequence:
                                if move.company_id.gen_refund_sequence_id:
                                    move.name =  move.company_id.gen_refund_sequence_id._next() or "/"

                        if move.move_type == 'in_receipt':
                            if move.branch_id.in_receipt_custom_sequence and move.branch_id.in_receipt_sequence_id:
                                move.name = move.branch_id.in_receipt_sequence_id._next() or "/"
                            if move.branch_id.in_receipt_custom_sequence and not move.branch_id.in_receipt_sequence_id:
                                if move.company_id.gen_in_receipt_sequence_id:
                                    move.name =  move.company_id.gen_in_receipt_sequence_id._next() or "/"
                            if not move.branch_id.in_receipt_custom_sequence:
                                if move.company_id.gen_in_receipt_sequence_id:
                                    move.name =  move.company_id.gen_in_receipt_sequence_id._next() or "/"
                    if not move.branch_id.use_custom_sequence:
                        if move.move_type == 'out_invoice':
                            if move.company_id.gen_inv_sequence_id:
                                move.name =  move.company_id.gen_inv_sequence_id._next() or "/"

                        if move.move_type == 'out_refund':
                            if move.company_id.gen_credit_sequence_id:
                                move.name =  move.company_id.gen_credit_sequence_id._next() or "/"
                        if move.move_type == 'out_receipt':
                            if move.company_id.gen_out_receipt_sequence_id:
                                move.name =  move.company_id.gen_out_receipt_sequence_id._next() or "/"

                        if move.move_type == 'in_invoice':
                            if move.company_id.gen_bill_sequence_id:
                                move.name =  move.company_id.gen_bill_sequence_id._next() or "/"


                        if move.move_type == 'in_refund':
                            if move.company_id.gen_refund_sequence_id:
                                move.name =  move.company_id.gen_refund_sequence_id._next() or "/"

                        if move.move_type == 'in_receipt':
                            if move.company_id.gen_in_receipt_sequence_id:
                                move.name =  move.company_id.gen_in_receipt_sequence_id._next() or "/"
        res = super(AccountMove, self)._post(soft=False)
        return res

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        for move in self:
            if move.is_branch and not move.branch_id:
                move.update({
                    'partner_id': False,
                })
                return
            if move.branch_id:
                partner = move.env['res.partner'].search([('type', '!=', 'private'), ('company_id', 'in', (False, move.company_id.id)),'|',('branch_ids', '=', self.branch_id.id),('branch_ids', '=', False)])
                move.update({
                    'partner_id': False,
                    'journal_id': False,
                })
                if partner:
                    move.partner_id = partner[0].id
                if move.invoice_filter_type_domain == 'sale':
                    journal = self.env['account.journal'].search([('type', '=', 'sale'),('branch_ids', 'in', (False, move.branch_id.id))])
                    if journal:                
                        move.update({
                        'journal_id': journal[0].id,
                        })
                elif move.invoice_filter_type_domain == 'purchase':
                    journal = move.env['account.journal'].search([('type', '=', 'purchase'),('branch_ids', 'in', (False, move.branch_id.id))])
                    if journal:              
                        move.update({
                        'journal_id': journal[0].id,
                        })
                elif move.move_type == 'entry':
                    journal = move.env['account.journal'].search([('type', '=', 'general'),('branch_ids', 'in', (False, move.branch_id.id))])
                    if journal:              
                        move.update({
                        'journal_id': journal[0].id,
                        })

    @api.onchange('company_id')
    def _onchange_company_id(self):
        company = self.env.company
        if not company.is_branch:
            return
        if company.is_branch:
            if not self._context.get('branch_id') and not self._context.get('branch_id2'):
                if self.env.user.branch_id:
                    self.branch_id = self.env.user.branch_id.id
                if not self.env.user.branch_id:
                    branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
                    if len(branches) > 0:
                        self.branch_id = branches[0]
                    else:
                        self.branch_id = False
                    return {'domain': {'branch_id': [('id', 'in', branches)]}}
                else:
                    return {'domain': {'branch_id': []}}

 
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

            
    branch_id = fields.Many2one("res.branch", string='Branch',store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
    is_branch = fields.Boolean(related='move_id.is_branch')
    branch_readonly = fields.Boolean(related='move_id.branch_readonly')
    
    @api.onchange('account_id')
    def onchange_account_branch_id(self):
        for line in self:
            if not line.account_id or line.display_type in ('line_section', 'line_note'):
                continue
            if self.move_id.branch_id:
                self.branch_id = self.move_id.branch_id.id

    @api.onchange('product_id')
    def onchange_product_branch_id(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            if self.move_id.branch_id:
                self.branch_id = self.move_id.branch_id.id

class AutomaticEntryWizard(models.TransientModel):
    _inherit = 'account.automatic.entry.wizard'
    _description = 'Create Automatic Entries with branch'

    is_branch = fields.Boolean(related='company_id.is_branch')

    def _get_move_dict_vals_change_period(self):
        # set the change_period account on the selected journal items
        accrual_account = self.revenue_accrual_account if self.account_type == 'income' else self.expense_accrual_account
        branch = self.move_line_ids.mapped('branch_id')
        move_data = {'new_date': {
            'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
            'move_type': 'entry',
            'branch_id': branch.id,
            'line_ids': [],
            'ref': _('Adjusting Entry'),
            'date': fields.Date.to_string(self.date),
            'journal_id': self.journal_id.id,
        }}
        # complete the account.move data
        for date, grouped_lines in groupby(self.move_line_ids, lambda m: m.move_id.date):
            grouped_lines = list(grouped_lines)
            branch = self.move_line_ids.mapped('branch_id')
            amount = sum(l.balance for l in grouped_lines)
            move_data[date] = {
                'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
                'move_type': 'entry',
                'branch_id': branch.id,
                'line_ids': [],
                'ref': self._format_strings(_('Adjusting Entry of {date} ({percent:f}% recognized on {new_date})'), grouped_lines[0].move_id, amount),
                'date': fields.Date.to_string(date),
                'journal_id': self.journal_id.id,
            }

        # compute the account.move.lines and the total amount per move
        for aml in self.move_line_ids:
            # account.move.line data
            reported_debit = aml.company_id.currency_id.round((self.percentage / 100) * aml.debit)
            reported_credit = aml.company_id.currency_id.round((self.percentage / 100) * aml.credit)
            reported_amount_currency = aml.currency_id.round((self.percentage / 100) * aml.amount_currency)

            move_data['new_date']['line_ids'] += [
                (0, 0, {
                    'name': aml.name or '',
                    'debit': reported_debit,
                    'credit': reported_credit,
                    'amount_currency': reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': aml.account_id.id,
                    'partner_id': aml.partner_id.id,
                    'branch_id': aml.branch_id.id,
                }),
                (0, 0, {
                    'name': _('Adjusting Entry'),
                    'debit': reported_credit,
                    'credit': reported_debit,
                    'amount_currency': -reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': accrual_account.id,
                    'partner_id': aml.partner_id.id,
                    'branch_id': aml.branch_id.id,
                }),
            ]
            move_data[aml.move_id.date]['line_ids'] += [
                (0, 0, {
                    'name': aml.name or '',
                    'debit': reported_credit,
                    'credit': reported_debit,
                    'amount_currency': -reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': aml.account_id.id,
                    'partner_id': aml.partner_id.id,
                    'branch_id': aml.branch_id.id,
                }),
                (0, 0, {
                    'name': _('Adjusting Entry'),
                    'debit': reported_debit,
                    'credit': reported_credit,
                    'amount_currency': reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': accrual_account.id,
                    'partner_id': aml.partner_id.id,
                    'branch_id': aml.branch_id.id,
                }),
            ]

        move_vals = [m for m in move_data.values()]
        return move_vals



class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    branch_ids = fields.Many2many(
        comodel_name="res.branch",
        string="Share To Branches",
        relation="analytic_account_branch_rel", domain="[('user_ids', '=', uid)]",column1="analytic_account_id",column2="branch_id", tracking=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    

    

class AccountMoveReport(models.Model):
    _inherit = 'account.invoice.report'


    branch_id = fields.Many2one('res.branch',string="Branch",readonly=True )
    is_branch = fields.Boolean()
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',readonly=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',readonly=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',readonly=True)

   
  
    def _select(self):
        return super(AccountMoveReport, self)._select() + ", line.branch_id as branch_id, line.branch_group_id as branch_group_id, line.branch_type_id as branch_type_id, line.branch_state_id as branch_state_id"


class AccountAccount(models.Model):
    _inherit = 'account.account'


    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)


    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for account in self:
            account.branches_count = branches_count


    branch_ids = fields.Many2many(comodel_name="res.branch", relation="account_branch_rel", column1="account_id", column2="branch_id",string='Share To Branches', tracking=True)
    is_branch = fields.Boolean(related='company_id.is_branch')

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    branch_ids = fields.Many2many(string='Share To Branches', comodel_name="res.branch", relation="journal_branch_rel", column1="journal_id", column2="branch_id", tracking=True)

    is_branch = fields.Boolean(related='company_id.is_branch')

    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)
    
    # def _get_last_bank_statement(self, domain=None):
    #     ''' Retrieve the last bank statement created using this journal.
    #     :param domain:  An additional domain to be applied on the account.bank.statement model.
    #     :return:        An account.bank.statement record or an empty recordset.
    #     '''
    #     self.ensure_one()
    #     last_statement_domain = (domain or []) + [('journal_id', '=', self.id,'branch_id', 'in', self.branch_id.ids)]
    #     last_st_line = self.env['account.bank.statement.line'].search(last_statement_domain, order='date desc, id desc', limit=1)
    #     return last_st_line.statement_id
  

        
    @api.onchange('branch_ids')
    def _check_count_for_cash_bank(self):
        for journal in self:
            if journal.type in ('bank', 'cash'):
                branches = journal.branch_ids
                if len(branches) > 1:
                    raise UserError(_("cash and bank journales allwed to one branch only!"))

    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for account in self:
            account.branches_count = branches_coun


class SetupBarBankConfigWizard(models.TransientModel):
    _inherit = 'account.setup.bank.manual.config'


    branch_ids = fields.Many2many(string='Share To Branches', comodel_name="res.branch")



    @api.depends('journal_id')  # Despite its name, journal_id is actually a One2many field
    def _compute_linked_journal_id(self):
        for record in self:
            record.linked_journal_id = record.journal_id and record.journal_id[0] or record.default_linked_journal_id()
            record.branch_ids = record.journal_id.branch_ids and record.journal_id[0].branch_ids

            
    @api.onchange('linked_journal_id')
    def _onchange_new_journal_related_data(self):
        for record in self:
            if record.linked_journal_id:
                record.new_journal_name = record.linked_journal_id.name
                record.branch_ids = record.linked_journal_id.branch_ids
