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

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    def _default_branch_id(self):
        if self.company_id and self.company_id.is_branch:
            if self.env.user.branch_id:
                self.branch_id = self.env.user.branch_id.id
            if not self.env.user.branch_id:
                user = self.env.user.id
                branches = self.env['res.branch'].search([('user_ids', '=', user),('company_id', '=', self.env.company.id)], limit=1)
                return branches
            else:
                self._onchange_company_id()

    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    branch_id = fields.Many2one("res.branch", default=_default_branch_id,store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')


                
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.company_id.is_branch:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if self.env.user.branch_id:
                self.branch_id = self.env.user.branch_id.id
            if not self.env.user.branch_id and len(branches) > 0:
                self.branch_id = branches[0]
            return {'domain': {'branch_id': [('id', 'in', branches)]}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            lot_stock_id = self.env['stock.location'].search([('id', '=', self.lot_stock_id.id)])
            if lot_stock_id:
                lot_stock_id.update({'branch_id': self.branch_id.id})

            view_location_id = self.env['stock.location'].search([('id', '=', self.view_location_id.id)])
            if view_location_id:
                view_location_id.update({'branch_id': self.branch_id.id})

            wh_input_stock_loc_id = self.env['stock.location'].search([('id', '=', self.wh_input_stock_loc_id.id)])
            if wh_input_stock_loc_id:
                wh_input_stock_loc_id.update({'branch_id': self.branch_id.id})

            wh_output_stock_loc_id = self.env['stock.location'].search([('id', '=', self.wh_output_stock_loc_id.id)])
            if wh_output_stock_loc_id:
                wh_output_stock_loc_id.update({'branch_id': self.branch_id.id})

            wh_pack_stock_loc_id = self.env['stock.location'].search([('id', '=', self.wh_pack_stock_loc_id.id)])
            if wh_output_stock_loc_id:
                wh_output_stock_loc_id.update({'branch_id': self.branch_id.id})
                
            wh_qc_stock_loc_id = self.env['stock.location'].search([('id', '=', self.wh_qc_stock_loc_id.id)])
            if wh_qc_stock_loc_id:
                wh_qc_stock_loc_id.update({'branch_id': self.branch_id.id})
  
    @api.model_create_multi
    def create(self, vals_list):
        warehouses = super().create(vals_list)
        for warehouse, vals in zip(warehouses, vals_list):
            view_location_id = self.env['stock.location'].browse(vals.get('view_location_id'))
            (view_location_id | view_location_id.with_context(active_test=False).child_ids).write({'branch_id': warehouse.branch_id.id})
        return warehouses


    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('branch_id', False):
            branch_id = self._context.get('branch_id', False)
            warehouses = self.env['stock.warehouse'].search([('branch_id', '=', branch_id)])
            if len(warehouses) > 0:
                args.append(('id', 'in', warehouses.ids))
            else:
                args.append(('id', '=', []))
        return super(Warehouse, self).name_search(name, args=args, operator=operator, limit=limit)

