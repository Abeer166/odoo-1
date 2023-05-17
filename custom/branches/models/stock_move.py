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

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, OrderedSet

import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'


    branch_id = fields.Many2one("res.branch",check_company=True,string="Branch",store=True)

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if self.picking_id:
            if self.picking_id.branch_id:
                self.branch_id =  self.picking_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.is_branch:
            if self.product_id:
                self.branch_id =  self.picking_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False
        res = super(StockMove, self)._onchange_product_id()

    

    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )



    location_acc_valuation = fields.Many2one(
        'account.account', 'Stock Valuation Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product, this account will hold the current value of the products.""",)
    location_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0])]", check_company=True,
        help="When doing automated inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed.")

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        if self.company_id.is_branch:
            valuation_partner_id = self._get_partner_id_for_valuation_lines()
            move_ids = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, svl_id, description)
            svl = self.env['stock.valuation.layer'].browse(svl_id)
            if self.env.context.get('force_period_date'):
                date = self.env.context.get('force_period_date')
            elif svl.account_move_line_id:
                date = svl.account_move_line_id.date
            else:
                date = fields.Date.context_today(self)
            return {
                'journal_id': journal_id,
                'line_ids': move_ids,
                'partner_id': valuation_partner_id,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'branch_id': self.branch_id.id or self.picking_id.branch_id.id or self.picking_type_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False,
                'branch_group_id': self.branch_group_id.id or self.picking_type_id.branch_group_id.id or self.picking_id.branch_id.group_id.id  or self.location_id.branch_id.group_id.id or self.location_dest_id.branch_id.group_id.id or False,
                'branch_type_id': self.branch_type_id.id or self.picking_type_id.branch_type_id.id or self.picking_id.branch_id.type_id.id  or self.location_id.branch_id.type_id.id or self.location_dest_id.branch_id.type_id.id or False,
                'branch_state_id': self.branch_state_id.id or self.picking_type_id.branch_state_id.id or self.picking_id.branch_id.state_id.id  or self.location_id.branch_id.state_id.id or self.location_dest_id.branch_id.state_id.id or False,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'move_type': 'entry',
            }
        else:
            valuation_partner_id = self._get_partner_id_for_valuation_lines()
            move_ids = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, svl_id, description)
            svl = self.env['stock.valuation.layer'].browse(svl_id)
            if self.env.context.get('force_period_date'):
                date = self.env.context.get('force_period_date')
            elif svl.account_move_line_id:
                date = svl.account_move_line_id.date
            else:
                date = fields.Date.context_today(self)
            return {
                'journal_id': journal_id,
                'line_ids': move_ids,
                'partner_id': valuation_partner_id,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
            }


    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        if self.company_id.is_branch:
            if self.picking_type_id.code !='internal' and self.product_id.valuation == "real_time" and self.is_branch:
                res['debit_line_vals'].update({'branch_id': self.branch_id.id or self.picking_id.branch_id.id or self.picking_type_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False,
                    'branch_group_id': self.branch_group_id.id or self.picking_id.branch_group_id.id or self.picking_type_id.branch_group_id.id or self.location_id.branch_group_id.id or self.location_dest_id.branch_group_id.id or False,
                    'branch_type_id': self.branch_type_id.id or self.picking_id.branch_type_id.id or self.picking_type_id.branch_type_id.id or self.location_id.branch_type_id.id or self.location_dest_id.branch_type_id.id or False,
                    'branch_state_id': self.branch_state_id.id or self.picking_id.branch_state_id.id or self.picking_type_id.branch_state_id.id or self.location_id.branch_state_id.id or self.location_dest_id.branch_state_id.id or False,})
                res['credit_line_vals'].update({'branch_id': self.branch_id.id or self.picking_id.branch_id.id or self.picking_type_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False,
                    'branch_type_id': self.branch_type_id.id or self.picking_id.branch_type_id.id or self.picking_type_id.branch_type_id.id or self.location_id.branch_type_id.id or self.location_dest_id.branch_type_id.id or False,
                    'branch_group_id': self.branch_group_id.id or self.picking_id.branch_group_id.id or self.picking_type_id.branch_group_id.id or self.location_id.branch_group_id.id or self.location_dest_id.branch_group_id.id or False,
                    'branch_state_id': self.branch_state_id.id or self.picking_id.branch_state_id.id or self.picking_type_id.branch_state_id.id or self.location_id.branch_state_id.id or self.location_dest_id.branch_state_id.id or False,})
                if 'price_diff_line_vals' in res:
                    res['price_diff_line_vals'].update({'branch_id': self.branch_id.id or self.picking_id.branch_id.id or self.picking_type_id.branch_id.id or self.location_id.branch_id.id or self.location_dest_id.branch_id.id or False,'branch_type_id': self.branch_type_id.id or False ,'branch_group_id': self.branch_group_id.id or False,'branch_state_id': self.branch_state_id.id or False,})
            if self.picking_type_id.code == 'internal' and self.product_id.valuation == "real_time" and self.is_branch:
                res['debit_line_vals'].update({'branch_id': self.location_dest_id.branch_id.id,'branch_type_id': self.location_dest_id.branch_id.type_id.id ,'branch_group_id': self.location_dest_id.branch_id.group_id.id ,'branch_state_id': self.location_dest_id.branch_id.state_id.id,})
                res['credit_line_vals'].update({'branch_id': self.location_id.branch_id.id,'branch_type_id': self.location_id.branch_id.type_id.id ,'branch_group_id': self.location_id.branch_id.group_id.id ,'branch_state_id': self.location_id.branch_id.state_id.id,})
                if 'price_diff_line_vals' in res:
                    res['price_diff_line_vals'].update({'branch_id': self.branch_id.id,'branch_type_id': self.branch_id.type_id.id ,'branch_group_id': self.branch_id.group_id.id ,'branch_state_id': self.branch_id.state_id.id,})
        return res

    def _get_accounting_data_for_valuation(self):
        res = super(StockMove, self)._get_accounting_data_for_valuation()
        if self.company_id.activat_internal_trans and self.picking_type_id.code != 'internal':
            self.ensure_one()
            self = self.with_context(force_company=self.company_id.id)
            accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

            if self.location_id.valuation_out_account_id:
                acc_src = self.location_id.valuation_out_account_id.id
            else:
                acc_src = accounts_data['stock_input'].id

            if self.location_dest_id.valuation_in_account_id:
                acc_dest = self.location_dest_id.valuation_in_account_id.id
            else:
                acc_dest = accounts_data['stock_output'].id

            acc_valuation = self.location_id.location_acc_valuation or self.location_dest_id.location_acc_valuation or accounts_data.get('stock_valuation', False)
            if acc_valuation:
                acc_valuation = acc_valuation.id
            if not accounts_data.get('stock_journal', False):
                raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
            if not acc_src:
                raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
            if not acc_dest:
                raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
            if not acc_valuation:
                raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))

            journal_id = self.location_id.location_stock_journal.id or self.location_dest_id.location_stock_journal.id or accounts_data['stock_journal'].id
            return journal_id, acc_src, acc_dest, acc_valuation

        return res

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in self:
            if not move.company_id.is_branch and not move.company_id.activat_internal_trans:
                return True

            if not move.company_id.is_branch and move.company_id.activat_internal_trans and not move.scrapped:
                if move.picking_type_id.code == 'internal' and not move.company_id.inter_locations_clearing_account_id:
                    raise UserError(_("please Define Inter-locations clearing account in Company Info"))
                if move.picking_type_id.code == 'internal' and move.company_id.inter_locations_clearing_account_id:
                    if not move.picking_type_id.code == "internal":
                        return True
                    if move.picking_type_id.code == "internal":
                        if move.product_id.valuation == "real_time" and move.product_id.type == "product":
                            if (move.location_id.company_id
                                and move.location_id.company_id == move.location_dest_id.company_id
                                and move.location_id != move.location_dest_id):
                                (
                                    journal_id,
                                    acc_src,
                                    acc_dest,
                                    acc_valuation,
                                ) = move._get_accounting_data_for_valuation()
                                move_total_value = (move.product_id.standard_price)*(move.product_qty)
                                if move_total_value >0:
                                    location_acc_valuation_from = move.location_id.location_acc_valuation.id or acc_valuation
                                    journal_id_from = move.location_id.location_stock_journal.id or journal_id
                                    journal_id_to = move.location_dest_id.location_stock_journal.id or journal_id
                                    location_acc_valuation_to = move.location_dest_id.location_acc_valuation.id or acc_valuation
                                    inter_locations_clearing_account_id = move.company_id.inter_locations_clearing_account_id.id
                                    ref_name = '%s- %s' % (move.picking_id.name,move.product_id.display_name)
                                    svl_id = move.product_id.standard_price
                                    move_lines_to = move._prepare_account_move_line(
                                        move.product_qty,
                                        move_total_value,
                                        location_acc_valuation_from,
                                        inter_locations_clearing_account_id,
                                        svl_id,
                                        ref_name,
                                    )
                                    move_lines_from = move._prepare_account_move_line(
                                        move.product_qty,
                                        move_total_value,
                                        inter_locations_clearing_account_id,
                                        location_acc_valuation_to,
                                        svl_id,
                                        ref_name,
                                    )
                                    AccountMove = move.env["account.move"].with_context(
                                                force_company=move.location_id.company_id.id,
                                                company_id=move.company_id.id,)
                                    if move_lines_to and move_lines_from and move_total_value !=0:
                                        all_lines = move_lines_from + move_lines_from
                                        date = move._context.get('force_period_date', fields.Date.context_today(self))
                                        new_account_move = AccountMove.sudo().create(
                                                {
                                                    "journal_id": journal_id_from,
                                                    "line_ids": move_lines_to,
                                                    "company_id": move.company_id.id,
                                                    'date': date,
                                                    "ref": move.picking_id and move.picking_id.name,
                                                    "stock_move_id": move.id,
                                                    "move_type": 'entry',
                                                }
                                            )
                                        new_account_move._post()
                                        new_account_move2 = AccountMove.sudo().create(
                                                {
                                                    "journal_id": journal_id_to,
                                                    "line_ids": move_lines_from,
                                                    "company_id": move.company_id.id,
                                                    'date': date,
                                                    "ref": move.picking_id and move.picking_id.name,
                                                    "stock_move_id": move.id,
                                                    "move_type": 'entry',
                                                }
                                            )
                                        new_account_move2._post()
            if move.company_id.is_branch and not move.scrapped:
                if move.company_id.activat_internal_trans and move.picking_type_id.code == 'internal':
                    if not move.company_id.inter_locations_clearing_account_id:
                        raise UserError(_("please Define Inter-locations clearing account in Company Info"))
                    if move.company_id.inter_locations_clearing_account_id:
                        if not move.picking_type_id.code == "internal":
                            return True
                        if move.picking_type_id.code == "internal":
                            if move.product_id.valuation == "real_time" and move.product_id.type == "product":
                                if (move.location_id.company_id
                                    and move.location_id.company_id == move.location_dest_id.company_id
                                    and move.location_id != move.location_dest_id):
                                    (
                                        journal_id,
                                        acc_src,
                                        acc_dest,
                                        acc_valuation,
                                    ) = move._get_accounting_data_for_valuation()
                                    move_total_value = (move.product_id.standard_price)*(move.product_qty)
                                    if move_total_value >0:
                                        location_acc_valuation_from = move.location_id.location_acc_valuation.id or acc_valuation
                                        journal_id_from = move.location_id.location_stock_journal.id or journal_id
                                        journal_id_to = move.location_dest_id.location_stock_journal.id or journal_id
                                        location_acc_valuation_to = move.location_dest_id.location_acc_valuation.id or acc_valuation
                                        inter_locations_clearing_account_id = move.company_id.inter_locations_clearing_account_id.id
                                        ref_name = '%s- %s' % (move.picking_id.name,move.product_id.display_name)
                                        from_branch = move.location_id.branch_id.id
                                        from_branch_group = move.location_id.branch_id.group_id.id
                                        from_branch_type = move.location_id.branch_id.type_id.id
                                        from_branch_state = move.location_id.branch_id.state_id.id
                                        to_branch = move.location_dest_id.branch_id.id
                                        to_branch_group = move.location_dest_id.branch_id.group_id.id
                                        to_branch_type = move.location_dest_id.branch_id.type_id.id
                                        to_branch_state = move.location_dest_id.branch_id.state_id.id
                                        svl_id = move.product_id.standard_price
                                        move_lines_to = move._prepare_account_move_line(
                                            move.product_qty,
                                            move_total_value,
                                            location_acc_valuation_from,
                                            inter_locations_clearing_account_id,
                                            svl_id,
                                            ref_name,
                                        )
                                        move_lines_from = move._prepare_account_move_line(
                                            move.product_qty,
                                            move_total_value,
                                            inter_locations_clearing_account_id,
                                            location_acc_valuation_to,
                                            svl_id,
                                            ref_name,
                                        )
                                        AccountMove = move.env["account.move"].with_context(
                                                    force_company=move.location_id.company_id.id,
                                                    company_id=move.company_id.id,)
                                        if move_lines_to and move_lines_from and move_total_value !=0:
                                            all_lines = move_lines_from + move_lines_from
                                            date = move._context.get('force_period_date', fields.Date.context_today(self))
                                            new_account_move = AccountMove.sudo().create(
                                                    {
                                                        "journal_id": journal_id_from,
                                                        "line_ids": move_lines_to,
                                                        "company_id": move.company_id.id,
                                                        'date': date,
                                                        'branch_id': from_branch,
                                                        'branch_group_id': from_branch_group,
                                                        'branch_type_id': from_branch_type,
                                                        'branch_state_id': from_branch_state,
                                                        "ref": move.picking_id and move.picking_id.name,
                                                        "stock_move_id": move.id,
                                                        "move_type": 'entry',
                                                    }
                                                )
                                            new_account_move._post()
                                            new_account_move2 = AccountMove.sudo().create(
                                                    {
                                                        "journal_id": journal_id_to,
                                                        "line_ids": move_lines_from,
                                                        "company_id": move.company_id.id,
                                                        'date': date,
                                                        'branch_id': to_branch,
                                                        'branch_group_id': to_branch_group,
                                                        'branch_type_id': to_branch_type,
                                                        'branch_state_id': to_branch_state,
                                                        "ref": move.picking_id and move.picking_id.name,
                                                        "stock_move_id": move.id,
                                                        "move_type": 'entry',
                                                    }
                                                )
                                            new_account_move2._post()        
        return res
 

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

   
    branch_id = fields.Many2one('res.branch', string="Branch", related='move_id.branch_id',readonly=False, store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

