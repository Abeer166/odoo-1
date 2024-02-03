# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockLocationInherit(models.Model):
    _inherit = "stock.location"

    so_count = fields.Float('Sale Order', compute="compute_no_of_so")

    def action_reserve_quantity(self):
        for rec in self:
            quant_ids = rec.env['stock.quant'].sudo().search([('location_id', '=', rec.id)])
            for quant_id in quant_ids:
                quant_id.reserved_quantity = quant_id.old_qty
                quant_id.old_qty = 0

    def action_unreserve_quantity(self):
        for rec in self:
            quant_ids = rec.env['stock.quant'].sudo().search([('location_id', '=', rec.id)])
            for quant_id in quant_ids:
                quant_id.old_qty = quant_id.reserved_quantity
                quant_id.reserved_quantity = 0

                # move_line_ids = rec.env['stock.move.line'].search([('state', 'in', ['assigned', 'partially_assigned']),
                #                                                    ('product_id', '=', quant_id.product_id.id),
                #                                                    '|',
                #                                                    ('location_id', '=', quant_id.location_id.id),
                #                                                    ('location_dest_id', '=', quant_id.location_id.id),
                #                                                    ('lot_id', '=', quant_id.lot_id.id),
                #                                                    '|',
                #                                                    ('package_id', '=', quant_id.package_id.id),
                #                                                    ('result_package_id', '=', quant_id.package_id.id),
                #                                                    ])
                # for line_id in move_line_ids:
                #     line_id.move_id._do_unreserve()
                #     line_id.move_id.old_qty = line_id.move_id.reserved_availability


class StockQuantInherit(models.Model):
    _inherit = "stock.quant"

    old_qty = fields.Float(string="Old Reserve Quantity")
