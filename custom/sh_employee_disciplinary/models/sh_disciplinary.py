# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


# Sh disciplinary object


class ShDisciplinary(models.Model):
    _name = 'sh.disciplinary'
    _description = 'Disciplinary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Disciplinary Sequence', readonly=True,
                       required=True, copy=False, default='New')
    sh_employee_id = fields.Many2one(
        'hr.employee', string="Employee")
    sh_disciplinary_category = fields.Many2one(
        'sh.disciplinary.categories', string="Disciplinary Category")
    sh_action_category = fields.Many2one(
        'sh.disciplinary.categories', string="Action Category")
    sh_description = fields.Text('Comments')
    sh_emp_explaination = fields.Text('Employee Explaination')
    sh_action_explaination = fields.Text('Action Explaination')
    sh_attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting for Explanation'),
        ('submitted', 'Waiting For Action'),
        ('validate', 'Action Validated'),
        ('closed', 'Closed'),
    ], string='State', readonly=True, index=True, copy=False, default='draft')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)

    sh_contract_id = fields.Many2one(
        'hr.contract', string="Contract", store=True)

    sh_department_id = fields.Many2one(
        "hr.department", string="Department", store=True)
    sh_responsible_person = fields.Many2one(
        related="sh_employee_id.parent_id.user_id", string="Responsible Persons", store=True)

    first_contract_start_date = fields.Date("Contract Start Date")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sh.disciplinary') or 'New'
                result = super(ShDisciplinary, self).create(vals_list)
        return result

    def sh_reset_to_draft_button(self):
        self.state = 'draft'
        return {}

    def sh_post_disciplinary_button(self):
        if not self.sh_responsible_person:
            raise ValidationError(
                _("Please set Employee Manager this can't be empty. \nAs their role here is among the Responsible Persons for running the Disciplinary Flow."))
        self.state = 'explain'
        return {}

    def sh_submit_button(self):

        if not self.sh_emp_explaination:
            raise UserError(_('Please give an Explanation..!'))
        self.state = 'submitted'
        return {}

    def sh_validate_button(self):

        if not self.sh_action_category and not self.sh_action_explaination:
            raise UserError(_('Please take Appropriate Action..!'))

        self.state = 'validate'

    def sh_close_button(self):
        self.state = 'closed'
        return {}

    @api.onchange('sh_employee_id')
    def onchange_sh_employee_id(self):
        self.sh_department_id = False
        self.sh_contract_id = False
        if self.sh_employee_id and self.sh_employee_id.department_id:
            self.sh_department_id = self.sh_employee_id.department_id
        if self.sh_employee_id.sudo().first_contract_date:
            first_contract = self.env['hr.contract'].sudo().search(
                [('date_start', '=', self.sh_employee_id.sudo().first_contract_date), ('employee_id', '=', self.sh_employee_id.id)])
            if first_contract:
                self.sh_contract_id = first_contract.sudo().id

    @api.onchange('sh_contract_id')
    def onchange_sh_contract_id(self):
        self.first_contract_start_date = False
        if self.sh_contract_id and self.sh_contract_id.sudo().date_start:
            self.first_contract_start_date = self.sh_contract_id.sudo().date_start
