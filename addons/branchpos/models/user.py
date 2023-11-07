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

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo.osv import expression
from odoo.service.db import check_super


class users(models.Model):
    _inherit = 'res.users'
    
 
    def _pos_count(self):
        return self.env['pos.config'].sudo().search_count([])

    pos_count = fields.Integer(compute='_compute_pos_count', string="Number of Alloweed POS", default=_pos_count)
    # pos_ids = fields.Many2many('pos.config','config_id',string='Allowed POS',domain="[('branch_id', '=', branch_ids)]" ,check_company=True,auto_join=True)
    pos_ids = fields.Many2many(string="Allowed POS", comodel_name="pos.config", relation="pos_config_user_rel",column1="user_id" , column2="config_id",check_company=True)

    def _compute_pos_count(self):
        pos_count = self._pos_count()
        for user in self:
            user.pos_count = pos_count
  

    def write(self, values):
        if 'pos_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
        if any(key.startswith('context_') or key in ('pos_ids') for key in values):
            self.context_get.clear_cache(self)
        user = super(users, self).write(values)
        return user
