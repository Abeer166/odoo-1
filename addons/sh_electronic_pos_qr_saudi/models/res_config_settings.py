# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_display_qr_code = fields.Boolean(related="pos_config_id.display_qr_code",string='Show QR Code In Receipt', readonly=False)
    pos_qr_code_setting = fields.Selection(
        related="pos_config_id.qr_code_setting", string='QR Code Position', readonly=False)
    pos_sh_display_arabic_name = fields.Boolean(related="pos_config_id.sh_display_arabic_name",
        string='Display Product Arabic Name', readonly=False)
    pos_sh_display_arabic_address = fields.Boolean(related="pos_config_id.sh_display_arabic_address",
        string='Display Arabic Address', readonly=False)
    pos_qr_code_height = fields.Integer(related="pos_config_id.qr_code_height",
        string='QR Code Size \n (Width x Height)', readonly=False)
    pos_qr_code_width = fields.Integer(related="pos_config_id.qr_code_width",string='QR code Width', readonly=False)
    pos_show_return_order_ref = fields.Boolean(related="pos_config_id.show_return_order_ref",string='Show Return Order Reference', readonly=False)
        