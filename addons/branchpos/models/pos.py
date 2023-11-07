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

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
from functools import partial
from itertools import groupby

import psycopg2
import pytz
import re

from odoo.tools import float_is_zero, float_round, float_repr, float_compare, formatLang
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)



class PosConfig(models.Model):
    _inherit = 'pos.config'


    def _default_branch_id(self):
        if self.env.user.branch_id:
            self.branch_id = self.env.user.branch_id.id
            self._onchange_branch_id()
        elif not self.env.user.branch_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            if len(branches) > 0:
                self.branch_id = branches[0]
                self._onchange_branch_id()

    def _default_group_type_id(self):
        if self.branch_id:
            self.branch_name = self.branch_id.name
            self.branch_email = self.branch_id.email
            self.branch_phone = self.branch_id.phone
            self.branch_mobile = self.branch_id.mobile


    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id),'|',('branch_id', '=', self.branch_id.id),('branch_id', '=', False)], limit=1).id

    branch_user_id = fields.Many2many(string='Allowed Users', comodel_name="res.users", relation="pos_config_user_rel",column1="config_id" , column2="user_id",)
    branch_id = fields.Many2one('res.branch',string="Branch", readonly=False,default=_default_branch_id,ondelete='restrict',store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
   
    warehouse_id = fields.Many2one('stock.warehouse', default=_default_warehouse_id, ondelete='restrict')
    branch_name = fields.Char(string="POS Branch Name", store=True,default=_default_group_type_id)
    branch_email = fields.Char( string="POS Email",store=True,default=_default_group_type_id)
    branch_phone = fields.Char( string="POS Phone",store=True,default=_default_group_type_id)
    branch_mobile = fields.Char( string="POS Mobile",store=True,default=_default_group_type_id)


    def _default_invoice_journal(self):
        return self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.env.company.id),'|',('branch_ids', '=', self.branch_id.id),('branch_ids', '=', False)], limit=1)

    invoice_journal_id = fields.Many2one('account.journal', string='Invoice Journal',domain=[('type', '=', 'sale')],help="Accounting journal used to create invoices.",default=_default_invoice_journal)

    def setup_invoice_journal(self, company):
        for pos_config in self:
            invoice_journal_id = pos_config.invoice_journal_id or self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', company.id),'|',('branch_ids', '=', pos_config.branch_id.id),('branch_ids', '=', False)], limit=1)
            if invoice_journal_id:
                pos_config.write({'invoice_journal_id': invoice_journal_id.id})

    def assign_payment_journals(self, company):
        for pos_config in self:
            if pos_config.payment_method_ids or pos_config.has_active_session:
                continue
            cash_journal = self.env['account.journal'].search([('company_id', '=', company.id), ('type', '=', 'cash'),'|',('branch_ids', '=', 'branch_id'),('branch_ids', '=', 'False')])
            bank_journal = self.env['account.journal'].search([('company_id', '=', company.id), ('type', '=', 'bank'),'|',('branch_ids', '=', 'branch_id'),('branch_ids', '=', 'False')])
            branch = pos_config.branch_id
            payment_methods = self.env['pos.payment.method']
            if cash_journal:
                payment_methods |= payment_methods.create({
                    'name': _('Cash'),
                    'journal_id': cash_journal.id,
                    'branch_id': branch.id,
                    'company_id': company.id,
                })
            if bank_journal:
                payment_methods |= payment_methods.create({
                    'name': _('Bank'),
                    'journal_id': bank_journal.id,
                    'branch_id': branch.id,
                    'company_id': company.id,
                })
            payment_methods |= payment_methods.create({
                'name': _('Customer Account'),
                'company_id': company.id,
                'split_transactions': True,
            })
            pos_config.write({'payment_method_ids': [(6, 0, payment_methods.ids)]})


    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            picking = self.env['stock.picking.type'].search([('warehouse_id', '=', self.warehouse_id.id),('code', '=', 'outgoing')])
            self.picking_type_id = False
            if self.warehouse_id and picking:
                self.picking_type_id = picking[0].id
            return {'domain': {'picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            return {'domain': {'picking_type_id': []}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        for pos_config in self:
            branch_id = pos_config.branch_id
            if branch_id:
                pos_config.branch_type_id =  pos_config.branch_id.type_id.id
                pos_config.branch_group_id =  pos_config.branch_id.group_id.id
                pos_config.branch_state_id =  pos_config.branch_id.state_id.id
                pos_config.branch_name =  pos_config.branch_id.name
                pos_config.branch_phone =  pos_config.branch_id.phone
                pos_config.branch_email =  pos_config.branch_id.email
                pos_config.branch_mobile =  pos_config.branch_id.mobile
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id),'|',('branch_id', '=', pos_config.branch_id.id),('branch_id', '=', False)])
                journalinv = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id),'|',('branch_ids', '=', pos_config.branch_id.id),('branch_ids', '=', False)])
                payment_methods = self.env['pos.payment.method'].search([('split_transactions', '=', False), ('company_id', '=', self.env.company.id),'|',('branch_ids', '=', pos_config.branch_id.id),('branch_ids', '=', False)])
                journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id),'|',('branch_ids', '=', pos_config.branch_id.id),('branch_ids', '=', False)])
                pos_config.warehouse_id = False
                pos_config.journal_id = False
                pos_config.payment_method_ids = False
                pos_config.invoice_journal_id = False
                if pos_config.branch_id and warehouse:
                    pos_config.warehouse_id = warehouse[0].id
                if pos_config.branch_id and journalinv:
                    pos_config.invoice_journal_id = journalinv[0].id
                if pos_config.branch_id and journal:
                    pos_config.journal_id = journal[0].id
                if pos_config.branch_id and payment_methods:
                    pos_config.payment_method_ids = payment_methods


class PosSession(models.Model):
    _inherit = 'pos.session'


    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_id = fields.Many2one('res.branch',string="Branch",related='config_id.branch_id',store=True ) 
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
   

    branch_name = fields.Char(related='config_id.branch_name')
    branch_email = fields.Char(related='config_id.branch_email')
    branch_phone = fields.Char(related='config_id.branch_phone')
    branch_mobile = fields.Char(related='config_id.branch_mobile')


    def _create_diff_account_move_for_split_payment_method(self, payment_method, diff_amount):
        self.ensure_one()

        get_diff_vals_result = self._get_diff_vals(payment_method.id, diff_amount)
        if not get_diff_vals_result:
            return

        source_vals, dest_vals = get_diff_vals_result
        diff_move = self.env['account.move'].create({
            'journal_id': payment_method.journal_id.id,
            'date': fields.Date.context_today(self),
            'branch_id': self.branch_id.id,
            'ref': self._get_diff_account_move_ref(payment_method),
            'line_ids': [Command.create(source_vals), Command.create(dest_vals)]
        })
        diff_move._post()

    def _prepare_balancing_line_vals(self, imbalance_amount, move, balancing_account):
        partial_vals = {
            'name': _('Difference at closing PoS session'),
            'account_id': balancing_account.id,
            'move_id': move.id,
            'branch_id': self.branch_id.id,
            'partner_id': False,
        }
        imbalance_amount_session = 0
        if (not self.is_in_company_currency):
            imbalance_amount_session = self.company_id.currency_id._convert(imbalance_amount, self.currency_id, self.company_id, fields.Date.context_today(self))
        return self._credit_amounts(partial_vals, imbalance_amount_session, imbalance_amount)

    def _create_account_move(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        account_move = self.env['account.move'].create({
            'journal_id': self.config_id.journal_id.id,
            'branch_id': self.config_id.branch_id.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
        })
        self.write({'move_id': account_move.id})

        data = {'bank_payment_method_diffs': bank_payment_method_diffs or {}}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_bank_payment_moves(data)
        data = self._create_pay_later_receivable_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)
        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        if balancing_account and amount_to_balance:
            data = self._create_balancing_line(data, balancing_account, amount_to_balance)

        return data


    def _create_combine_account_payment(self, payment_method, amounts, diff_amount):
        outstanding_account = payment_method.outstanding_account_id or self.company_id.account_journal_payment_debit_account_id
        destination_account = self._get_receivable_account(payment_method)

        if float_compare(amounts['amount'], 0, precision_rounding=self.currency_id.rounding) < 0:
            # revert the accounts because account.payment doesn't accept negative amount.
            outstanding_account, destination_account = destination_account, outstanding_account

        account_payment = self.env['account.payment'].create({
            'amount': abs(amounts['amount']),
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id':  destination_account.id,
            'ref': _('Combine %s POS payments from %s') % (payment_method.name, self.name),
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
            'branch_id': self.branch_id.id,
        })

        diff_amount_compare_to_zero = self.currency_id.compare_amounts(diff_amount, 0)
        if diff_amount_compare_to_zero != 0:
            self._apply_diff_on_account_payment_move(account_payment, payment_method, diff_amount)

        account_payment.action_post()
        return account_payment.move_id.line_ids.filtered(lambda line: line.account_id == account_payment.destination_account_id)

    def _create_split_account_payment(self, payment, amounts):
        payment_method = payment.payment_method_id
        if not payment_method.journal_id:
            return self.env['account.move.line']
        outstanding_account = payment_method.outstanding_account_id or self.company_id.account_journal_payment_debit_account_id
        accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
        destination_account = accounting_partner.property_account_receivable_id

        if float_compare(amounts['amount'], 0, precision_rounding=self.currency_id.rounding) < 0:
            # revert the accounts because account.payment doesn't accept negative amount.
            outstanding_account, destination_account = destination_account, outstanding_account

        account_payment = self.env['account.payment'].create({
            'amount': abs(amounts['amount']),
            'partner_id': payment.partner_id.id,
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id': destination_account.id,
            'ref': _('%s POS payment of %s in %s') % (payment_method.name, payment.partner_id.display_name, self.name),
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
            'branch_id': self.branch_id.id,
        })
        account_payment.action_post()
        return account_payment.move_id.line_ids.filtered(lambda line: line.account_id == account_payment.destination_account_id)


    def _get_rounding_difference_vals(self, amount, amount_converted):
        if self.config_id.cash_rounding:
            partial_args = {
                'name': 'Rounding line',
                'move_id': self.move_id.id,
                'branch_id': self.branch_id.id,
            }
            if float_compare(0.0, amount, precision_rounding=self.currency_id.rounding) > 0:    # loss
                partial_args['account_id'] = self.config_id.rounding_method.loss_account_id.id
                return self._debit_amounts(partial_args, -amount, -amount_converted)

            if float_compare(0.0, amount, precision_rounding=self.currency_id.rounding) < 0:   # profit
                partial_args['account_id'] = self.config_id.rounding_method.profit_account_id.id
                return self._credit_amounts(partial_args, amount, amount_converted)

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
        if not accounting_partner:
            raise UserError(_("You have enabled the \"Identify Customer\" option for %s payment method,"
                              "but the order %s does not contain a customer.") % (payment.payment_method_id.name,
                               payment.pos_order_id.name))
        partial_vals = {
            'account_id': accounting_partner.property_account_receivable_id.id,
            'move_id': self.move_id.id,
            'partner_id': accounting_partner.id,
            'branch_id': self.branch_id.id,
            'name': '%s - %s' % (self.name, payment.payment_method_id.name),
        }
        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        partial_vals = {
            'account_id': self._get_receivable_account(payment_method).id,
            'move_id': self.move_id.id,
            'branch_id': self.branch_id.id,
            'name': '%s - %s' % (self.name, payment_method.name)
        }
        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _get_invoice_receivable_vals(self, amount, amount_converted):
        partial_vals = {
            'account_id': self.company_id.account_default_pos_receivable_account_id.id,
            'move_id': self.move_id.id,
            'branch_id': self.branch_id.id,
            'name': _('From invoice payments'),
        }
        return self._credit_amounts(partial_vals, amount, amount_converted)


    def _prepare_line(self, order_line):
        def get_income_account(order_line):
            product = order_line.product_id
            income_account = product.with_company(order_line.company_id)._get_product_accounts()['income']
            if not income_account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).')
                                % (product.name, product.id))
            return order_line.order_id.fiscal_position_id.map_account(income_account)

        tax_ids = order_line.tax_ids_after_fiscal_position\
                    .filtered(lambda t: t.company_id.id == order_line.order_id.company_id.id)
        sign = -1 if order_line.qty >= 0 else 1
        price = sign * order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        check_refund = lambda x: x.qty * x.price_unit < 0
        is_refund = check_refund(order_line)
        tax_data = tax_ids.compute_all(price_unit=price, quantity=abs(order_line.qty), currency=self.currency_id, is_refund=is_refund, fixed_multiplicator=sign)
        taxes = tax_data['taxes']
        for tax in taxes:
            tax_rep = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
            tax['account_id'] = tax_rep.account_id.id
        date_order = order_line.order_id.date_order
        taxes = [{'date_order': date_order, **tax} for tax in taxes]
        return {
            'date_order': order_line.order_id.date_order,
            'branch_id': order_line.order_id.branch_id.id,
            'income_account_id': get_income_account(order_line).id,
            'amount': order_line.price_subtotal,
            'taxes': taxes,
            'base_tags': tuple(tax_data['base_tags']),
        }

   
    def _get_sale_vals(self, key, amount, amount_converted):
        account_id, sign, tax_keys, base_tag_ids = key
        tax_ids = set(tax[0] for tax in tax_keys)
        applied_taxes = self.env['account.tax'].browse(tax_ids)
        title = 'Sales' if sign == 1 else 'Refund'
        name = '%s untaxed' % title
        if applied_taxes:
            name = '%s with %s' % (title, ', '.join([tax.name for tax in applied_taxes]))
        partial_vals = {
            'name': name,
            'account_id': account_id,
            'move_id': self.move_id.id,
            'tax_ids': [(6, 0, tax_ids)],
            'tax_tag_ids': [(6, 0, base_tag_ids)],
            'branch_id': self.branch_id.id,
        }
        return self._credit_amounts(partial_vals, amount, amount_converted)

    def _get_tax_vals(self, key, amount, amount_converted, base_amount_converted):
        account_id, repartition_line_id, tax_id, tag_ids = key
        tax = self.env['account.tax'].browse(tax_id)
        partial_args = {
            'name': tax.name,
            'account_id': account_id,
            'move_id': self.move_id.id,
            'tax_base_amount': abs(base_amount_converted),
            'tax_repartition_line_id': repartition_line_id,
            'tax_tag_ids': [(6, 0, tag_ids)],
            'branch_id': self.branch_id.id,
        }
        return self._debit_amounts(partial_args, amount, amount_converted)

    def _get_stock_expense_vals(self, exp_account, amount, amount_converted):
        partial_args = {'account_id': exp_account.id, 'move_id': self.move_id.id,'branch_id': self.branch_id.id,}
        return self._debit_amounts(partial_args, amount, amount_converted, force_company_currency=True)

   

    def _get_stock_output_vals(self, out_account, amount, amount_converted):
        partial_args = {'account_id': out_account.id, 'move_id': self.move_id.id, 'branch_id': self.branch_id.id}
        return self._credit_amounts(partial_args, amount, amount_converted, force_company_currency=True)


    def _get_combine_statement_line_vals(self, journal_id, amount, payment_method):
        return {
            'date': fields.Date.context_today(self),
            'amount': amount,
            'payment_ref': self.name,
            'pos_session_id': self.id,
            'branch_id': self.branch_id.id,
            'journal_id': journal_id,
            'counterpart_account_id': self._get_receivable_account(payment_method).id,
        }

    def _get_split_statement_line_vals(self, journal_id, amount, payment):
        accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
        return {
            'date': fields.Date.context_today(self, timestamp=payment.payment_date),
            'amount': amount,
            'payment_ref': payment.name,
            'pos_session_id': self.id,
            'journal_id': journal_id,
            'branch_id': self.branch_id.id,
            'counterpart_account_id': accounting_partner.property_account_receivable_id.id,
            'partner_id': accounting_partner.id,
        }
    def _post_statement_difference(self, amount):
        if amount:
            if self.config_id.cash_control:
                st_line_vals = {
                    'journal_id': self.cash_journal_id.id,
                    'branch_id': self.config_id.branch_id.id,
                    'amount': amount,
                    'date': self.statement_line_ids.sorted()[-1:].date or fields.Date.context_today(self),
                    'pos_session_id': self.id,
                }

            if self.cash_register_difference < 0.0:
                if not self.cash_journal_id.loss_account_id:
                    raise UserError(
                        _('Please go on the %s journal and define a Loss Account. This account will be used to record cash difference.',
                          self.cash_journal_id.name))

                st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Loss)")
                st_line_vals['counterpart_account_id'] = self.cash_journal_id.loss_account_id.id
                st_line_vals['branch_id'] = self.config_id.branch_id.id
            else:
                # self.cash_register_difference  > 0.0
                if not self.cash_journal_id.profit_account_id:
                    raise UserError(
                        _('Please go on the %s journal and define a Profit Account. This account will be used to record cash difference.',
                          self.cash_journal_id.name))

                st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Profit)")
                st_line_vals['counterpart_account_id'] = self.cash_journal_id.profit_account_id.id
                st_line_vals['branch_id'] = self.config_id.branch_id.id

            self.env['account.bank.statement.line'].create(st_line_vals)


    def try_cash_in_out(self, _type, amount, reason, extras):
        sign = 1 if _type == 'in' else -1
        sessions = self.filtered('cash_journal_id')
        if not sessions:
            raise UserError(_("There is no cash payment method for this PoS Session"))

        self.env['account.bank.statement.line'].create([
            {
                'pos_session_id': session.id,
                'journal_id': session.cash_journal_id.id,
                'branch_id': session.branch_id.id,
                'amount': sign * amount,
                'date': fields.Date.context_today(self),
                'payment_ref': '-'.join([session.name, extras['translatedType'], reason]),
            }
            for session in sessions
        ])

        message_content = [f"Cash {extras['translatedType']}", f'- Amount: {extras["formattedAmount"]}']
        if reason:
            message_content.append(f'- Reason: {reason}')
        self.message_post(body='<br/>\n'.join(message_content))
   
class PosOrder(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one('res.branch', string='Branch',readonly=False)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
    branch_name = fields.Char(related='session_id.branch_name',readonly=False)
    branch_email = fields.Char(related='session_id.branch_email',readonly=False)
    branch_phone = fields.Char(related='session_id.branch_phone',readonly=False)
    branch_mobile = fields.Char(related='session_id.branch_mobile',readonly=False)

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
        return {
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'branch_id': self.env['pos.session'].browse(ui_order['pos_session_id']).branch_id.id,
            'sequence_number': ui_order['sequence_number'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid':  ui_order['amount_paid'],
            'amount_total':  ui_order['amount_total'],
            'amount_tax':  ui_order['amount_tax'],
            'amount_return':  ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'to_invoice': ui_order['to_invoice'] if "to_invoice" in ui_order else False,
            'to_ship': ui_order['to_ship'] if "to_ship" in ui_order else False,
            'is_tipped': ui_order.get('is_tipped', False),
            'tip_amount': ui_order.get('tip_amount', 0),
            'access_token': ui_order.get('access_token', '')
        }

    @api.model
    def _process_order(self, order, draft, existing_order):
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id
            order['branch_id'] = self.session_id.branch_id.id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            order['branch_id'] = pos_order.branch_id.id
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            pos_order._create_order_picking()
            pos_order._compute_total_cost_in_real_time()

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order._generate_pos_order_invoice()

        return pos_order.id


    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result.update({
            'branch_id': order.branch_id.id,
        })
        return result

    def _create_misc_reversal_move(self, payment_moves):
        """ Create a misc move to reverse this POS order and "remove" it from the POS closing entry.
        This is done by taking data from the order and using it to somewhat replicate the resulting entry in order to
        reverse partially the movements done ine the POS closing entry.
        """
        aml_values_list_per_nature = self._prepare_aml_values_list_per_nature()
        move_lines = []
        for aml_values_list in aml_values_list_per_nature.values():
            for aml_values in aml_values_list:
                aml_values['balance'] = -aml_values['balance']
                aml_values['amount_currency'] = -aml_values['amount_currency']
                move_lines.append(aml_values)

        # Make a move with all the lines.
        reversal_entry = self.env['account.move'].with_context(default_journal_id=self.config_id.journal_id.id).create({
            'journal_id': self.config_id.journal_id.id,
            'branch_id': self.config_id.branch_id.id,
            'date': fields.Date.context_today(self),
            'ref': _('Reversal of POS closing entry %s for order %s from session %s', self.session_move_id.name, self.name, self.session_id.name),
            'invoice_line_ids': [(0, 0, aml_value) for aml_value in move_lines],
        })
        reversal_entry.action_post()

        # Reconcile the new receivable line with the lines from the payment move.
        pos_account_receivable = self.company_id.account_default_pos_receivable_account_id
        reversal_entry_receivable = reversal_entry.line_ids.filtered(lambda l: l.account_id == pos_account_receivable)
        payment_receivable = payment_moves.line_ids.filtered(lambda l: l.account_id == pos_account_receivable)
        (reversal_entry_receivable | payment_receivable).reconcile()

    def _create_invoice(self, move_vals):
        self.ensure_one()
        new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type=move_vals['move_type']).create(move_vals)
        message = _(
            "This invoice has been created from the point of sale session: %s",
            self._get_html_link(),
        )
        new_move.message_post(body=message)
        if self.config_id.cash_rounding:
            rounding_applied = float_round(self.amount_paid - self.amount_total,
                                           precision_rounding=new_move.currency_id.rounding)
            rounding_line = new_move.line_ids.filtered(lambda line: line.display_type == 'rounding')
            if rounding_line and rounding_line.debit > 0:
                rounding_line_difference = rounding_line.debit + rounding_applied
            elif rounding_line and rounding_line.credit > 0:
                rounding_line_difference = -rounding_line.credit + rounding_applied
            else:
                rounding_line_difference = rounding_applied
            if rounding_applied:
                if rounding_applied > 0.0:
                    account_id = new_move.invoice_cash_rounding_id.loss_account_id.id
                else:
                    account_id = new_move.invoice_cash_rounding_id.profit_account_id.id
                if rounding_line:
                    if rounding_line_difference:
                        rounding_line.with_context(check_move_validity=False).write({
                            'debit': rounding_applied < 0.0 and -rounding_applied or 0.0,
                            'credit': rounding_applied > 0.0 and rounding_applied or 0.0,
                            'account_id': account_id,
                            'price_unit': rounding_applied,
                            'branch_id': self.config_id.branch_id.id,
                        })

                else:
                    self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'debit': rounding_applied < 0.0 and -rounding_applied or 0.0,
                        'credit': rounding_applied > 0.0 and rounding_applied or 0.0,
                        'quantity': 1.0,
                        'amount_currency': rounding_applied,
                        'partner_id': new_move.partner_id.id,
                        'move_id': new_move.id,
                        'currency_id': new_move.currency_id if new_move.currency_id != new_move.company_id.currency_id else False,
                        'company_id': new_move.company_id.id,
                        'company_currency_id': new_move.company_id.currency_id.id,
                        'display_type': 'rounding',
                        'sequence': 9999,
                        'branch_id': self.config_id.branch_id.id,
                        'name': new_move.invoice_cash_rounding_id.name,
                        'account_id': account_id,
                    })
            else:
                if rounding_line:
                    rounding_line.with_context(check_move_validity=False).unlink()
            if rounding_line_difference:
                existing_terms_line = new_move.line_ids.filtered(
                    lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                if existing_terms_line.debit > 0:
                    existing_terms_line_new_val = float_round(
                        existing_terms_line.debit + rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                else:
                    existing_terms_line_new_val = float_round(
                        -existing_terms_line.credit + rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                existing_terms_line.write({
                    'debit': existing_terms_line_new_val > 0.0 and existing_terms_line_new_val or 0.0,
                    'credit': existing_terms_line_new_val < 0.0 and -existing_terms_line_new_val or 0.0,
                })

                new_move._recompute_payment_terms_lines()
        return new_move


    def _prepare_invoice_vals(self):
        invoice_vals = super(PosOrder, self)._prepare_invoice_vals()
        invoice_vals['branch_id'] = self.branch_id.id

        return invoice_vals

    def _prepare_refund_values(self, current_session):
        invoice_vals = super(PosOrder, self)._prepare_refund_values(current_session)
        invoice_vals['branch_id'] = self.branch_id.id

        return invoice_vals

   

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        return {
            'amount': ui_paymentline['amount'] or 0.0,
            'payment_date': ui_paymentline['name'],
            'payment_method_id': ui_paymentline['payment_method_id'],
            'card_type': ui_paymentline.get('card_type'),
            'cardholder_name': ui_paymentline.get('cardholder_name'),
            'transaction_id': ui_paymentline.get('transaction_id'),
            'payment_status': ui_paymentline.get('payment_status'),
            'branch_id': order.branch_id.id,
            'ticket': ui_paymentline.get('ticket'),
            'pos_order_id': order.id,
        }



    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        for payments in pos_order['statement_ids']:
            order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'branch_id': order.branch_id.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Datetime.now(),
                'payment_method_id': cash_payment_method.id,
                'is_change': True,
            }
            order.add_payment(return_payment_vals)
    @api.model
    def _complete_values_from_session(self, session, values):
        values = super(PosOrder, self)._complete_values_from_session(session, values)
        values.setdefault('branch_id', session.config_id.branch_id.id)
        return values
     

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder,self)._prepare_invoice_line(order_line)
        res.update({'branch_id': order_line.branch_id.id,})
        return res

   

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"


    branch_id = fields.Many2one('res.branch', string='Branch',related='order_id.branch_id',store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


    def _prepare_refund_data(self,  refund_order, PosOrderLineLot):
        data = super(PosOrderLine, self)._prepare_refund_data( refund_order, PosOrderLineLot)
        data.update({'branch_id': refund_order.branch_id.id,})
        return data


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    branch_id = fields.Many2one('res.branch', string='Branch',readonly= True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',readonly= True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',readonly= True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',readonly= True)

    def _select(self):
        return super(PosOrderReport, self)._select() + ',s.branch_id AS branch_id, s.branch_group_id AS branch_group_id, s.branch_type_id AS branch_type_id, s.branch_state_id AS branch_state_id'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',s.branch_id,s.branch_group_id,s.branch_type_id,s.branch_state_id'


class PosPaymentIn(models.Model):
    _inherit = "pos.payment"

    branch_id = fields.Many2one('res.branch', string='Branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    def _export_for_ui(self, payment):
        result = super(PosPaymentIn, self)._export_for_ui(payment)
        result.update({
            'branch_id': payment.branch_id.id,})
        return result
    
    def _create_payment_moves(self):
        result = self.env['account.move']
        for payment in self:
            order = payment.pos_order_id
            payment_method = payment.payment_method_id
            if payment_method.type == 'pay_later' or float_is_zero(payment.amount, precision_rounding=order.currency_id.rounding):
                continue
            accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
            pos_session = order.session_id
            journal = pos_session.config_id.journal_id
            branch = pos_session.config_id.branch_id
            payment_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
                'journal_id': journal.id,
                'branch_id': branch.id,
                'date': fields.Date.context_today(payment),
                'ref': _('Invoice payment for %s (%s) using %s') % (order.name, order.account_move.name, payment_method.name),
                'pos_payment_ids': payment.ids,
            })
            result |= payment_move
            payment.write({'account_move_id': payment_move.id})
            amounts = pos_session._update_amounts({'amount': 0, 'amount_converted': 0}, {'amount': payment.amount}, payment.payment_date)
            credit_line_vals = pos_session._credit_amounts({
                'account_id': accounting_partner.with_company(order.company_id).property_account_receivable_id.id,  # The field being company dependant, we need to make sure the right value is received.
                'partner_id': accounting_partner.id,
                'branch_id': branch.id,
                'move_id': payment_move.id,
            }, amounts['amount'], amounts['amount_converted'])
            debit_line_vals = pos_session._debit_amounts({
                'account_id': pos_session.company_id.account_default_pos_receivable_account_id.id,
                'move_id': payment_move.id,
                'branch_id': branch.id,
            }, amounts['amount'], amounts['amount_converted'])
            self.env['account.move.line'].with_context(check_move_validity=False).create([credit_line_vals, debit_line_vals])
            payment_move._post()
        return result


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    branch_ids = fields.Many2many('res.branch', string='Branch',related='journal_id.branch_ids')

class PosMakePayment(models.TransientModel):
    _inherit = "pos.make.payment"


    def _default_branch(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            return self.env['pos.order'].browse(active_id).session_id.branch_id
        return False


    branch_id = fields.Many2one('res.branch', string='Branch', default=_default_branch)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
