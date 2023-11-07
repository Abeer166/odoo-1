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
    
 
    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branches_count = fields.Integer(compute='_compute_branches_count', string="Number of branches", default=_branches_count)
    branch_id = fields.Many2one('res.branch', string='Default Branch for current company',compute='_compute_branch_id')
    branch_ids = fields.Many2many('res.branch',compute='_compute_branch_ids',string='Allowed Branches For Current Company')
    branches = fields.Many2many( comodel_name="res.branch", relation="res_user_branch_rel", column1="user_id", column2="branch_id",string='Allowed Branches')
    default_branches = fields.One2many('users.default.branch', 'user_ids',string="Default Branches Per each Allowed Company",readonly=False, context={'user_preference': True})
    branch_id2 = fields.Many2one(related='default_branches.branch_id', string='Default Branch',readonly=False, context={'user_preference': True})

    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for user in self:
            user.branches_count = branches_count
   
    @api.onchange('company_ids')
    def _compute_is_branch(self):
        company = self.env.company
        if company.is_branch:
            self.is_branch = True
        else:
            self.is_branch = False

        

    is_branch = fields.Boolean(compute='_compute_is_branch')


    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['branch_id','default_branches','branch_id2']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['branch_id','default_branches','branch_id2']


    @api.onchange('branch_id2')
    def _onchange_branch_id2(self):
        if self.branch_id2:
            default_branches = self.env['users.default.branch'].search([('user_ids', '=', self.env.user.id),'|',('company_id', '=', False),('company_id', '=', self.env.company.id)])
            if len(default_branches) == 0:
                self.env['users.default.branch'].sudo().create({'branch_id': self.branch_id2.id,'company_id': self.env.company.id,'user_ids': self.env.user.id})

    def write(self, values):
        if 'default_branches' in values or 'branch_id2' in values or 'branch_ids' in values or'branch_id' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
        if any(key.startswith('context_') or key in ('default_branches', 'branch_id2', 'branch_id','branch_ids') for key in values):
            self.context_get.clear_cache(self)
        user = super(users, self).write(values)
        return user

    def _compute_branch_ids(self):
        if self.branches:
            self.branch_ids = self.branches.filtered(lambda m: m.company_id.id == self.env.company.id).ids
        else:
            self.branch_ids = False

    def _compute_branch_id(self):
        if self.branch_id2:
            self.branch_id = self.branch_id2.id
        else:
            self.branch_id = False


class UsersDefaultBranches(models.Model):
    _name = 'users.default.branch'
    _description = 'users default branch per company'
    _rec_name = 'branch_id'
    _check_company_auto = True


    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch', string='Default Branch',)
    user_ids = fields.Many2one('res.users',index=True, required=True, auto_join=True,string='User',default=lambda self: self.env.user )



    _sql_constraints = [
        ('branch_idcompany_id_uniq', 'unique (company_id,user_ids)', "The default branch already exists with this user or default branch defind in this company before so ask admin to update from 'Users Default Branches screen'"),
    ]


    @api.onchange('user_ids')
    def _onchange_user_ids(self):
        if self.user_ids:
            branches_in_this_company = self.env['res.branch'].search([('user_ids', '=', self.user_ids.id),'|',('company_id', '=', False),('company_id', '=', self.env.company.id)])
            if branches_in_this_company:
                user = self.env.user.id
                branches = self.env['res.branch'].search([('user_ids', '=', self.user_ids.id),'|',('company_id', '=', False),('company_id', '=', self.env.company.id)])
                if branches:
                    self.branch_id = branches[0].id
            else:
                raise UserError(_("the selected user not allowed to any branch at this company"))

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches_in_this_company = self.env['res.branch'].search([('user_ids', '=', self.user_ids.id),'|',('company_id', '=', False),('company_id', '=', self.env.company.id)])
            if branches_in_this_company:
                user = self.env.user.id
                branches = self.env['res.branch'].search([('user_ids', '=', self.user_ids.id),'|',('company_id', '=', False),('company_id', '=', self.env.company.id)])
                if branches:
                    self.branch_id = branches[0].id
            else:
                raise UserError(_("the selected user not allowed to any branch at this company"))
