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

{
    'name': 'Odoo Multi Branch Financial Reports(Community-Enterprise)',
    'version': '0.16',
    'author': 'Zero Systems',
    'website': "https://www.erpzero.com",
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/e0SlLr6ncFs',
    'category': 'Accounting',              
    'summary': 'Multiple Branch operation Financial Reports',
    'description': "" 
    
    "Multi Branch Accounting Reports , Multi Branch Financial Reports"

    "Print Report In PDF Format"
    "Date and Other Filter Option"
    "Branch wise Financial Statement"
    "Journal Filter on Report"
    "Balance Sheet Report"
    "Profit and Loss Report"
    "General Ledger Report"
    "Trial balance Report"

    "",
    'depends': ['branches'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_account_type.xml',
        'views/financial_report.xml',
        'wizard/report_common_view.xml',
        'wizard/partner_ledger.xml',
        'wizard/general_ledger.xml',
        'wizard/trial_balance.xml',
        'wizard/balance_sheet.xml',
        'wizard/profit_and_loss.xml',
        'report/report.xml',
        'report/report_partner_ledger.xml',
        'report/report_general_ledger.xml',
        'report/report_trial_balance.xml',
        'report/report_financial.xml',
        'report/report_journal_entries.xml',
    ],
    "price": 50.0,
    "currency": 'EUR',
    'installable': True,
    'auto_install': False,
    "application": False,
    'images': ['static/description/branchreportcc.png'],
    'pre_init_check_vers': 'pre_init_check_vers',
}
