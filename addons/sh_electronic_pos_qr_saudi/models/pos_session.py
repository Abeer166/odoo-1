# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()

        if 'sh.pos.config.qr.elements' not in result:
            result.append('sh.pos.config.qr.elements')
        return result

    def _loader_params_sh_pos_config_qr_elements(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_sh_pos_config_qr_elements(self, params):
        return self.env['sh.pos.config.qr.elements'].search_read(**params['search_params'])

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['sh_arabic_name'])
        return result

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend(['sh_arabic_name'])
        result['search_params']['fields'].extend(['street'])
        result['search_params']['fields'].extend(['city'])
        result['search_params']['fields'].extend(['zip'])
        result['search_params']['fields'].extend(['arabic_street'])
        result['search_params']['fields'].extend(['arabic_street2'])
        result['search_params']['fields'].extend(['arabic_city'])
        result['search_params']['fields'].extend(['arabic_zip'])
        return result

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].extend(['sh_cr_no'])
        return result

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].extend(['sh_payment_method_arabic_name'])
        return result