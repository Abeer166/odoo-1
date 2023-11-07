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

import base64
import datetime
import re
from lxml import etree
import io
import math
import os
from collections import defaultdict
from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from PIL import Image
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.osv.expression import AND

from odoo.tests.common import Form
from itertools import groupby

import logging
import psycopg2
import pytz

_logger = logging.getLogger(__name__)


# class IrUiMenu(models.Model):
#     _inherit = 'ir.ui.menu'

#     def _load_menus_blacklist(self):
#         res = super()._load_menus_blacklist()
#         if self.env.user.has_group('branches.group_branch_user'):
#             res.append(self.env.ref('branches.menu_branches').id)
#         return res

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)

    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for account in self:
            account.branches_count = branches_count

    
    branch_ids = fields.Many2many(string='Share To Branches', comodel_name="res.branch", relation="res_partner_branch_rel", column1="partner_id", column2="branch_id",readonly=False)

    def _compute_is_branch(self):
        company = self.env.company
        if company.is_branch:
            self.is_branch = True
        else:
            self.is_branch = False

    is_branch = fields.Boolean(default='_compute_is_branch',store=True)


    @api.onchange('parent_id', 'branch_ids')
    def _onchange_parent_id(self):
        """methode to set branch on changing the parent branch"""
        if self.parent_id:
            self.branch_ids = self.parent_id.branch_ids


    def write(self, vals):
        """override write methode"""
        if vals.get('branch_ids'):
            branch_id = vals['branch_ids']
            for partner in self:
                # if partner.child_ids:
                for child in partner.child_ids:
                    child.write({'branch_ids': branch_ids})
        result = super(ResPartner, self).write(vals)
        return result


   

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'


    branch_ids = fields.Many2many(string='Share To Branches', comodel_name="res.branch", relation="bank_branch_rel", column1="bank_id", column2="branch_id")

    is_branch = fields.Boolean(related='company_id.is_branch')

    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)
 
    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for bank in self:
            bank.branches_count = branches_count

class Company(models.Model):
    _inherit = 'res.company'

    is_branch = fields.Boolean("Company has Branches?")
    branch_ids = fields.Many2many('res.branch','company_id', string='Company Branches')
    activat_internal_trans = fields.Boolean(string="Activate accounts when transfer between different storage locations",)
    inter_locations_clearing_account_id = fields.Many2one('account.account',
        domain="[('account_type', '=', 'asset_current'), ('deprecated', '=', False)]", string="Inter-locations Clearing Account",
         help="Intermediary account used when moving stock from a storage Location to another different storage Location")

    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)

    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for account in self:
            account.branches_count = branches_count

    activate_general_sequence = fields.Boolean('Activate Branches General Sequanses?',
        help="Use General Sequences For any branch automatic for branches withot any Custom Sequence instead of using odoo no_gap Sequence",
        readonly=False,default=False)

    gen_so_sequence_id = fields.Many2one('ir.sequence', string='So General Sequence',check_company=True,store=True,readonly=False)
    gen_po_sequence_id = fields.Many2one('ir.sequence', string='PO General Sequence',check_company=True,store=True,readonly=False)
    gen_inv_sequence_id = fields.Many2one('ir.sequence', string='INV General Sequence',check_company=True,store=True,readonly=False)
    gen_bill_sequence_id = fields.Many2one('ir.sequence', string='Bill General Sequence',check_company=True,store=True,readonly=False)
    gen_credit_sequence_id = fields.Many2one('ir.sequence', string='Credit General Sequence',check_company=True,store=True,readonly=False)
    gen_in_receipt_sequence_id = fields.Many2one('ir.sequence', string='IN Receipt General Sequence',check_company=True,store=True,readonly=False)
    gen_refund_sequence_id = fields.Many2one('ir.sequence', string='Refund General sequence',check_company=True,store=True,readonly=False)
    gen_out_receipt_sequence_id = fields.Many2one('ir.sequence', string='Out Receipt General Sequence',check_company=True,store=True,readonly=False)


    def create_sequence(self):
        if not self.gen_so_sequence_id:
            seq =self.sudo()._create_so_sequence()
            self.gen_so_sequence_id = seq.id

        if not self.gen_po_sequence_id:
            seq=self.sudo()._create_po_sequence()
            self.gen_po_sequence_id = seq.id

        if not self.gen_inv_sequence_id:
            seq=self.sudo()._create_inv_sequence()
            self.gen_inv_sequence_id = seq.id

        if not self.gen_bill_sequence_id:
            seq=self.sudo()._create_bill_sequence()
            self.gen_bill_sequence_id = seq.id

        if not self.gen_credit_sequence_id:
            seq=self.sudo()._create_credit_sequence()
            self.gen_credit_sequence_id = seq.id
            
        if not self.gen_in_receipt_sequence_id:
            seq=self.sudo()._create_in_receipt_sequence()
            self.gen_in_receipt_sequence_id = seq.id
            
        if not self.gen_refund_sequence_id:
            seq=self.sudo()._create_refund_sequence()
            self.gen_refund_sequence_id = seq.id
            
        if not self.gen_out_receipt_sequence_id:
            seq=self.sudo()._create_out_receipt_sequence()
            self.gen_out_receipt_sequence_id = seq.id
       
        self.update({
            'activate_general_sequence': True})
                
    @api.model
    def _create_so_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('So')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_po_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Po')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_inv_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Invoice')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_bill_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Bill')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_credit_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Credit Note')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_in_receipt_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Customer Receipt')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_refund_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Vendor Receipt')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_out_receipt_sequence(self):
        seq_name =''
        rang = '/%(range_year)s/'
        seq_name = _('Bill Receipt')
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id':self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_branch = fields.Boolean(string="Company has Branches?",related='company_id.is_branch', readonly=False)
    activat_internal_trans = fields.Boolean(string="Activate accounts when transfer between different storage locations",
        related='company_id.activat_internal_trans', readonly=False)
    inter_locations_clearing_account_id = fields.Many2one('account.account', string="Inter-locations Clearing Account",
        related='company_id.inter_locations_clearing_account_id', readonly=False,
        domain="[('account_type', '=', 'asset_current'), ('deprecated', '=', False)]",
        help="Intermediary account used when moving stock from a storage Location to another different storage Location")

class ResBranchSettings(models.Model):
    _name = 'res.branch.settings'
    _description = 'Branches Setting'
    _check_company_auto = True

    activat_internal_trans = fields.Boolean(string="Activate accounts when transfer between different storage locations",related='company_id.activat_internal_trans', readonly=False)
    inter_locations_clearing_account_id = fields.Many2one('account.account', string="Inter-locations Clearing Account",
        related='company_id.inter_locations_clearing_account_id', readonly=False,
        domain="[('account_type', '=', 'asset_current'), ('deprecated', '=', False)]",
        help="Intermediary account used when moving stock from a storage Location to another different storage Location")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


class AccountbranchGroup(models.Model):
    _name = 'account.branch.group'
    _description = 'Branch Categories'
    _inherit = ['image.mixin','portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _parent_store = True
    _rec_name = 'complete_name'
    _check_company_auto = True

    name = fields.Char(required=True, translate=True,index='trigram')
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index', default=0)
    description = fields.Text(string='Description', translate=True)
    more_details = fields.Html(string='More Details', translate=True,store=True)
    parent_id = fields.Many2one('account.branch.group', string="Parent", index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many('account.branch.group', 'parent_id', string="Children's")
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True,recursive=True)
    company_id = fields.Many2one('res.company', string='Company',index=True, default=lambda self: self.env.company)
    branch_ids = fields.One2many('res.branch','group_id', string='Branches')
    account_branch_group_count = fields.Integer(compute='_compute_sub_groups',string="Sub Groups")
    branch_count = fields.Integer('# Branches', compute='_compute_branch_count',help="The number of branches under this Group (Does not consider the children Group)",store=True)


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for group in self:
            if group.parent_id:
                group.complete_name = '%s / %s' % (group.parent_id.complete_name, group.name)
            else:
                group.complete_name = group.name

   
    def _compute_branch_count(self):
        read_group_res = self.env['res.branch'].read_group([('group_id', 'child_of', self.ids)], ['group_id'], ['group_id'])
        group_data = dict((data['group_id'][0], data['group_id_count']) for data in read_group_res)
        for categ in self:
            branch_count = 0
            for sub_categ_id in categ.search([('id', 'child_of', categ.ids)]).ids:
                branch_count += group_data.get(sub_categ_id, 0)
            categ.branch_count = branch_count


    def _compute_sub_groups(self):
        for record in self:
            record.account_branch_group_count = self.env['account.branch.group'].search_count([('parent_id', '=', record.id)])


    def redirect_sub_groups(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sub Groups',
            'view_mode': 'tree,form',
            'res_model': 'account.branch.group',
            'domain': [('parent_id', '=', self.id)],
            'target': 'current',
            'context': dict(self._context, default_parent_id=self.id),
        }


        ###########           Redirect Branch Group      ####################

    def redirect_sale_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': ['|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }

    def redirect_purchase_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': ['|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type','=','out_invoice'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_bill(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type','=','in_invoice'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_paid(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paid$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('payment_type','=','outbound'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_recived(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recived$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('payment_type','=','inbound'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice_credit(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Notes',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type','=','out_refund'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_refund(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refunds',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_group_id','=',self.id),('move_type','=','in_refund')],
            'domain': [('move_type','=','out_refund'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_entry(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type','=','entry'),'|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_picking(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': ['|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }
    def redirect_stock_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': ['|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_scrap_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'view_mode': 'tree,form',
            'res_model': 'stock.scrap',
            'domain': ['|',('branch_id.group_id.parent_id','=',self.id),('branch_id.group_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
        
class AccountbranchType(models.Model):
    _name = 'account.branch.type'
    _description = 'Branch Business Type'
    _inherit = ['image.mixin','portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string='Description', translate=True)
    more_details = fields.Html(string='More Details', translate=True,store=True)
    company_id = fields.Many2one('res.company', string='Company',index=True, default=lambda self: self.env.company)
    branch_ids = fields.One2many('res.branch','type_id', string='Branches')
    color = fields.Integer(string='Color Index', default=0)
   
    branch_count = fields.Integer(
        '# Branches', compute='_compute_branch_count',
        help="The number of branches under this Type")

    @api.depends('branch_ids')
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.branch_ids)

    def redirect_branches(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branches',
            'view_mode': 'tree,form',
            'res_model': 'res.branch',
            'domain': [('type_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_type_id=self.id),
        }

            ###########           Redirect Business Type      ####################

    def redirect_sale_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('branch_id.type_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }

    def redirect_purchase_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('branch_id.type_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.type_id','=',self.id),('move_type','=','out_invoice')],
            'target': 'current',
            'context': context,
        }
    def redirect_bill(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.type_id','=',self.id),('move_type','=','in_invoice')],
            'target': 'current',
            'context': context,
        }

    def redirect_paid(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paid$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id.type_id','=',self.id),('payment_type','=','outbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_recived(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recived$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id.type_id','=',self.id),('payment_type','=','inbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice_credit(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Notes',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.type_id','=',self.id),('move_type','=','out_refund')],
            'target': 'current',
            'context': context,
        }

    def redirect_refund(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refunds',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.type_id','=',self.id),('move_type','=','in_refund')],
            'target': 'current',
            'context': context,
        }
    def redirect_entry(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.type_id','=',self.id),('move_type','=','entry')],
            'target': 'current',
            'context': context,
        }

    def redirect_picking(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('branch_id.type_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }
    def redirect_stock_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': [('branch_id.type_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_scrap_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'view_mode': 'tree,form',
            'res_model': 'stock.scrap',
            'domain': [('branch_id.type_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

class AccountbranchTags(models.Model):
    _name = 'account.branch.tags'
    _description = 'Branches tags'
    _inherit = ['image.mixin','portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    more_details = fields.Html(string='More Details', translate=True,store=True)
    company_id = fields.Many2one('res.company', string='Company',index=True, default=lambda self: self.env.company)
    branch_ids = fields.Many2many(string='Branches', comodel_name="res.branch", relation="branch_tags_rel", column1="tag_id", column2="branch_id",readonly=False)

    color = fields.Integer(string='Color Index', default=0)
   
    branch_count = fields.Integer(
        '# Branches', compute='_compute_branch_count',
        help="The number of branches under this Type")

    @api.depends('branch_ids')
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.branch_ids)

    def redirect_branches(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branches',
            'view_mode': 'tree,form',
            'res_model': 'res.branch',
            'domain': [('tag_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_tag_id=self.id),
        }

            ###########           Redirect Branches Tags      ####################

    def redirect_sale_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('branch_id.tag_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_purchase_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('branch_id.tag_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.tag_id','=',self.id),('move_type','=','out_invoice')],
            'target': 'current',
            'context': context,
        }
    def redirect_bill(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.tag_id','=',self.id),('move_type','=','in_invoice')],
            'target': 'current',
            'context': context,
        }

    def redirect_paid(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paid$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id.tag_id','=',self.id),('payment_type','=','outbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_recived(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recived$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id.tag_id','=',self.id),('payment_type','=','inbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice_credit(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Notes',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.tag_id','=',self.id),('move_type','=','out_refund')],
            'target': 'current',
            'context': context,
        }

    def redirect_refund(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refunds',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.tag_id','=',self.id),('move_type','=','in_refund')],
            'target': 'current',
            'context': context,
        }
    def redirect_entry(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id.tag_id','=',self.id),('move_type','=','entry')],
            'target': 'current',
            'context': context,
        }

    def redirect_picking(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('branch_id.tag_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_stock_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': [('branch_id.tag_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_scrap_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'view_mode': 'tree,form',
            'res_model': 'stock.scrap',
            'domain': [('branch_id.tag_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

class Branch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'
    _inherit = ['format.address.mixin', 'image.mixin','portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'complete_name,sequence'
    _check_company_auto = True

    name = fields.Char(string='Branch Name', required=True, store=True, readonly=False)
    email = fields.Char(store=True, readonly=False)
    phone = fields.Char(store=True, readonly=False)
    mobile = fields.Char(store=True, readonly=False)
    street = fields.Char(store=True, readonly=False)
    street2 = fields.Char(store=True, readonly=False)
    zip = fields.Char(store=True, readonly=False)
    city = fields.Char(store=True, readonly=False)
    country_id = fields.Many2one('res.country', string='Country',related='company_id.country_id', store=True, readonly=False)
    state_id = fields.Many2one(
        'res.country.state',
        string="State", domain="[('country_id', '=?', country_id)]",required=True, ondelete='restrict', store=True, readonly=False)
    logo = fields.Binary(string="Branch Logo", readonly=False, store=True)

    sequence = fields.Integer(default=10)
    description = fields.Text(string='Description', translate=True)
    more_details = fields.Html(string='More Details', translate=True,store=True)
    wh_create = fields.Boolean('Create Warehouse?', default=True,store=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name',store=True)
    partner_ids = fields.Many2many(string='Branch Partners', comodel_name="res.partner", relation="res_partner_branch_rel", column2="partner_id", column1="branch_id")
    product_ids = fields.Many2many(string='Branch products', comodel_name="product.template", relation="product_temp_branch_rel", column2="product_id", column1="branch_id")
    account_ids = fields.Many2many(comodel_name='account.account',relation="account_branch_rel", column2="account_id", column1="branch_id",string='Allowed Accounts')
    journal_ids = fields.Many2many(comodel_name='account.journal',string='Allowed Journal', relation="journal_branch_rel",column1="branch_id" , column2="journal_id")
    line_ids = fields.One2many('account.move.line', 'branch_id', string="branch Lines",copy=False, readonly=True)
    warehouse_ids = fields.One2many('stock.warehouse','branch_id',string='Branch Warehouses')
    company_id = fields.Many2one('res.company', string='Company',index=True, default=lambda self: self.env.company, required=True)
    user_ids = fields.Many2many(string='Branch Users', comodel_name="res.users", relation="res_user_branch_rel",column1="branch_id" , column2="user_id",tracking=True)
    sequence = fields.Integer(help='Used to order Branches in the branch switcher', default=10)
    color = fields.Integer(string='Color Index', default=0)
    wh_code = fields.Char('Warehouse cod', size=5, help="Short name used to identify your warehouse")
    active = fields.Boolean('Active', default=True)

        # ***********Custome sequences**************
    use_custom_sequence = fields.Boolean('Branch Custom Sequanse?',default=True,store=True)
 
    so_code = fields.Char('SO Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    so_code1 = fields.Char('SO Suffix',help="Suffix value of the record for the sequence",required=False, trim=False,store=True)
    so_custom_sequence = fields.Boolean('SO Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    so_sequence_id = fields.Many2one('ir.sequence', string='So Sequence',check_company=True,store=True)
    so_use_date_range = fields.Boolean(string='So date range?',default=True,store=True)

    po_code = fields.Char('PO Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    po_code1 = fields.Char('PO Suffix',help="Suffix value of the record for the sequence", trim=False,required=False,store=True)
    po_custom_sequence = fields.Boolean('Po Custom Sequence ?',compute='_compute_custom_sequence',readonly=False,store=True)
    po_sequence_id = fields.Many2one('ir.sequence', string='PO Sequence',check_company=True,store=True)
    po_use_date_range = fields.Boolean(string='PO date range?',default=True,store=True)

    inv_code = fields.Char('INV Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    inv_code1 = fields.Char('INV Suffix',help="Suffix value of the record for the sequence", trim=False,required=False,store=True)
    inv_custom_sequence = fields.Boolean('INV Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    inv_custom_journal = fields.Boolean('Custom Invoice Journal?',default=False,store=True)
    inv_sequence_id = fields.Many2one('ir.sequence', string='INV Sequence',check_company=True,store=True)
    inv_use_date_range = fields.Boolean(string='INV date range?',default=True,store=True)

    bill_code = fields.Char('Bill Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    bill_code1 = fields.Char('Bill Suffix',help="Suffix value of the record for the sequence", trim=False,required=False,store=True )
    bill_custom_sequence = fields.Boolean('Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    bill_custom_journal = fields.Boolean('Custom Bill Journal?',default=False,store=True)
    bill_sequence_id = fields.Many2one('ir.sequence', string='Bill Sequence',check_company=True,store=True)
    bill_use_date_range = fields.Boolean(string='Bill date range?',default=True,store=True)

    credit_code = fields.Char('Credit Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    credit_code1 = fields.Char('Credit Suffix',help="Suffix value of the record for the sequence", trim=False ,required=False,store=True)
    credit_custom_sequence = fields.Boolean('Credit Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    credit_sequence_id = fields.Many2one('ir.sequence', string='Credit Sequence',check_company=True,store=True)
    credit_use_date_range = fields.Boolean(string='Credit date range?',default=True,store=True)

    out_receipt_code = fields.Char('INV Receipt Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    out_receipt_code1 = fields.Char('INV Receipt Suffix',help="Suffix value of the record for the sequence", trim=False,required=False,store=True)
    out_receipt_custom_sequence = fields.Boolean('INV Receipt Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    out_receipt_sequence_id = fields.Many2one('ir.sequence', string='Out Receipt Sequence',check_company=True,store=True)
    out_receipt_use_date_range = fields.Boolean(string='INV Receipt date range?',default=True,store=True)

    refund_code = fields.Char('Refund Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False,required=False,store=True)
    refund_code1 = fields.Char('Refund Suffix',help="Suffix value of the record for the sequence", trim=False,required=False ,store=True)
    refund_custom_sequence = fields.Boolean('Refund Custom sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    refund_sequence_id = fields.Many2one('ir.sequence', string='Refund sequence',check_company=True,store=True)
    refund_use_date_range = fields.Boolean(string='Refund date range?',default=True,store=True)

    in_receipt_code = fields.Char('IN Receipt Prefix',help="Prefix value of the record for the sequence",compute='_comput_branch_cod_names',readonly=False, trim=False ,required=False,store=True)
    in_receipt_code1 = fields.Char('IN Receipt Suffix',help="Suffix value of the record for the sequence", trim=False,required=False,store=True )
    in_receipt_custom_sequence = fields.Boolean('IN Receipt Custom Sequence?',compute='_compute_custom_sequence',readonly=False,store=True)
    in_receipt_sequence_id = fields.Many2one('ir.sequence', string='IN Receipt Sequence',check_company=True,store=True)
    in_receipt_use_date_range = fields.Boolean(string='IN Receipt date range?',default=True,store=True)
##########################        Sequences          #######################

    @api.depends('use_custom_sequence')
    def _compute_custom_sequence(self):
        for branch in self:
            if branch.use_custom_sequence:
                branch.so_custom_sequence = True
                branch.po_custom_sequence = True
                branch.inv_custom_sequence = True
                branch.bill_custom_sequence = True
                branch.credit_custom_sequence = True
                branch.out_receipt_custom_sequence = True
                branch.refund_custom_sequence = True
                branch.in_receipt_custom_sequence = True
            if not branch.use_custom_sequence:
                branch.so_custom_sequence = False
                branch.po_custom_sequence = False
                branch.inv_custom_sequence = False
                branch.bill_custom_sequence = False
                branch.credit_custom_sequence = False
                branch.out_receipt_custom_sequence = False
                branch.refund_custom_sequence = False
                branch.in_receipt_custom_sequence = False


    @api.depends('name')
    def _comput_branch_cod_names(self):
        for branch in self:
            if branch.name:
                if not branch.so_code and branch.so_custom_sequence:
                    branch.so_code = branch.name+ ' ' + _('So')
                if not branch.po_code and branch.po_custom_sequence:
                    branch.po_code = branch.name+ ' ' + _('PO')
                if not branch.inv_code and branch.inv_custom_sequence:
                    branch.inv_code = branch.name+ ' ' + _('Invoice')
                if not branch.bill_code and branch.bill_custom_sequence:
                    branch.bill_code = branch.name+ ' ' + _('Bill')
                if not branch.credit_code and branch.credit_custom_sequence:
                    branch.credit_code = branch.name+ ' ' + _('Credit Note')
                if not branch.out_receipt_code and branch.out_receipt_custom_sequence:
                    branch.out_receipt_code = branch.name+ ' ' + _('Customer Receipt')
                if not branch.refund_code and branch.refund_custom_sequence:
                    branch.refund_code = branch.name+ ' ' + _('Vendor Receipt')
                if not branch.in_receipt_code and branch.in_receipt_custom_sequence:
                    branch.in_receipt_code = branch.name+ ' ' + _('Bill Receipt')

       
    def _read_group_categ_id(self, categories, domain, order):
        category_ids = self.env.context.get('default_group_id')
        if not category_ids and self.env.context.get('group_expand'):
            category_ids = categories._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)


    group_id = fields.Many2one(
        'account.branch.group', 'Branch Group',
        group_expand='_read_group_categ_id',
        required=True)

    @api.depends('name', 'group_id.complete_name')
    def _compute_complete_name(self):
        for branch in self:
            if branch.group_id:
                branch.complete_name = '%s / %s' % (branch.group_id.complete_name, branch.name)
            else:
                branch.complete_name = branch.name

    type_id = fields.Many2one('account.branch.type' ,required=True, string='Branch Business Type')
    tag_id = fields.Many2many(string='Branch Tag', comodel_name="account.branch.tags", relation="branch_tags_rel", column2="tag_id", column1="branch_id")


    @api.onchange('group_id')
    def _onchange_group(self):
       if self.group_id and self.group_id.account_branch_group_count !=0:
          raise UserError(_("Please Select Sub Group where Parent Groups Not Allowed"))
   
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)

    def copy(self, default=None):
        raise UserError(_('Duplicating a Branch is not allowed. Please create a new Branch instead.'))

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The branch name must be unique !')]
 

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            branch = super(Branch, self).create(vals_list)
            self.env.user.write({'branches': [(4, branch.id)]})
            self.env.company.write({'branch_ids': [(4, branch.id)],'is_branch': True})
            if vals.get('wh_create') and 'wh_code' in vals:
                self.env['stock.warehouse'].check_access_rights('create')
                self.env['stock.warehouse'].sudo().create({'branch_id': branch.id,'name': branch.name, 'code': branch.wh_code[:5], 'company_id': branch.company_id.id})
            if 'company_id' in vals:
                branch.country_id = branch.company_id.country_id.id or branch.company_id.partner_id.country_id.id
            if 'company_id' not in vals:
                branch.company_id= self.env.company.id
                if branch.company_id:
                    branch.country_id = branch.company_id.country_id.id or branch.company_id.partner_id.country_id.id
        return branch


    def write(self, vals):
        branch = self.with_context(active_test=False)
        for branch in self:
            if 'active' in vals:
                products = self.env['product.template'].with_context(active_test=False).search([('branch_ids', '=', branch.id)])
                product_ids = products.filtered(lambda r: len(r.branch_ids) == 1).write({'active': vals['active']})
                partners = self.env['res.partner'].with_context(active_test=False).search([('branch_ids', '=', branch.id)])
                partner_ids = partners.filtered(lambda r: len(r.branch_ids) == 1).write({'active': vals['active']})
                warehouses = self.env['stock.warehouse'].with_context(active_test=False).search([('branch_id', '=', branch.id)])
                warehouse_ids = warehouses.filtered(lambda r: len(r.branch_id) > 0)
                for warehouse in warehouse_ids:
                    warehouse.write({'active': vals['active']})
        # self.clear_caches()
        result = super(Branch, self).write(vals)

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('branch_id', False):
            branch_ids = self._context.get('branch_id', False)
            for branch in branch_ids:
                for ids in branch[2:]:
                    if len(ids) > 0:
                        args.append(('id', 'in', ids))
                    else:
                        args.append(('id', 'in', []))
        if self._context.get('company_id', False):
            branches = self.env.user.branches.filtered(lambda m: m.company_id.id == self._context.get('company_id')).ids
            if branches:
                args.append(('id', 'in', branches))
        return super(Branch, self).name_search(name, args=args, operator=operator, limit=limit)


   
###########           Redirect Branch      ####################
    def redirect_accounts(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chart of Account',
            'view_mode': 'tree,form',
            'res_model': 'account.account',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }
    def redirect_warehouses(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warehouses',
            'view_mode': 'tree,form',
            'res_model': 'stock.warehouse',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_users(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Users',
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }
    def redirect_journals(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journals',
            'view_mode': 'tree,form',
            'res_model': 'account.journal',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }
    def redirect_products(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }
    def redirect_product_variants(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products Variants',
            'view_mode': 'tree,form',
            'res_model': 'product.template',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }


    def redirect_partners(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partners',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'domain': ['|',('branch_ids','=',self.id),('branch_ids','=',False)],
            'target': 'current',
            'context': context,
        }


    def redirect_sale_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }

    def redirect_purchase_order(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id','=',self.id),('move_type','=','out_invoice')],
            'target': 'current',
            'context': context,
        }
    def redirect_bill(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id','=',self.id),('move_type','=','in_invoice')],
            'target': 'current',
            'context': context,
        }

    def redirect_paid(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paid$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id','=',self.id),('payment_type','=','outbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_recived(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recived$',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('branch_id','=',self.id),('payment_type','=','inbound')],
            'target': 'current',
            'context': context,
        }

    def redirect_invoice_credit(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Notes',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id','=',self.id),('move_type','=','out_refund')],
            'target': 'current',
            'context': context,
        }

    def redirect_refund(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refunds',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id','=',self.id),('move_type','=','in_refund')],
            'target': 'current',
            'context': context,
        }
    def redirect_entry(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('branch_id','=',self.id),('move_type','=','entry')],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }

    def redirect_picking(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': dict(self._context, default_branch_id=self.id),
        }
    def redirect_stock_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }

    def redirect_scrap_move(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'view_mode': 'tree,form',
            'res_model': 'stock.scrap',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }



class ResBranchInh(models.Model):
    _inherit = 'res.branch'

                    
    @api.model
    def _create_so_sequence(self, vals):
            daterange=''
            seq_name =''
            rang=''
            suffix = ''
            if 'so_use_date_range' in vals:
                daterange= True
                rang = '/%(range_year)s/'
            if 'so_use_date_range' not in vals:
                daterange= False
                rang = ''
            if 'so_code' not in vals:
                seq_name = self.name + ' ' + _('So')
            if 'so_code' in vals:
                seq_name = vals['so_code']
            if 'so_code1' in vals:
                suffix = vals['so_code1']
            if 'so_code1' not in vals:
                suffix = ''
            seq = {
                'name': str(seq_name),
                'implementation': 'no_gap',
                'prefix': str(seq_name)+ rang,
                'suffix': suffix,
                'padding': 4,
                'number_increment': 1,
                'use_date_range': daterange,
                'company_id': vals.get('company_id') or self.env.company.id,
            }
            seq = self.env['ir.sequence'].create(seq)
            return seq

    @api.model
    def _create_po_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('po_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('po_use_date_range'):
            daterange= False
            rang = ''
        if 'po_code' not in vals:
            seq_name = self.name + ' ' + _('Po')
        if 'po_code' in vals:
            seq_name = vals['po_code']
        if 'po_code1' in vals:
            suffix = vals['po_code1']
        if 'po_code1' not in vals:
            suffix = ''
        seq = {
            'name': seq_name,
            'implementation': 'no_gap',
            'prefix': str(seq_name)+ rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_inv_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('inv_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('inv_use_date_range'):
            daterange: False
            rang = ''
        if 'inv_code' not in vals:
            seq_name = self.name+ ' ' + _('Invoice')
        if 'inv_code' in vals:
            seq_name = vals['inv_code']
        if 'inv_code1' in vals:
            suffix = vals['inv_code1']
        if 'inv_code1' not in vals:
            suffix = ''
        seq = {
            'name': seq_name,
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_bill_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('bill_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('bill_use_date_range'):
            daterange: False
            rang = ''
        if 'bill_code' not in vals:
            seq_name = self.name+ ' ' + _('Bill')
        if 'bill_code' in vals:
            seq_name = vals['bill_code']
        if 'bill_code1' in vals:
            suffix = vals['bill_code1']
        if 'bill_code1' not in vals:
            suffix = ''
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_credit_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('credit_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('credit_use_date_range'):
            daterange: False
            rang = ''
        if 'credit_code' not in vals:
            seq_name = self.name+ ' ' + _('Credit Note')
        if 'credit_code' in vals:
            seq_name = vals['credit_code']
        if 'credit_code1' in vals:
            suffix = vals['credit_code1']
        if 'credit_code1' not in vals:
            suffix = ''
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def _create_in_receipt_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('in_receipt_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('in_receipt_use_date_range'):
            daterange: False
            rang = ''
        if 'in_receipt_code' not in vals:
            seq_name = self.name+ ' ' + _('Customer Receipt')
        if 'in_receipt_code' in vals:
            seq_name = vals['in_receipt_code']
        if 'in_receipt_code1' in vals:
            suffix = vals['refund_code1']
        if 'in_receipt_code1' not in vals:
            suffix = ''
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq
    @api.model
    def _create_refund_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('refund_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('refund_use_date_range'):
            daterange: False
            rang = ''
        if 'refund_code' not in vals:
            seq_name = self.name+ ' ' + _('Vendor Receipt')
        if 'refund_code' in vals:
            seq_name = vals['refund_code']
        if 'refund_code1' in vals:
            suffix = vals['refund_code1']
        if 'refund_code1' not in vals:
            suffix = ''
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq
    @api.model
    def _create_out_receipt_sequence(self, vals):
        daterange=''
        seq_name =''
        rang=''
        suffix = ''
        if vals.get('out_receipt_use_date_range'):
            daterange= True
            rang = '/%(range_year)s/'
        if not vals.get('out_receipt_use_date_range'):
            daterange: False
            rang = ''
        if 'out_receipt_code' not in vals:
            seq_name = self.name+ ' ' + _('Bill Receipt')
        if 'out_receipt_code' in vals:
            seq_name = vals['out_receipt_code']
        if 'out_receipt_code1' in vals:
            suffix = vals['out_receipt_code1']
        if 'out_receipt_code1' not in vals:
            suffix = ''
        seq = {
            'name': str(seq_name),
            'implementation': 'no_gap',
            'prefix': str(seq_name) + rang,
            'suffix': suffix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': daterange,
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('so_sequence_id') :
                vals.update({'so_sequence_id': self.sudo()._create_so_sequence(vals).id})

            if not vals.get('po_sequence_id') :
                vals.update({'po_sequence_id': self.sudo()._create_po_sequence(vals).id})

            if not vals.get('inv_sequence_id') :
                vals.update({'inv_sequence_id': self.sudo()._create_inv_sequence(vals).id})

            if not vals.get('bill_sequence_id') :
                vals.update({'bill_sequence_id': self.sudo()._create_bill_sequence(vals).id})

            if not vals.get('credit_sequence_id') :
                vals.update({'credit_sequence_id': self.sudo()._create_credit_sequence(vals).id})

            if not vals.get('in_receipt_sequence_id') :
                vals.update({'in_receipt_sequence_id': self.sudo()._create_in_receipt_sequence(vals).id})

            if not vals.get('refund_sequence_id') :
                vals.update({'refund_sequence_id': self.sudo()._create_refund_sequence(vals).id})

            if not vals.get('out_receipt_sequence_id') :
                vals.update({'out_receipt_sequence_id': self.sudo()._create_out_receipt_sequence(vals).id})

        return super(ResBranchInh, self).create(vals_list)
