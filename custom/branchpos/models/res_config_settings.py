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

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
 
   

    pos_branch_id = fields.Many2one(related='pos_config_id.branch_id', readonly=False, string="Branch(PoS)")
    pos_branch_user_id = fields.Many2many(related='pos_config_id.branch_user_id', readonly=False, string="Allowed Users (PoS)")
    pos_branch_name = fields.Char(string="POS Branch Name", related='pos_config_id.branch_name',readonly=False)
    pos_branch_email = fields.Char(string="POS Email",related='pos_config_id.branch_email', readonly=False)
    pos_branch_phone = fields.Char(string="POS Phone",related='pos_config_id.branch_phone', readonly=False)
    pos_branch_mobile = fields.Char(string="POS Mobile",related='pos_config_id.branch_mobile', readonly=False)


  
    @api.onchange('pos_branch_id')
    def _onchange_branch_id(self):
        for pos_config in self:
            branch_id = pos_config.pos_branch_id
            if branch_id:
                pos_config.pos_branch_name =  pos_config.pos_branch_id.name
                pos_config.pos_branch_phone =  pos_config.pos_branch_id.phone
                pos_config.pos_branch_email =  pos_config.pos_branch_id.email
                pos_config.pos_branch_mobile =  pos_config.pos_branch_id.mobile
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id),'|',('branch_id', '=', pos_config.pos_branch_id.id),('branch_id', '=', False)])
                journalinv = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id),'|',('branch_ids', '=', pos_config.pos_branch_id.id),('branch_ids', '=', False)])
                payment_methods = self.env['pos.payment.method'].search([('split_transactions', '=', False), ('company_id', '=', self.env.company.id),'|',('branch_ids', '=', pos_config.pos_branch_id.id),('branch_ids', '=', False)])
                journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id),'|',('branch_ids', '=', pos_config.pos_branch_id.id),('branch_ids', '=', False)])
                pos_config.pos_warehouse_id = False
                pos_config.pos_journal_id = False
                pos_config.pos_payment_method_ids = False
                pos_config.pos_invoice_journal_id = False
                if pos_config.pos_branch_id and warehouse:
                    pos_config.pos_warehouse_id = warehouse[0].id
                if pos_config.pos_branch_id and journalinv:
                    pos_config.pos_invoice_journal_id = journalinv[0].id
                if pos_config.pos_branch_id and journal:
                    pos_config.pos_journal_id = journal[0].id
                if pos_config.pos_branch_id and payment_methods:
                    pos_config.pos_payment_method_ids = payment_methods



    @api.onchange('pos_warehouse_id')
    def onchange_warehouse_id(self):
        if self.pos_warehouse_id:
            picking = self.env['stock.picking.type'].search([('warehouse_id', '=', self.pos_warehouse_id.id),('code', '=', 'outgoing')])
            self.pos_picking_type_id = False
            if self.pos_warehouse_id and picking:
                self.pos_picking_type_id = picking[0].id
            return {'domain': {'pos_picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            return {'domain': {'pos_picking_type_id': []}}
