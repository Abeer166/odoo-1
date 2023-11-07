from odoo import models, fields, api, _

class AllocationWizard(models.TransientModel):
	_name = "allocation.wizard"
	_description = "allocation.wizard"

	description = fields.Text()
	date_from = fields.Date()
	date_to  = fields.Date()
	shift_id = fields.Many2one("hr.shift",required=True)
	employee_ids = fields.Many2many("hr.employee",required=True)
	
	@api.model
	def default_get(self, fields):
		vals = super(AllocationWizard, self).default_get(fields)
		active_ids = self.env.context.get('active_ids')
		vals['employee_ids'] = active_ids
		return vals

	def bulk_allocation(self):
		vals = {
			'date_from': self.date_from,
			'date_to': self.date_to,
			'shift_id': self.shift_id.id,
			'shift_type_id': self.shift_id.shift_type_id and self.shift_id.shift_type_id.id,
			'description': self.description,
			'state': 'in_progress',
		}
		for emp in self.employee_ids:
			vals['employee_id'] = emp.id
			self.env['shift.allocation'].create(vals)
		# link with emp
		self.employee_ids.write({
			'resource_calendar_id': self.shift_id.calender_id and self.shift_id.calender_id.id
		})

