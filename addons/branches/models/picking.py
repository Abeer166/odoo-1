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

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for picking in self:
            if picking.company_id.is_branch:
                if picking.picking_type_id and picking.picking_type_id.branch_id:
                    picking.branch_id = picking.picking_type_id.branch_id
                    if picking.branch_id:
                        picking.move_ids.write({'branch_id': picking.branch_id.id,'branch_group_id': picking.branch_id.group_id.id,'branch_type_id': picking.branch_id.type_id.id,'branch_state_id': picking.branch_id.state_id.id})
                        picking.move_line_ids.write({'branch_id': picking.branch_id.id,'branch_group_id': picking.branch_id.group_id.id,'branch_type_id': picking.branch_id.type_id.id,'branch_state_id': picking.branch_id.state_id.id})
                if picking.picking_type_id and not picking.picking_type_id.branch_id:
                    raise UserError(_('Please select branch in %s Operation Type.' % (self.picking_type_id.name)))
        return res


    branch_id = fields.Many2one("res.branch",related='picking_type_id.branch_id',store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )



    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.is_branch and self.picking_type_id and not self.picking_type_id.branch_id:
            raise UserError(_('Please select branch in %s Operation Type.' % (self.picking_type_id.name)))


  
class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    branch_id = fields.Many2one('res.branch', related='warehouse_id.branch_id', store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

