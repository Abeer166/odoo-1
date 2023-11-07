from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class ShiftType(models.Model):
    _name = "shift.type"
    _description = "shift.type"

    name = fields.Char(required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('shift_id')
    def _onchange_shift(self):
        if self.shift_id:
            self.resource_calendar_id = self.shift_id.calender_id and self.shift_id.calender_id.id   

    shift_id = fields.Many2one("hr.shift", compute='_compute_shift_id', search='_search_shift_id')

    def _compute_shift_id(self):
        today = date.today()
        for emp in self:
            allocation_id = self.env['shift.allocation'].search([
                ('employee_id', '=', emp.id),
                ('date_from','<=', today), ('date_to', '>=', today),
                ('state', '=', 'in_progress'),
            ], limit=1) 
            emp.shift_id = allocation_id and allocation_id.shift_id.id or False

    def _search_shift_id(self, operator, value):
        today = date.today()

        domain = [('date_from','<=', today), ('date_to', '>=', today)]
        if operator in ('ilike', 'not ilike'):
            domain.append(('shift_id.name', operator, value))
        if operator in ('=', '!=', 'in', 'not in'):
            domain.append(('shift_id', operator, value))

        allocation_ids = self.env['shift.allocation'].search(domain)
        set_employee = allocation_ids.mapped('employee_id')
        not_set_employee = self.env['hr.employee'].search([('id', 'not in', set_employee.ids)])
        if set_employee and operator in ('!=', '=', 'ilike', 'not ilike', 'in', 'not on'):
            return [('id', 'in', set_employee.ids)]

        if not allocation_ids and not set_employee:
            allocation_ids = self.env['shift.allocation'].search([('date_from','<=', today), ('date_to', '>=', today)])
            set_employee = allocation_ids.mapped('employee_id')
            not_set_employee = self.env['hr.employee'].search([('id', 'not in', set_employee.ids)]) 
            return [('id', 'in', not_set_employee.ids)]
        return []

class ShiftAllocation(models.Model):
    _name = "shift.allocation"
    _description = "shift .allocation"
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    date_from = fields.Date()
    date_to = fields.Date()
    shift_id = fields.Many2one("hr.shift")
    employee_id = fields.Many2one("hr.employee")
    state = fields.Selection([('draft', 'Draft'),('in_progress', 'Done'),('cancel','Cancel')], default='draft')
    description = fields.Text()
    shift_type_id = fields.Many2one('shift.type')
    
    @api.onchange('shift_id')
    def _onchange_shift(self):
        if self.shift_id:
            self.date_from = self.shift_id.date_from
            self.date_to = self.shift_id.date_to

    @api.constrains('employee_id','date_from','date_to')
    def check_validation(self):
        # Overlapping Not working
        for rec in self:
            match_shift = self.env['shift.allocation'].search([
                ('id', '!=', rec.id),
                ('employee_id', '=', rec.employee_id.id),
                ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_to)
            ])
            if match_shift:
                raise ValidationError(_('Shift allocation are already defined for these dates'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.shift.allocation') or '/'
        return super(ShiftAllocation, self).create(vals)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.employee_id and rec.shift_id:
                name = "%s - %s" % (rec.employee_id.name, rec.shift_id.name)
            res += [(rec.id, name)]
        return res

    def button_in_progress(self):
        self.write({'state' :'in_progress'})

    def button_closed(self):
        self.write({'state': 'cancel'})

class HrShift(models.Model):
    _name = 'hr.shift'
    _description = "hr.shift"

    name = fields.Char(required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    calender_id = fields.Many2one('resource.calendar',string="Working Hours")
    shift_type_id = fields.Many2one('shift.type')
    attendance_hours = fields.Integer(string='Attendace Hours', default=1)
    on_time = fields.Integer(string='On Time(In Minutes)', default=10)

    @api.constrains('shift_type_id','date_from','date_to')
    def check_validation(self):
        for rec in self:
            shift = self.env['hr.shift'].search([
                ('id', '!=', rec.id),
                ('shift_type_id', '=', rec.shift_type_id.id),
                ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_to)
            ])
            if shift: 
                raise ValidationError(_('Shift allocation are already defined for these dates'))
