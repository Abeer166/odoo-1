
# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    sh_disciplinary_record_count = fields.Integer(
        'Disciplinary', compute='_compute_disciplinary_record')

    sh_disciplinary_record_ids = fields.Many2many('sh.disciplinary')

    def _compute_disciplinary_record(self):
        if self:
            for rec in self:
                rec.sh_disciplinary_record_count = 0
                record = self.env['sh.disciplinary'].search(
                    [('sh_employee_id', '=', self.id)])
                self.sh_disciplinary_record_ids = [(6, 0, record.ids)]
                if record:
                    rec.sh_disciplinary_record_count = len(record.ids)

    def action_view_disciplinary_record(self):
        self.ensure_one()
        record = self.env['sh.disciplinary'].search(
            [('sh_employee_id', '=', self.id)])
        if record:
            return {
                'name': 'Disciplinary Record',
                'res_model': 'sh.disciplinary',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.sh_disciplinary_record_ids.ids)],
                'target': 'current'
            }
