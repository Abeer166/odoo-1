# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class Qr_elements(models.Model):
    _name = 'sh.pos.config.qr.elements'
    _description = 'pos config qr elements'

    fields_id = fields.Selection(
        [('pos_reference', 'Receipt Number'), ('create_date', 'Created on'), ('write_date', 'Last Update on'), ('amount_paid', 'Amount Paid'), ('amount_return', 'Amount Change'), ('date_order', 'Date'), ('customer_vat', 'Customer VAT'), ('sh_cr_no', 'Customer CR No.'), ('price_total', 'Total Price'), ('sequence_number', 'Sequence Number'), ('amount_before_tax', 'Amount Before VAT'), ('price_included_taxt_total', 'Total Amount (Included VAT)'), ('config_id', 'Point of Sale'), ('amount_vat', 'VAT Amount'), ('partner_id', 'Customer'), ('company_name', 'Seller'), ('company_vat_no', 'Company VAT No'), ('company_cr_no', 'Company CR No')])
    label = fields.Char(string='Label')
    custom_field = fields.Many2one('pos.config', 'field')

    @api.onchange('fields_id')
    def _onchange_field(self):
        selections = self.fields_get()["fields_id"]["selection"]
        value = next((v[1] for v in selections if v[0]
                     == self.fields_id), self.fields_id)
        self.label = value
