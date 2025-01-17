#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    namee = fields.Char(string=" name", related='partner_id.name')
    street = fields.Char(string=" name", related='partner_id.street')

    building_no = fields.Integer(string="Building no", related='partner_id.building_no', help="Building No")
    district = fields.Char(string="District", related='partner_id.district', help="District")
    code = fields.Char(string="Code", related='partner_id.code', help="Code")
    additional_no = fields.Char(string="Additional no", related='partner_id.additional_no', help="Additional No")
    other_id = fields.Char(string="Other ID", related='partner_id.other_id', help="")
