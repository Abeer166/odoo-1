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

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from functools import partial
from itertools import groupby
import json

from markupsafe import escape, Markup
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang, format_amount

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
   
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                branch = vals.get("branch_id")
                company = vals.get("company_id")
                if branch:
                    use_custom_sequence = self.env['res.branch'].browse(branch).use_custom_sequence
                    activate_general_sequence = self.env['res.company'].browse(company).activate_general_sequence
                    po_custom_sequence = self.env['res.branch'].browse(branch).po_custom_sequence
                    gen_po_sequence_id = self.env['res.company'].browse(company).gen_po_sequence_id
                    if use_custom_sequence:
                        if po_custom_sequence:
                            sequence_id = self.env['res.branch'].browse(branch).po_sequence_id
                            if sequence_id:
                                vals["name"] = sequence_id._next() or "/"
                        if not po_custom_sequence:
                            if activate_general_sequence:
                                if gen_po_sequence_id:
                                    sequence_id = self.env['res.company'].browse(company).gen_po_sequence_id
                                    if sequence_id:
                                        vals["name"] = sequence_id._next() or "/"
                    if not use_custom_sequence:
                        if activate_general_sequence:
                            if gen_po_sequence_id:
                                sequence_id = self.env['res.company'].browse(company).gen_po_sequence_id
                                if sequence_id:
                                    vals["name"] = sequence_id._next() or "/"
        return super(PurchaseOrder, self).create(vals_list)

    @api.model
    def _default_branch_id(self):
        branch_id = self.branch_id
        if self._context.get('default_branch_id'):
            branch_id = self._context.get('default_branch_id')
        if not self._context.get('default_branch_id'):
            if self.env.user.branch_id:
                branch_id = self.env.user.branch_id.id
            elif self.env.user.branch_ids and not self.env.user.branch_id:
                branches = self.env['res.branch'].search([('user_ids', '=', self.env.user.id),('company_id', '=', self.env.company.id)])
                if branches:
                    branch_id = branches[0].id
        return branch_id


  

    branch_id = fields.Many2one("res.branch", string='Branch', default=_default_branch_id, tracking=True,states=Purchase.READONLY_STATES,store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    is_branch = fields.Boolean(related='company_id.is_branch')

    warehouse_id = fields.Many2one('stock.warehouse',  string='Warehouse', states=Purchase.READONLY_STATES,)
    journal_id = fields.Many2one("account.journal", string="Journal",copy=True,states=Purchase.READONLY_STATES)
    bill_custom_journal = fields.Boolean(related='branch_id.bill_custom_journal')

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if not self.branch_id:
            self.update({
                'warehouse_id': False,
                'journal_id': False,
                'partner_id': False,
            })
            return
        if self.branch_id:
            warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
            journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.company_id.id),'|',('branch_ids', '=', self.branch_id.id),('branch_ids', '=', False)])
            partner = self.env['res.partner'].search([ ('company_id', 'in', (False, self.company_id.id)),'|',('branch_ids', '=', self.branch_id.id),('branch_ids', '=', False)])
            self.update({
                'warehouse_id': False,
                'journal_id': False,
                'partner_id': False,
            })
            if warehouse:
                self.warehouse_id = warehouse[0].id
                self.onchange_warehouse_id()
            if journal:
                self.journal_id = journal[0].id
            if partner:
                self.partner_id = partner[0].id
  
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.company_id.is_branch and not self._context.get('default_branch_id'):
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            self.warehouse_id = False
            if self.env.user.branch_id:
                self.branch_id = self.env.user.branch_id.id
                self._onchange_branch_id()
            if not self.env.user.branch_id and len(branches) > 0:
                self.branch_id = branches[0]
                self._onchange_branch_id()
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        res = super(PurchaseOrder, self)._onchange_company_id()


    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id and self.company_id.is_branch:
            picking = self.env['stock.picking.type'].search([('warehouse_id', '=', self.warehouse_id.id),('code', '=', 'incoming')])
            self.picking_type_id = False
            if self.warehouse_id and picking:
                self.picking_type_id = picking[0].id
            return {'domain': {'picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            return {'domain': {'picking_type_id': []}}


    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'),x.get('branch_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()

        return self.action_view_invoice(moves)


    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        if self.journal_id and self.branch_id:
            invoice_vals.update({'journal_id': self.journal_id.id,'branch_readonly': True,'branch_id': self.branch_id.id,'branch_type_id' : self.branch_id.type_id.id,'branch_group_id' : self.branch_id.group_id.id,'branch_state_id' : self.branch_id.state_id.id, })
        if not self.journal_id and self.branch_id:
            invoice_vals.update({'branch_readonly': True,'branch_id': self.branch_id.id,'branch_type_id' : self.branch_id.type_id.id,'branch_group_id' : self.branch_id.group_id.id,'branch_state_id' : self.branch_id.state_id.id, })
        return invoice_vals

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.branch_id:
            res.update({'branch_id': self.branch_id.id,'branch_type_id' : self.branch_id.type_id.id,'branch_group_id' : self.branch_id.group_id.id,'branch_state_id' : self.branch_id.state_id.id})
        return res
   
    
class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    branch_id = fields.Many2one('res.branch',related='order_id.branch_id',store=True)
    is_branch = fields.Boolean(related='order_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


  
    def _prepare_stock_moves(self, picking):
        template = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if template:
            template[0].update({
                                'branch_id': picking.branch_id.id,
                                'branch_type_id': picking.branch_id.type_id.id,
                                'branch_group_id': picking.branch_id.group_id.id,
                                'branch_state_id': picking.branch_id.state_id.id,
                            })
        return template
   

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    branch_id = fields.Many2one('res.branch',string="Branch" )
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State', )


    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            self.branch_type_id =  self.branch_id.type_id.id
            self.branch_group_id =  self.branch_id.group_id.id
            self.branch_state_id =  self.branch_id.state_id.id
  
    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.branch_type_id as branch_type_id, po.branch_group_id as branch_group_id, po.branch_id as branch_id, po.branch_state_id as branch_state_id"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.branch_type_id, po.branch_group_id, po.branch_id, po.branch_state_id"

   
