# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    #_order = 'sequence'

    locations = fields.Many2one('route.lines', string='Location')
    sequence = fields.Integer(default=10)
    name=fields.Char("أسم العميل")

    statuss = fields.Boolean(string="الحالة")

    def get_all_dues(self):
        query = """select name,invoice_date_due,amount_residual_signed from account_move where partner_id in
                (select id from res_partner where id =%s or parent_id=%s) and state != 'draft' and 
                amount_residual_signed != 0
                order by create_date"""
        self.env.cr.execute(query, [self.id, self.id])
        list = self.env.cr.dictfetchall()
        return list
