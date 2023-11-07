# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Sales Details Report",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Sales",
    "summary": """sales order report app, so analysis by time odoo, quotation information module ,Sales Details Report""",
    "description": """Do you want to get detaied informations of sales like which products sold? how many qty sold? payment got by which methods?what is taxes  amount? tax details? so our app will help you to get all this information very easily.
 you need to enter from date to date and you can select optional things if you want, status and channels. 
you will find detaild report with sales information. this app will help you to get more infomration apart from total sale order. Cheers!
 Sales Order Detail Report Odoo, Quotations Detail Report Odoo.
 Sales detail report Module, Detailed Information Of  Sales Order odoo, scheduled report of sales , Quotation Information Date Wise Odoo, So Detail Report Odoo, Sale Order Detail Information Report Odoo.
 sales Order Report app, So Analysis By Time Odoo, Quotation Information Module""",

    "version": "16.0.2",
    "depends": [
        "sale_management"
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "security/sh_sale_details_report_groups.xml",
        "wizard/sh_sale_details_report_wizard_views.xml",
        "report/sh_sale_details_templates.xml",
        "views/sh_sale_details_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "price": 30,
    "currency": "EUR"
}
