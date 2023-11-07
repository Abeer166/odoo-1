# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_qr_elements(self):
        return [
            (0, 0, {'fields_id': 'pos_reference', 'label': '#'}),
            (0, 0, {'fields_id': 'date_order', 'label': 'Date'}),
            (0, 0, {'fields_id': 'company_name', 'label': 'Seller'}),
            (0, 0, {'fields_id': 'customer_vat', 'label': 'Customer VAT'}),
            (0, 0, {'fields_id': 'price_included_taxt_total', 'label': 'Total Amount (Included VAT)'}),
            (0, 0, {'fields_id': 'amount_before_tax',
             'label': 'Amount Before VAT'}),
            (0, 0, {'fields_id': 'amount_vat', 'label': 'VAT Amount'}),
        ]

    display_qr_code = fields.Boolean(string='Show QR Code In Receipt')
    qr_code_setting = fields.Selection(
        [('top', 'Top'), ('bottom', 'Bottom')], string='QR Code Position', default='bottom')
    sh_display_arabic_name = fields.Boolean(
        string='Display Product Arabic Name',)
    sh_display_arabic_address = fields.Boolean(
        string='Display Arabic Address',)
    qr_code_height = fields.Integer(
        string='QR Code Size \n (Width x Height)', default=120)
    qr_code_width = fields.Integer(string='QR code Width', default=120)
    show_return_order_ref = fields.Boolean(string='Show Return Order Reference')
