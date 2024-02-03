# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    so_count = fields.Float('Sale Order', compute="compute_no_of_so")

    def compute_no_of_so(self):
        for rec in self:
            sale_ids = rec.env['sale.order'].search([('name', '=', self.origin)])
            rec.so_count = len(sale_ids)

    def action_view_sale_order(self):
        xml_id = 'sale.view_quotation_tree_with_onboarding'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'sale.view_order_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'sale.order',
            'domain': [('name', '=', self.origin)],
            'context': {'create': 0, 'edit': 0},
            'type': 'ir.actions.act_window',
        }
