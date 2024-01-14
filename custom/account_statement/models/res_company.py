# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta

class Company(models.Model):
    _inherit = 'res.company'
    
    
    send_statement = fields.Boolean("Send Customer Statement")
    send_supplier_statement = fields.Boolean("Send Supplier Statement")
    period = fields.Selection([('monthly', 'Monthly'),('all', "All"),('weekly', "Weekly")],'Period',default='monthly')
    sup_period = fields.Selection([('monthly', 'Monthly'),('all', "All"),('weekly', "Weekly")],'Period ',default='monthly')
    statement_days = fields.Integer("Statement Send Date")
    sup_statement_days = fields.Integer("Statement Send Date ")
    is_customer_statement_portal = fields.Boolean(string="Customer Statement Portal")
    is_supplier_statement_portal = fields.Boolean(string="Supplier Statement Portal")
    due_customer_statement = fields.Selection([('only_due', 'Only Due'),('only_overdue', "Only Overdue"),('both', "Both")],'Dislay Customer Due/overdue Statements ',default='both')
    due_supplier_statement = fields.Selection([('only_due', 'Only Due'),('only_overdue', "Only Overdue"),('both', "Both")],'Dislay Supplier Due/overdue Statements ',default='both')
    
    weekly_days = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ],string="Weekly Send Day")


    sup_weekly_days = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ],string="Weekly Send Day ")
    
    



