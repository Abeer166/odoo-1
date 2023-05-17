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


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)


    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for Product in self:
            Product.branches_count = branches_count

    def _compute_is_branch(self):
        company = self.env.company
        if company.is_branch:
            self.is_branch = True
        else:
            self.is_branch = False


    is_branch = fields.Boolean(default='_compute_is_branch')



    branch_ids = fields.Many2many(comodel_name="res.branch", relation="product_branch_rel", column1="product_id", column2="branch_id",string='Share To Branches', readonly=False, tracking=True)

    
