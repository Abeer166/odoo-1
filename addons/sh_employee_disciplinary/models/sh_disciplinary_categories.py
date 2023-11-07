# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models

# sh.disciplinary.categories object


class ShDisciplinaryCategories(models.Model):
    _name = 'sh.disciplinary.categories'
    _description = 'Sh Disciplinary Categories'

    name = fields.Char(string='Disciplinary Categories', required=True)
    sh_category_type = fields.Selection(
        [('disciplinary', 'Disciplinary Category'), ('action', 'Action Category')], string="Category Type", required=True)
