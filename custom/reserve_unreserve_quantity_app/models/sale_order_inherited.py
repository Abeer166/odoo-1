# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    po_count = fields.Float('Purchase Order', compute="compute_no_of_po")

    def compute_no_of_po(self):
        for rec in self:
            purchase_ids = rec.env['purchase.order'].search([('origin', '=', self.name)])
            rec.po_count = len(purchase_ids)

    def action_view_purchase_order(self):
        purchase_ids = self.env['purchase.order'].search([('origin', '=', self.name)])
        xml_id = 'purchase.purchase_order_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'purchase.purchase_order_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Purchase'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'purchase.order',
            'domain': [('id', 'in', purchase_ids.ids)],
            'context': {'create': 0, 'edit': 0},
            'type': 'ir.actions.act_window',
        }

    def action_confirm(self):
        result = super(SaleOrderInherit, self).action_confirm()
        if self.user_has_groups('reserve_unreserve_quantity_app.group_manage_res_unres'):
            po_line = []
            for lines in self.order_line:
                po_line.append(((0, 0, {
                    'name': lines.name,
                    'display_name': lines.product_id.name,
                    'price_unit': lines.price_unit,
                    'product_qty': lines.product_uom_qty,
                    'product_uom': lines.product_id.uom_id.id,
                    'product_id': lines.product_id.id or False,
                    'taxes_id': [(6, 0, lines.tax_id.ids)],
                    'date_planned': lines.order_id.date_order,
                    'date_order': lines.order_id.date_order,
                })))
            vals = {
                'state': 'draft',
                'partner_id': self.partner_id.id,
                'order_line': po_line,
                'origin': self.name,
            }
            self.env['purchase.order'].create(vals)
        return result
