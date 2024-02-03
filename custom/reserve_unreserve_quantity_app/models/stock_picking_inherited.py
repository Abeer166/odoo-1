# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'

    def action_open_reserve_wizard(self):

        return {
            'name': _('Reserve Unreserve Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'reserve.unreserve.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }
