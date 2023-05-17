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
from odoo.exceptions import ValidationError,UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'
 
    def _default_branch_id(self):
        if self.company_id and self.company_id.is_branch:
            if self.env.user.branch_id:
                self.branch_id = self.env.user.branch_id.id
            if not self.env.user.branch_id:
                user = self.env.user.id
                branches = self.env['res.branch'].search([('user_ids', '=', user),('company_id', '=', self.env.company.id)], limit=1)
                return branches

    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    branch_id = fields.Many2one("res.branch", default=_default_branch_id,store=True)
    is_branch = fields.Boolean(related='company_id.is_branch')



    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id and self.location_id.branch_id and self.usage=='internal':
            self.branch_id =  self.location_id.branch_id.id
        if self.location_id and not self.location_id.branch_id and self.usage=='internal':
            raise UserError(_("Please Define Branch to Selected Stock Location"))

  
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.location_id.branch_id:
            if self.branch_id.id != self.location_id.branch_id.id:
                raise UserError(_("Configuration Error \n You must select same branch on a location as a warehouse configuration"))

    location_acc_valuation = fields.Many2one(
        'account.account', 'Stock Valuation Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product, this account will hold the current value of the products.""",)
    location_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0])]", check_company=True,
        help="When doing automated inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed.")
