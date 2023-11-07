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

from odoo.exceptions import UserError, ValidationError


from odoo.tools.misc import clean_context

from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby
from odoo.tools import float_compare

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    branch_id = fields.Many2one("res.branch", string='Branch',related='location_id.branch_id', store=True )
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type',string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


    @api.onchange('product_id')
    def onchange_product_id_loc(self):
        if self.env.company.is_branch and not self._is_inventory_mode():
            return
        if self.env.company.is_branch and self._is_inventory_mode():
            if self.location_id and not self.location_id.branch_id:
                raise ValidationError(_("please define branch to Stock Location %s") % (self.location_id.name))
            if self.product_id:
                location = self.env['stock.location'].search([('usage', 'in', ['internal', 'transit']),('branch_id.user_ids','=', self.env.user.id)])
                self.location_id = False
                if self.product_id and location:
                    self.location_id = location[0].id
                return {'domain': {'location_id': [('id', 'in', location.ids)]}}
            else:
                location = self.env['stock.location'].search([('usage', 'in', ['internal', 'transit'])])
                self.location_id = False
                if self.product_id and location:
                    self.location_id = location[0].id
                return {'domain': {'location_id': [('id', 'in', location.ids)]}}


    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.env.company.is_branch and not self._is_inventory_mode():
            return
        if self.env.company.is_branch and not self._is_inventory_mode():
            if self.location_id and self.location_id.branch_id:
                self.branch_id = self.location_id.branch_id.id
                if self.branch_id:
                    products = self.env['product.template'].search([('type', '=', 'product'),'|',('branch_ids', '=',self.branch_id.id),('branch_ids', '=',False)])
                    self.product_id = False
                    if self.location_id and products:
                        self.product_id = products[0].id
                    return {'domain': {'product_id': [('id', 'in', products.ids)]}}
                else:
                    raise ValidationError(_("please define branch to Stock Location %s") % (self.location_id.name))

  
  
    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, out=False)
        if self.is_branch and self.location_id.usage =='internal':
            if not self.location_id.branch_id:
                raise ValidationError(_("please define branch to Stock Location %s") % (self.location_id.name))
            if self.location_id.branch_id:
                res.update({"branch_id": self.branch_id.id})
        return res

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when editing a quant in `inventory_mode`."""
        res = super()._get_inventory_fields_write()
        res += ['branch_id','branch_type_id','branch_group_id','branch_state_id']
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    is_branch = fields.Boolean(related='company_id.is_branch')

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        if self.is_branch:
            res.update({'warehouse_id': self.picking_type_id.warehouse_id.id,
             'branch_id': self.picking_type_id.branch_id.id,})
        return res


class StockWarehouseOrderPoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    branch_id = fields.Many2one("res.branch", string='Branch', related='warehouse_id.branch_id',store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type',string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


    @api.constrains("branch_id", "warehouse_id", "location_id")
    def _check_location(self):
        for rec in self:
            if (
                rec.warehouse_id
                and rec.location_id
                and rec.warehouse_id.branch_id
                != rec.location_id.branch_id
            ):
                raise UserError(
                    _(
                        "Configuration Error. The Branch of the "
                        "Warehouse and the Location must be the same. "
                    )
                )

class ProductReplenish(models.TransientModel):
    _inherit = "product.replenish"

    branch_id = fields.Many2one("res.branch", string='Branch', related='warehouse_id.branch_id',store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type',string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )


    # def launch_replenishment(self):
    #     uom_reference = self.product_id.uom_id
    #     self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
    #     try:
    #         self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
    #             self.env['procurement.group'].Procurement(
    #                 self.product_id,
    #                 self.quantity,
    #                 uom_reference,
    #                 self.warehouse_id.lot_stock_id,  # Location
    #                 _("Manual Replenishment"),  # Name
    #                 _("Manual Replenishment"),  # Origin
    #                 self.warehouse_id.company_id,
    #                 self._prepare_run_values()  # Values
    #             )
    #         ])
    #     except UserError as error:
    #         raise UserError(error)

    def _prepare_run_values(self):
        replenishment = self.env['procurement.group'].create({})

        values = {
            'warehouse_id': self.warehouse_id,
            'branch_id': self.branch_id,
            'route_ids': self.route_ids,
            'date_planned': self.date_planned,
            'group_id': replenishment,
        }
        return values
class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def _default_location_id(self):
        if self.location_id and not self.picking_id:
            if self.location_id and not self.picking_id:
                self.branch_id =  self.location_id.branch_id.id
        if self.picking_id and self.location_id:
            if self.location_id and self.picking_id:
                self.branch_id =  self.picking_id.branch_id.id 
  
    branch_id = fields.Many2one('res.branch', string="Branch",default=_default_location_id,store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

  
    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.is_branch and self.location_id and not self.location_id.branch_id:
            raise UserError(_("Please Define Branch to Selected Stock Location"))
        if self.location_id and not self.picking_id:
            if self.location_id and not self.picking_id:
                self.branch_id =  self.location_id.branch_id.id
        if self.picking_id and self.location_id:
            if self.location_id and self.picking_id:
                self.branch_id =  self.picking_id.branch_id.id 
  
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.is_branch and self.location_id and not self.location_id.branch_id:
            raise UserError(_("Please Define Branch to Selected Stock Location"))
        if self.location_id and not self.picking_id:
            if self.location_id and not self.picking_id:
                self.branch_id =  self.location_id.branch_id.id
        if self.picking_id and self.location_id:
            if self.location_id and self.picking_id:
                self.branch_id =  self.picking_id.branch_id.id 
        res = super(StockScrap, self)._onchange_product_id()


    def _prepare_move_values(self):
        res = super()._prepare_move_values()
        res.update(
            {
                "branch_id": self.branch_id.id
            }
        )
        return res


class BranchStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    branch_id = fields.Many2one('res.branch', readonly=True, store=True,related='stock_move_id.branch_id')
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )
