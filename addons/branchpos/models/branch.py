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

from odoo import api, fields, models, _, tools



class Branch(models.Model):
    _inherit = 'res.branch'

    pos_ids = fields.One2many('pos.config','branch_id',string='Branch POS',check_company=True,auto_join=True)


    def _compute_showin_pos(self):
        for record in self:
            poss_count = record.poss_count
            if poss_count == 0:
                record.showin_pos = False
            else:
                record.showin_pos = True

    showin_pos = fields.Boolean("show Branch",compute='_compute_showin_pos')


    poss_count = fields.Integer(
        'Number of POS', compute='_compute_poss_count',
        help="The number of POSs under this Branch")

    @api.depends('pos_ids')
    def _compute_poss_count(self):
        for rec in self:
            rec.poss_count = len(rec.pos_ids)



    def write(self, vals):
        branch = self.with_context(active_test=False)
        for branch in self:
                poss = self.env['pos.config'].with_context(active_test=False).search([('branch_id', '=', branch.id)])
                pos_ids = poss.filtered(lambda r: len(r.branch_id) > 0)
                for pos in pos_ids:
                    if 'active' in vals:
                        pos.write({'active': vals['active']})
        result = super(Branch, self).write(vals)
        return result



    def redirect_pos(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pos(s)',
            'view_mode': 'tree,form',
            'res_model': 'pos.config',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_pos_orders(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pos Orders',
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_pos_session(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pos Sessions',
            'view_mode': 'tree,form',
            'res_model': 'pos.session',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
    def redirect_pos_payments(self,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pos Payments',
            'view_mode': 'tree,form',
            'res_model': 'pos.payment',
            'domain': [('branch_id','=',self.id)],
            'target': 'current',
            'context': context,
        }
