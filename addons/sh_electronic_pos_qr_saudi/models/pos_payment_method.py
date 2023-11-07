# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class PaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    sh_payment_method_arabic_name = fields.Char(
        string='Payment Method Arabic Name')
        