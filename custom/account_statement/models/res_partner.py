# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.tools.float_utils import float_round as round
from odoo import api, fields, models, _
from datetime import datetime, time, date, timedelta
from dateutil.relativedelta import relativedelta
from lxml import etree
import base64
from odoo.exceptions import UserError
import re
from odoo import tools
import calendar


class account_move(models.Model):
	
	_inherit = 'account.move'
	_order = 'invoice_date_due'
	
	def _get_result(self):
		for aml in self:
			aml.result = 0.0

			if aml.is_outbound():
				sign = -1
			else:
				sign = 1

			aml.result = sign * (abs(aml.amount_total_signed) - abs(aml.credit_amount))
	
					
	def _get_credit(self):
		for aml in self:
			aml.credit_amount = 0.0
			aml.credit_amount = abs(aml.amount_total_signed) - abs(aml.amount_residual_signed)

	credit_amount = fields.Float(compute ='_get_credit',   string="Credit/paid")
	result = fields.Float(compute ='_get_result',   string="Balance") #'balance' field is not the same
	invoice_origin = fields.Char('Origin')
	is_set_statments = fields.Boolean(string='Set Staments')

class Res_Partner(models.Model):
	_inherit = 'res.partner'
	
	def _get_payment_amount_due_amt(self):
		current_date = datetime.now().date()
		for partner in self:
			partner.do_process_monthly_statement_filter(sts=None)
			partner.do_process_weekly_statement_filter()
			amount_due = 0.0
			amount_overdue = 0.0

			for aml in partner.balance_invoice_ids:
				if aml.company_id == partner.env.company:
					date_maturity = aml.invoice_date_due or aml.date
					amount_due += aml.result
					if date_maturity:
						if date_maturity <= current_date :
							amount_overdue += aml.result
			
			partner.payment_amount_due_amt = amount_due
			partner.payment_amount_overdue_amt = amount_overdue

	def _get_payment_amount_due_amt_supplier(self):
		current_date = datetime.now().date()
		for partner in self:
			partner.do_process_monthly_statement_supplier_filter(sts=None)
			partner.do_process_weekly_statement_filter()
			supplier_amount_due = 0.0
			supplier_amount_overdue = 0.0
			for aml in partner.supplier_invoice_ids:
				date_maturity = aml.invoice_date_due or aml.date
				supplier_amount_due += aml.result
				if (date_maturity <= current_date):
					supplier_amount_overdue += aml.result
			partner.payment_amount_due_amt_supplier = supplier_amount_due
			partner.payment_amount_overdue_amt_supplier =  supplier_amount_overdue


	def _get_monthly_payment_amount_due_amt(self):
		today = date.today()
		d = today - relativedelta(months=1)

		start_date = date(d.year, d.month,1)
		end_date = date(today.year, today.month,1) - relativedelta(days=1)
	
		company = self.env.user.company_id
		current_date = datetime.now().date()
		monthly_payment_amount_due_amt = 0.0
		monthly_payment_amount_overdue_amt = 0.0
		for partner in self:
			partner.do_process_monthly_statement_filter(sts=None)
			partner.do_process_weekly_statement_filter()
			monthly_amount_due_amt = 0.0
			monthly_amount_overdue_amt = 0.0
			if partner.monthly_statement_line_ids:
				for aml in partner.monthly_statement_line_ids:
					if aml.invoice_type == 'invoice':
						date_maturity = aml.invoice_date_due
						if date_maturity and (aml.invoice_date >= start_date and aml.invoice_date <= end_date):
							monthly_amount_due_amt += aml.result
							if date_maturity <= end_date:
								monthly_amount_overdue_amt += aml.result
					partner.monthly_payment_amount_due_amt = monthly_amount_due_amt
					partner.monthly_payment_amount_overdue_amt = monthly_amount_overdue_amt
			else:
				partner.monthly_payment_amount_due_amt = 0.0
				partner.monthly_payment_amount_overdue_amt = 0.0


	def _get_monthly_supplier_payment_amount_due_amt(self):
		today = date.today()
		d = today - relativedelta(months=1)
		start_date = date(d.year, d.month,1)
		end_date = date(today.year, today.month,1) - relativedelta(days=1)

		company = self.env.user.company_id
		current_date = datetime.now().date()
		for partner in self:
			partner.do_process_monthly_statement_supplier_filter(sts=None)
			partner.do_process_weekly_statement_supplier_filter()
			monthly_amount_due_amt = 0.0
			monthly_amount_overdue_amt = 0.0
			if partner.monthly_statement_line_ids:
				for aml in partner.monthly_statement_line_ids:
					if aml.invoice_type == 'bill':
						date_maturity = aml.invoice_date_due
						if date_maturity and (aml.invoice_date >= start_date and aml.invoice_date <= end_date):
							monthly_amount_due_amt += aml.result
							if date_maturity <= end_date:
								monthly_amount_overdue_amt += aml.result
					partner.monthly_payment_supplier_amount_due_amt = monthly_amount_due_amt
					partner.monthly_payment_supplier_amount_overdue_amt = monthly_amount_overdue_amt
			else:
				partner.monthly_payment_supplier_amount_due_amt = 0.0
				partner.monthly_payment_supplier_amount_overdue_amt = 0.0

	def _get_weekly_payment_amount_due_amt(self):
		company = self.env.user.company_id
		current_date = datetime.now().date()
		for partner in self:
			partner.do_process_monthly_statement_filter(sts=None)
			partner.do_process_weekly_statement_filter()
			weekly_amount_due_amt = 0.0
			weekly_amount_overdue_amt = 0.0
			if partner.weekly_statement_line_ids:
				for aml in partner.weekly_statement_line_ids:
					if aml.invoice_type == 'invoice':
						date_maturity = aml.invoice_date_due
						weekly_amount_due_amt += aml.result
						if date_maturity:
							if date_maturity <= current_date:
								weekly_amount_overdue_amt += aml.result
					partner.weekly_payment_amount_due_amt = weekly_amount_due_amt
					partner.weekly_payment_amount_overdue_amt = weekly_amount_overdue_amt
			else:
				partner.weekly_payment_amount_due_amt = 00
				partner.weekly_payment_amount_overdue_amt = 00

	def _get_weekly_supplier_payment_amount_due_amt(self):
		company = self.env.user.company_id
		current_date = datetime.now().date()
		for partner in self:
			partner.do_process_monthly_statement_supplier_filter(sts=None)
			partner.do_process_weekly_statement_supplier_filter()
			weekly_amount_due_amt = 0.0
			weekly_amount_overdue_amt = 0.0
			if partner.weekly_statement_line_ids:
				for aml in partner.weekly_statement_line_ids:
					if aml.invoice_type == 'bill':
						date_maturity = aml.invoice_date_due
						weekly_amount_due_amt += aml.result
						if date_maturity:
							if date_maturity <= current_date:
								weekly_amount_overdue_amt += aml.result
					partner.weekly_supplier_payment_amount_due_amt = weekly_amount_due_amt
					partner.weekly_supplier_payment_amount_overdue_amt = weekly_amount_overdue_amt
			else:
				partner.weekly_supplier_payment_amount_due_amt = 00
				partner.weekly_supplier_payment_amount_overdue_amt = 00

	def _get_today(self):
		for obj in self:
			obj.current_date = fields.Date.today()
	

	is_set_statments = fields.Boolean(string='Set Staments',compute='_compute_set_statments')
	start_date = fields.Date('Start Date', compute='get_dates')
	month_name = fields.Char('Month', compute='get_dates')
	end_date = fields.Date('End Date', compute='get_dates')

	monthly_statement_line_ids = fields.One2many('monthly.statement.line', 'partner_id', 'Monthly Statement Lines')
	weekly_statement_line_ids = fields.One2many('weekly.statement.line', 'partner_id', 'Weekly Statement Lines')

	supplier_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customers move lines', domain=[('move_type', 'in', ['in_invoice','in_refund']),('state', 'in', ['posted']),('is_set_statments', '=', True)])
	balance_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines', domain=[('move_type', 'in', ['out_invoice','out_refund']),('state', 'in', ['posted']),('is_set_statments', '=', True)])
	
	payment_amount_due_amt=fields.Float(compute='_get_payment_amount_due_amt', string="Balance Due")
	payment_amount_overdue_amt = fields.Float(compute='_get_payment_amount_due_amt', string="Total Overdue Amount"  )
	
	payment_amount_due_amt_supplier=fields.Float(compute = '_get_payment_amount_due_amt_supplier', string="Supplier Balance Due")
	payment_amount_overdue_amt_supplier = fields.Float(compute='_get_payment_amount_due_amt_supplier', string="Total Supplier Overdue Amount"  )
	
	monthly_payment_amount_due_amt = fields.Float(compute='_get_monthly_payment_amount_due_amt', string="Monthly Balance Due",)
	monthly_payment_amount_overdue_amt = fields.Float(compute='_get_monthly_payment_amount_due_amt', string="Monthly Total Overdue Amount")

	monthly_payment_supplier_amount_due_amt = fields.Float(compute='_get_monthly_supplier_payment_amount_due_amt', string="Supplier Monthly Balance Due")
	monthly_payment_supplier_amount_overdue_amt = fields.Float(compute='_get_monthly_supplier_payment_amount_due_amt', string="Supplier Monthly Total Overdue Amount")

	weekly_payment_amount_due_amt = fields.Float(compute='_get_weekly_payment_amount_due_amt',
												 string="Weekly Balance Due")
	weekly_payment_amount_overdue_amt = fields.Float(compute='_get_weekly_payment_amount_due_amt',
													 string="Weekly Total Overdue Amount")


	weekly_supplier_payment_amount_due_amt = fields.Float(compute='_get_weekly_supplier_payment_amount_due_amt',
												 string="Supplier Weekly Balance Due",)
	weekly_supplier_payment_amount_overdue_amt = fields.Float(compute='_get_weekly_supplier_payment_amount_due_amt',
													 string="Supplier Weekly Total Overdue Amount")
	current_date = fields.Date(default=fields.date.today(), compute="_get_today")

	first_thirty_day = fields.Float(string="0-30",compute="compute_days")
	thirty_sixty_days = fields.Float(string="30-60",compute="compute_days")
	sixty_ninty_days = fields.Float(string="60-90",compute="compute_days")
	ninty_plus_days = fields.Float(string="90+",compute="compute_days")
	total = fields.Float(string="Total",compute="compute_total")
	opt_statement = fields.Boolean('Opt Statement', default=False)
	company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
	due_customer_statement = fields.Selection(related='company_id.due_customer_statement', string="Statements",readonly=False)
	due_supplier_statement = fields.Selection(related='company_id.due_supplier_statement', string="Statements ",
											  readonly=False)



	def _compute_set_statments(self):
		account_id =  self.env['account.move'].search([])
		for check in account_id:
			check.is_set_statments = False
		for rec in self:
			if not rec.company_id:
				rec.company_id  = self.env.user.company_id
			if rec.due_customer_statement == 'only_due':
				rec.is_set_statments = True
				due_id = self.env['account.move'].search([('partner_id','=',rec.id),('move_type', 'in', ['out_invoice','out_refund','entry']),('state', 'in', ['posted']),('amount_residual_signed', '!=',0)])
				sup_due_id = self.env['account.move'].search([('move_type', 'in', ['in_invoice','in_refund','entry']),('state', 'in', ['posted']),('amount_residual_signed', '!=',0)])
				for record in due_id:
					record.is_set_statments = rec.is_set_statments

				for set in sup_due_id:
					set.is_set_statments = rec.is_set_statments

			elif rec.due_customer_statement == 'only_overdue':
				today = date.today()
				rec.is_set_statments = True
				due_id = self.env['account.move'].search(
					[('partner_id', '=', rec.id), ('move_type', 'in', ['out_invoice', 'out_refund', 'entry']),
					 ('state', 'in', ['posted'])])
				sup_due_id = self.env['account.move'].search(
					[('move_type', 'in', ['in_invoice', 'in_refund', 'entry']), ('state', 'in', ['posted'])])
				set = []
				for record in due_id:
					if record.invoice_date:
						start_date = fields.Date.from_string(today)
						end_date = fields.Date.from_string(record.invoice_date_due)
						if start_date > end_date:
							set.append(record.id)
							record.is_set_statments = rec.is_set_statments

					else:
						record.is_set_statments = False

				for record in sup_due_id:
					if record.invoice_date:
						start_date = fields.Date.from_string(today)
						end_date = fields.Date.from_string(record.invoice_date_due)
						if start_date > end_date:
							set.append(record.id)
							record.is_set_statments = rec.is_set_statments
					else:
						record.is_set_statments = False

			else:
				rec.is_set_statments = True
				due_id = self.env['account.move'].search(
					[('partner_id', '=', rec.id), ('move_type', 'in', ['out_invoice', 'out_refund', 'entry']),
					 ('state', 'in', ['posted'])])

				sup_due_id = self.env['account.move'].search(
					[('move_type', 'in', ['in_invoice', 'in_refund', 'entry']), ('state', 'in', ['posted'])])
				for record in due_id:
					record.is_set_statments = rec.is_set_statments

				for set in sup_due_id:
					set.is_set_statments = rec.is_set_statments


	def get_dates(self):
		for record in self:
			today = date.today()
			d = today - relativedelta(months=1)

			start_date = date(d.year, d.month,1)
			end_date = date(today.year, today.month,1) - relativedelta(days=1)
			
			record.month_name = calendar.month_name[start_date.month] or False
			record.start_date = str(start_date) or False
			record.end_date = str(end_date) or False

	@api.depends('balance_invoice_ids')
	def compute_days(self):
		today = datetime.today().date()
		for partner in self:
			partner.first_thirty_day = 0
			partner.thirty_sixty_days = 0
			partner.sixty_ninty_days = 0
			partner.ninty_plus_days = 0
			moves = self.env['account.move'].search([('partner_id','=',partner.id), ('state', 'in', ['posted'])]) 
			for mv in moves:
				for ml in mv.line_ids :
					if ml.account_id.account_type =='asset_receivable':
						if ml.date_maturity:
							diff = today - ml.date_maturity 
						else:
							diff = today - today
						if diff.days >= 0 and diff.days <= 30:
							partner.first_thirty_day = partner.first_thirty_day + ml.amount_residual

						elif diff.days > 30 and diff.days<=60:
							partner.thirty_sixty_days = partner.thirty_sixty_days + ml.amount_residual

						elif diff.days > 60 and diff.days<=90:
							partner.sixty_ninty_days = partner.sixty_ninty_days + ml.amount_residual
						else:
							if diff.days > 90  :
								partner.ninty_plus_days = partner.ninty_plus_days + ml.amount_residual
		return

	@api.depends('ninty_plus_days','sixty_ninty_days','thirty_sixty_days','first_thirty_day')
	def compute_total(self):
		for partner in self:
			partner.total = 0.0
			partner.total = partner.ninty_plus_days + partner.sixty_ninty_days + partner.thirty_sixty_days + partner.first_thirty_day
		return  

	def _cron_send_customer_statement(self):
		partners = self.env['res.partner'].search([])
		sts = self.env.user.company_id.period
		if self.env.company.send_statement : 
			if sts == 'monthly':
				partners.do_process_monthly_statement_filter(sts)
				partners.customer_monthly_send_mail()
			elif sts == 'all':
				partners.customer_send_mail_from_cron()
		return True

	def _cron_send_supplier_statement(self):
		partners = self.env['res.partner'].search([])
		sts = self.env.user.company_id.sup_period
		if self.env.company.send_supplier_statement:
			if sts == 'monthly':
				partners.do_process_monthly_statement_supplier_filter(sts)
				partners.supplier_monthly_send_mail()
			elif sts == 'all':
				partners.supplier_send_mail_from_cron()
		return True


	def customer_monthly_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.monthly_payment_amount_due_amt = None
			partner._get_monthly_payment_amount_due_amt()
			if partner.opt_statement == False:
				if partner.monthly_payment_amount_due_amt == 0.00:
					pass
				else:
					if partner.email:
						template = self.env.ref('account_statement.email_template_customer_monthly_statement')
						report = self.env.ref('account_statement.report_customer_monthly_print')
						attachments = []
						report_name = template._render_field('report_name', [partner.id])[partner.id]
						report_service = report.report_name
						if report.report_type in ['qweb-html', 'qweb-pdf']:
							result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])

						else:
							res = self.env['ir.actions.report']._render(report, [partner.id])
							if not res:
								raise UserError(_('Unsupported report type %s found.', report.report_type))
							result, report_format = res

						# TODO in trunk, change return format to binary to ma_cron_tch message_post expected format
						result = base64.b64encode(result)
						if not report_name:
							report_name = 'report.' + report_service
						ext = "." + report_format
						if not report_name.endswith(ext):
							report_name += ext
							
						author = ''
						attachments.append((report_name, result))
						template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)
						msg = _('Customer Monthly Statement email sent to %s-%s' % (partner.name, partner.email))
						partner.message_post(body=msg)
					else:
						unknown_mails += 1
		return unknown_mails


	def customer_weekly_send_mail(self):
		unknown_mails = 0
		
		for partner in self:
			partner.weekly_payment_amount_due_amt = None
			partner._get_weekly_payment_amount_due_amt()
			if partner.opt_statement == False:
				if partner.weekly_payment_amount_due_amt == 0.00:
					pass
				else:
					if partner.email:
						
						template = self.env.ref('account_statement.email_template_customer_weekly_statement')

						report = self.env.ref('account_statement.report_customer_weekly_print')

						attachments = []
						report_name = template._render_field('report_name', [partner.id])[partner.id]
						report_service = report.report_name

						if report.report_type in ['qweb-html', 'qweb-pdf']:
							result, format = report.sudo()._render_qweb_pdf([partner.id])
						else:
							res = report.render([partner.id])
							if not res:
								raise UserError(_('Unsupported report type %s found.') % report.report_type)
							result, format = res

						# TODO in trunk, change return format to binary to match message_post expected format
						result = base64.b64encode(result)
						if not report_name:
							report_name = 'report.' + report_service
						ext = "." + format
						if not report_name.endswith(ext):
							report_name += ext

						author = ''

						attachments.append((report_name, result))

						template.with_context(weekly_attachments=attachments).send_mail(partner.id)

						msg = _('Customer Weekly Statement email sent to %s-%s' % (partner.name, partner.email) )

						partner.message_post(body=msg)
					else:
						unknown_mails += 1
		return unknown_mails            
				
				
	def supplier_monthly_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.monthly_payment_supplier_amount_due_amt = None
			partner._get_monthly_supplier_payment_amount_due_amt()
			if partner.opt_statement == False:
				if partner.monthly_payment_supplier_amount_due_amt == 0.00:
					pass
				else:
					if partner.email:
						template = self.env.ref('account_statement.email_template_supplier_monthly_statement')
						report = self.env.ref('account_statement.report_supplier_monthly_print')
						attachments = []
						report_name = template._render_field('report_name', [partner.id])[partner.id]
						report_service = report.report_name
						if report.report_type in ['qweb-html', 'qweb-pdf']:
							result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])

						else:
							res = self.env['ir.actions.report']._render(report, [partner.id])
							if not res:
								raise UserError(_('Unsupported report type %s found.', report.report_type))
							result, report_format = res

						# TODO in trunk, change return format to binary to match message_post expected format
						result = base64.b64encode(result)
						if not report_name:
							report_name = 'report.' + report_service
						ext = "." + report_format
						if not report_name.endswith(ext):
							report_name += ext
							
						author = ''
						attachments.append((report_name, result))
						template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)
						msg = _('Supplier Monthly Statement email sent to %s-%s' % (partner.name, partner.email))
						partner.message_post(body=msg)
					else:
						unknown_mails += 1
		return unknown_mails
						
				
				
	def customer_weekly_send_mail(self):
		unknown_mails = 0
		
		for partner in self:
			partner.weekly_payment_amount_due_amt = None
			partner._get_weekly_payment_amount_due_amt()
			if partner.opt_statement == False:
				if partner.weekly_payment_amount_due_amt == 0.00:
					pass
				else:
					if partner.email: 
						
						template = self.env.ref('account_statement.email_template_customer_weekly_statement')

						report = self.env.ref('account_statement.report_customer_weekly_print')

						attachments = []
						report_name = template._render_field('report_name', [partner.id])[partner.id]
						report_service = report.report_name

						if report.report_type in ['qweb-html', 'qweb-pdf']:
							result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])

						else:
							res = self.env['ir.actions.report']._render(report, [partner.id])
							if not res:
								raise UserError(_('Unsupported report type %s found.', report.report_type))
							result, report_format = res

						# TODO in trunk, change return format to binary to match message_post expected format
						result = base64.b64encode(result)
						if not report_name:
							report_name = 'report.' + report_service
						ext = "." + report_format
						if not report_name.endswith(ext):
							report_name += ext

						author = ''

						attachments.append((report_name, result))

						template.with_context(weekly_attachments=attachments).send_mail(partner.id)

						msg = _('Customer Weekly Statement email sent to %s-%s' % (partner.name, partner.email) )

						partner.message_post(body=msg)
					else:
						unknown_mails += 1
		return unknown_mails   


	def supplier_weekly_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.weekly_supplier_payment_amount_due_amt = None
			partner._get_weekly_supplier_payment_amount_due_amt()
			if partner.opt_statement == False:
				if partner.weekly_supplier_payment_amount_due_amt == 0.00:
					pass
				else:
					if partner.email:
						
						template = self.env.ref('account_statement.email_template_supplier_weekly_statement')

						report = self.env.ref('account_statement.report_supplier_weekly_print')

						attachments = []
						report_name = template._render_field('report_name', [partner.id])[partner.id]
						report_service = report.report_name

						if report.report_type in ['qweb-html', 'qweb-pdf']:
							result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])

						else:
							res = self.env['ir.actions.report']._render(report, [partner.id])
							if not res:
								raise UserError(_('Unsupported report type %s found.', report.report_type))
							result, report_format = res

						# TODO in trunk, change return format to binary to match message_post expected format
						result = base64.b64encode(result)
						if not report_name:
							report_name = 'report.' + report_service
						ext = "." + report_format
						if not report_name.endswith(ext):
							report_name += ext

						author = ''

						attachments.append((report_name, result))

						template.with_context(weekly_attachments=attachments).send_mail(partner.id)

						msg = _('Supplier Weekly Statement email sent to %s-%s' % (partner.name, partner.email) )

						partner.message_post(body=msg)
					else:
						unknown_mails += 1
		return unknown_mails                   
				
				

	def do_process_monthly_statement_filter(self, sts):
		account_invoice_obj = self.env['account.move'] 
		statement_line_obj = self.env['monthly.statement.line']
		
		
		for record in self:
			today = date.today()
			d = today - relativedelta(months=1)

			start_date = date(d.year, d.month,1)
			end_date = date(today.year, today.month,1) - relativedelta(days=1)
			
			from_date = str(start_date)
			to_date = str(end_date)
			
			domain = [('move_type', 'in', ['out_invoice','out_refund']), ('state', 'in', ['posted']), ('partner_id', '=', record.id)]
			if from_date:
				domain.append(('invoice_date', '>=', from_date))
			if to_date:
				domain.append(('invoice_date', '<=', to_date))
				 
								
			invoices = account_invoice_obj.search(domain)
			for invoice in invoices.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':invoice.partner_id.id or False,
						'state':invoice.state or False,
						'invoice_date':invoice.invoice_date,
						'invoice_date_due':invoice.invoice_date_due,
						'result':invoice.result or 0.0,
						'name':invoice.name or '',
						'amount_total':invoice.amount_total or 0.0,
						'credit_amount':invoice.credit_amount or 0.0,
						'invoice_id' : invoice.id,
						'invoice_origin': invoice.invoice_origin,
						'invoice_type':'invoice',
					}
				exist_line = statement_line_obj.search([('invoice_id', '=', invoice.id)])
				exist_line.write(vals)
				if not exist_line:
					ob = statement_line_obj.create(vals) 

	def do_process_monthly_statement_supplier_filter(self, sts):
		account_invoice_obj = self.env['account.move'] 
		statement_line_obj = self.env['monthly.statement.line']
		
		for record in self:
			
			today = date.today()
			d = today - relativedelta(months=1)

			start_date = date(d.year, d.month,1)
			end_date = date(today.year, today.month,1) - relativedelta(days=1)
			
			from_date = str(start_date)
			to_date = str(end_date)
			domain = [('move_type', 'in', ['in_invoice','in_refund']), ('state', 'in', ['posted']), ('partner_id', '=', record.id)]
			if from_date:
				domain.append(('invoice_date', '>=', from_date))
			if to_date:
				domain.append(('invoice_date', '<=', to_date))
				 
								
			invoices = account_invoice_obj.search(domain)
			for invoice in invoices.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':invoice.partner_id.id or False,
						'state':invoice.state or False,
						'invoice_date':invoice.invoice_date,
						'invoice_date_due':invoice.invoice_date_due,
						'result':invoice.result or 0.0,
						'name':invoice.name or '',
						'amount_total':invoice.amount_total or 0.0,
						'credit_amount':invoice.credit_amount or 0.0,
						'invoice_id' : invoice.id,
						'invoice_origin': invoice.invoice_origin,
						'invoice_type': 'bill',
					}
				exist_line = statement_line_obj.search([('invoice_id', '=', invoice.id)])
				exist_line.write(vals)
				if not exist_line:
					ob = statement_line_obj.create(vals) 


	def customer_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
			if not partners_to_email and partner.email:
				partners_to_email = [partner]
			if partners_to_email:
				for partner_to_email in partners_to_email:
					mail_template_id = self.env.ref('account_statement.email_template_customer_statement')
					mail_template_id.send_mail(partner_to_email.id)
				if partner not in partner_to_email:
					self.message_post([partner.id], body=_('Customer Statement email sent to %s' % ', '.join(['%s <%s>' % (partner.name, partner.email) for partner in partners_to_email])))
		return unknown_mails
	
	def customer_send_mail_from_cron(self):
		for partner in self:
			if partner.opt_statement == False and partner.balance_invoice_ids:
				mail_template_id = self.env.ref('account_statement.email_template_customer_statement')
				mail_template_id.send_mail(partner.id)
		return True


	def supplier_send_mail_from_cron(self):
		for partner in self:
			if partner.opt_statement == False and partner.supplier_invoice_ids:
				mail_template_id = self.env.ref('account_statement.email_template_supplier_statement')
				mail_template_id.send_mail(partner.id)
		return True


	
	def _cron_send_customer_weekly_statement(self):
		partners = self.env['res.partner'].search([])
		company = self.env.user.company_id
		today = date.today()
		
		if company.send_statement and company.weekly_days and company.period == 'weekly' or company.period == 'all':
			if int(company.weekly_days) == int(today.weekday()) :
				partners.do_process_weekly_statement_filter()
				partners.customer_weekly_send_mail()
		return True


	def _cron_send_supplier_weekly_statement(self):
		partners = self.env['res.partner'].search([])
		company = self.env.user.company_id
		today = date.today()
		if company.send_supplier_statement and company.sup_weekly_days and company.sup_period == 'weekly' or company.sup_period == 'all':
			if int(company.sup_weekly_days) == int(today.weekday()) :
				partners.do_process_weekly_statement_supplier_filter()
				partners.supplier_weekly_send_mail()
		return True


	def do_process_weekly_statement_filter(self):
		weekly_account_invoice_obj = self.env['account.move']
		weekly_statement_line_obj = self.env['weekly.statement.line']
		for record in self:
			today = date.today()

			start_date = today + timedelta(-today.weekday(), weeks=-1)
			end_date = today + timedelta(-today.weekday() - 1)
			
			from_date = str(start_date)
			to_date = str(end_date)

			domain = [('move_type', 'in', ['out_invoice', 'out_refund']), ('state', 'in', ['posted']),
					  ('partner_id', '=', record.id)]
			if from_date:
				domain.append(('invoice_date', '>=', from_date))
			if to_date:
				domain.append(('invoice_date', '<=', to_date))

			invoices = weekly_account_invoice_obj.search(domain)
			for invoice in invoices.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':invoice.partner_id.id or False,
						'state':invoice.state or False,
						'invoice_date':invoice.invoice_date,
						'invoice_date_due':invoice.invoice_date_due,
						'result':invoice.result or 0.0,
						'name':invoice.name or '',
						'amount_total':invoice.amount_total or 0.0,
						'credit_amount':invoice.credit_amount or 0.0,
						'invoice_id' : invoice.id,
						'invoice_origin': invoice.invoice_origin,
						'invoice_type':'invoice',
					}
				exist_line = weekly_statement_line_obj.search([('invoice_id', '=', invoice.id)])
				exist_line.write(vals)
				if not exist_line:
					ob = weekly_statement_line_obj.create(vals) 


	def do_process_weekly_statement_supplier_filter(self):
		weekly_account_invoice_obj = self.env['account.move']
		weekly_statement_line_obj = self.env['weekly.statement.line']
		for record in self:
			today = date.today()

			start_date = today + timedelta(-today.weekday(), weeks=-1)
			end_date = today + timedelta(-today.weekday() - 1)
			
			from_date = str(start_date)
			to_date = str(end_date)

			domain = [('move_type', 'in', ['in_invoice', 'in_refund']), ('state', 'in', ['posted']),
					  ('partner_id', '=', record.id)]
			if from_date:
				domain.append(('invoice_date', '>=', from_date))
			if to_date:
				domain.append(('invoice_date', '<=', to_date))

			invoices = weekly_account_invoice_obj.search(domain)
			for invoice in invoices.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':invoice.partner_id.id or False,
						'state':invoice.state or False,
						'invoice_date':invoice.invoice_date,
						'invoice_date_due':invoice.invoice_date_due,
						'result':invoice.result or 0.0,
						'name':invoice.name or '',
						'amount_total':invoice.amount_total or 0.0,
						'credit_amount':invoice.credit_amount or 0.0,
						'invoice_id' : invoice.id,
						'invoice_origin': invoice.invoice_origin,
						'invoice_type': 'bill',
					}
				exist_line = weekly_statement_line_obj.search([('invoice_id', '=', invoice.id)])
				exist_line.write(vals)
				if not exist_line:
					ob = weekly_statement_line_obj.create(vals) 




	def supplier_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
			if not partners_to_email and partner.email:
				partners_to_email = [partner]
			if partners_to_email:
				for partner_to_email in partners_to_email:
					mail_template_id = self.env.ref('account_statement.email_template_supplier_statement')
					mail_template_id.send_mail(partner_to_email.id)
		return unknown_mails
	

	def do_button_print_statement(self):
		return self.env.ref('account_statement.report_customert_print').report_action(self)
		
	def do_button_print_statement_vendor(self) : 
		return self.env.ref('account_statement.report_supplier_print').report_action(self)



# Over due functionality

	def _cron_send_overdue_statement(self):
		partners = self.env['res.partner'].search([])
		if self.env.company.due_customer_statement:
			if self.env.company.due_customer_statement == 'only_overdue':
				partners.do_partner_mail()
		return True

	def _cron_send_supplier_overdue_statement(self):
		partners = self.env['res.partner'].search([])
		company = self.env.user.company_id
		if self.env.company.due_supplier_statement:
			if self.env.company.due_supplier_statement == 'only_overdue':
				partners.do_supplier_mail()
		return True

	def _cron_send_customer_due_statement(self):
		partners = self.env['res.partner'].search([])
		if self.env.company.due_customer_statement:
			if self.env.company.due_customer_statement == 'only_due':
				partners.do_partner_due_mail()
		return True

	def _cron_send_supplier_due_statement(self):
		partners = self.env['res.partner'].search([])
		if self.env.company.due_supplier_statement:
			if self.env.company.due_supplier_statement == 'only_due':
				partners.do_supplier_due_mail()
		return True

	def do_button_print(self):
		return self.env.ref('account_statement.report_customer_overdue_print').report_action(self)
	
	def do_partner_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.payment_amount_overdue_amt = None
			partner._get_payment_amount_due_amt()
			if partner.payment_amount_overdue_amt == 0.00:
				pass
			else:

				if partner.email:

					template = self.env.ref('account_statement.email_template_customer_over_due_statement')
					report = self.env.ref('account_statement.report_customer_overdue_print')

					attachments = []
					report_name = template._render_field('report_name', [partner.id])[partner.id]
					
					report_service = report.report_name

					if report.report_type in ['qweb-html', 'qweb-pdf']:
						result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])
					else:
						res = self.env['ir.actions.report']._render(report, [partner.id])
						if not res:
							raise UserError(_('Unsupported report type %s found.', report.report_type))
						result, report_format = res

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + report_format
					if not report_name.endswith(ext):
						report_name += ext

					author = ''

					attachments.append((report_name, result))

					template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)

					msg = _('Customer Overdue Statement email sent to %s-%s' % (partner.name, partner.email) )

					partner.message_post(body=msg)
				else:
					unknown_mails += 1


		return unknown_mails

	def do_button_due_print(self):
		return self.env.ref('account_statement.report_customer_due_print').report_action(self)

	def do_partner_due_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.payment_amount_due_amt = None
			partner._get_payment_amount_due_amt()
			if partner.payment_amount_due_amt == 0.00:
				pass
			else:

				if partner.email:

					template = self.env.ref('account_statement.email_template_customer_due_statement')
					report = self.env.ref('account_statement.report_customer_due_print')

					attachments = []
					report_name = template._render_field('report_name', [partner.id])[partner.id]
					
					report_service = report.report_name

					if report.report_type in ['qweb-html', 'qweb-pdf']:
						result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])
					else:
						res = self.env['ir.actions.report']._render(report, [partner.id])
						if not res:
							raise UserError(_('Unsupported report type %s found.', report.report_type))
						result, report_format = res

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + report_format
					if not report_name.endswith(ext):
						report_name += ext

					author = ''

					attachments.append((report_name, result))

					template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)

					msg = _('Customer due Statement email sent to %s-%s' % (partner.name, partner.email) )

					partner.message_post(body=msg)
				else:
					unknown_mails += 1


		return unknown_mails


	def do_button_supplier_print(self):
		return self.env.ref('account_statement.report_supplier_overdue_print').report_action(self)

	def do_supplier_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.payment_amount_overdue_amt_supplier = None
			partner._get_payment_amount_due_amt_supplier()
			if partner.payment_amount_overdue_amt_supplier == 0.00:
				pass
			else:

				if partner.email:

					template = self.env.ref('account_statement.email_template_supplier_over_due_statement')
					report = self.env.ref('account_statement.report_supplier_overdue_print')

					attachments = []
					report_name = template._render_field('report_name', [partner.id])[partner.id]
					
					report_service = report.report_name

					if report.report_type in ['qweb-html', 'qweb-pdf']:
						result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])
					else:
						res = self.env['ir.actions.report']._render(report, [partner.id])
						if not res:
							raise UserError(_('Unsupported report type %s found.', report.report_type))
						result, report_format = res

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + report_format
					if not report_name.endswith(ext):
						report_name += ext

					author = ''

					attachments.append((report_name, result))

					template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)

					msg = _('Supplier Overdue Statement email sent to %s-%s' % (partner.name, partner.email) )

					partner.message_post(body=msg)
				else:
					unknown_mails += 1


		return unknown_mails


	def do_button_due_supplier_print(self):
		return self.env.ref('account_statement.report_supplier_due_print').report_action(self)

	def do_supplier_due_mail(self):
		unknown_mails = 0
		for partner in self:
			partner.payment_amount_due_amt_supplier = None
			partner._get_payment_amount_due_amt_supplier()
			if partner.payment_amount_due_amt_supplier == 0.00:
				pass
			else:

				if partner.email:

					template = self.env.ref('account_statement.email_template_supplier_due_statement')
					report = self.env.ref('account_statement.report_supplier_due_print')

					attachments = []
					report_name = template._render_field('report_name', [partner.id])[partner.id]
					
					report_service = report.report_name

					if report.report_type in ['qweb-html', 'qweb-pdf']:
						result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, [partner.id])
					else:
						res = self.env['ir.actions.report']._render(report, [partner.id])
						if not res:
							raise UserError(_('Unsupported report type %s found.', report.report_type))
						result, report_format = res

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + report_format
					if not report_name.endswith(ext):
						report_name += ext

					author = ''

					attachments.append((report_name, result))

					template.sudo().with_context(monthly_attachments=attachments).send_mail(partner.id)

					msg = _('Supplier due Statement email sent to %s-%s' % (partner.name, partner.email) )

					partner.message_post(body=msg)
				else:
					unknown_mails += 1

		return unknown_mails




