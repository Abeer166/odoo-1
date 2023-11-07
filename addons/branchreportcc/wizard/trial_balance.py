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

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _name = 'account.balance.report'
    _inherit = "account.common.account.report"
    _description = 'Trial Balance Report'

    journal_ids = fields.Many2many('account.journal', 'account_balance_report_journal_rel',
                                   'account_id', 'journal_id', 
                                   string='Journals', required=True, default=[])

    branch_ids = fields.Many2many('res.branch', 'account_balance_report_branch_rel',
                                   'account_id', 'branch_id', 
                                   string='Branches', default=[])
    analytic_account_ids = fields.Many2many('account.analytic.account',
                                            'account_trial_balance_analytic_rel',
                                            string='Analytic Accounts')
    

    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return records, data

    def _print_report(self, data):
        records, data = self._get_report_data(data)
        return self.env.ref('branchreportcc.action_report_trial_balance').report_action(records, data=data)
