#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    building_no = fields.Integer(string="Building no", help="Building No")
    district = fields.Char(string="District", help="District")
    code = fields.Char(string="Code", help="Code")
    additional_no = fields.Char(string="Additional no", help="Additional No")
    other_id = fields.Char(string="Other ID", help="Other ID")

    vat = fields.Char(readonly=True)
    @api.constrains('vat')
    def _check_vat(self):
        for record in self:
            if len(record.vat) != 15:
                raise ValidationError('يجب ان تتكون خانة الرقم الضريبي من ١٥ رقم ')

    def test(self):

        pass
