# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    sh_arabic_name = fields.Char(string='Arabic Name')
    arabic_street = fields.Char(string='Arabic Street...')
    arabic_street2 = fields.Char(string='Arabic Street2...')
    arabic_city = fields.Char(string='Arabic City')
    arabic_zip = fields.Char(string='Arabic Zip')
    