# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models



class res_company_inherit(models.Model):
    _inherit = 'res.company'

    attachment_restriction = fields.Boolean(string="Only share own Attachments")
