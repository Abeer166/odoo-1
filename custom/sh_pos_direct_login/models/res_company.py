# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    account_default_pos_receivable_account_id = fields.Many2one(string="account_default_pos_receivable_account_id")
