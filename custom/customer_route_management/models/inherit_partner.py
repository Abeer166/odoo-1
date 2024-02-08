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

    #adding map from google_maps_partner to rout line
    def open_map(self):
        super(ResPartner, self).open_map()

    #we inhirit action_view_partner_invoices function and we add a new domain which is 'payment_state', '!=', 'paid'
    def action_view_partner_invoices(self):
        self.ensure_one()
        action = super(ResPartner, self).action_view_partner_invoices()

        # Add your custom domain here
        custom_domain = [('payment_state', '!=', 'paid')]

        # Check if 'domain' key exists in action and add the custom domain
        if 'domain' in action:
            action['domain'].extend(custom_domain)
        else:
            action['domain'] = custom_domain

        return action









