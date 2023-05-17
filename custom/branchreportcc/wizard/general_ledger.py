# -*- coding: utf-8 -*-

#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _name = "account.report.general.ledger"
    _inherit = "account.common.account.report"
    _description = "General Ledger Report"

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow'
                                         ' you to add a row to display the amount '
                                         'of debit/credit/balance that precedes'
                                         ' the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), 
                               ('sort_journal_partner', 'Journal & Partner')], 
                              string='Sort by', required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal',
                                   'account_report_general_ledger_journal_rel',
                                   'account_id', 'journal_id', 
                                   string='Journals', required=True)

    branch_ids = fields.Many2many('res.branch',
                                   'account_report_general_ledger_branch_rel',
                                   'account_id', 'branch_id', 
                                   string='Branches')

    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
        return records, data

    def _print_report(self, data):
        records, data = self._get_report_data(data)
        return self.env.ref('branchreportcc.action_report_general_ledger').with_context(landscape=True).report_action(records, data=data)

