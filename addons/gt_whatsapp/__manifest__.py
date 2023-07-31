
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    Globalteckz                                                              #
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)        #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################


{
    'name': 'All in one Whatsapp app Odoo integration',
    'version': '1.0',
    'category': 'Generic Modules',
    'sequence': 1,
    "summary":"All in one Whatsapp integration will help you to send sales, purchase orders, Picking and invoices to customers whatsapp connector whatsapp integration odoo Whatsapp crm Whatsapp lead Whatsapp task Whatsapp sale order Whatsapp purchase order Whatsapp invoice Whatsapp payment reminder Whatsapp pos Whatsapp so Whatsapp point of sale whats app communication Real WhatsApp All in One Screen integration. Send Product, Sale Order, Invoice, Partner. Connector. Chat-Api. ChatApi. Drag and Drop. ChatRoom Whatsapp Integration App,  Invoice To Customer Whatsapp Module, stock whatsup Whatsapp, Sales Whatsapp App, Purchase Whatsapp, CRM Whatsapp, invoice whatsapp, inventory whatsapp, account whatsup Odoo whatsapp live chat app,Customer Whatsapp, whatsup live chat, whatsup chat Odoo whatsapp chat by odoo website, client whatsup chat module Whatsapp connector integration with whatsapp odoo what'sapp connector invoicing through whatsapp connector for whatsapp odoo whatsup integration message through whatsapp odoo whatsapp bridge odoo whatsapp plugin whatsapp app for odoo erp software ",
    'website': 'https://www.globalteckz.com/shop/odoo-apps/odoo-whatsapp-connector/',
    'live_test_url': 'https://www.globalteckz.com/shop/odoo-apps/odoo-whatsapp-connector/',
    "author" : "Globalteckz",
	"license" : "Other proprietary",
    'images': ['static/description/Banner.gif'],
    "price": "15.00",
    "currency": "USD",
    'description': """
    Odoo whatsapp connector
Odoo whatsapp integration
Odoo whatsapp extension
Odoo whatsapp bridge
Odoo whatsapp plugin
Connect Odoo with whatapp
Whatsapp Odoo connection
Odoo what's app connector
Odoo what's app integration
Odoo what's app extension
Odoo what's app bridge
Odoo what's app plugin
Connect Odoo with what's app
what's app Odoo connection
Odoo whats app connector
Odoo whats app integration
Odoo whats app extension
Odoo whats app bridge
Odoo whats app plugin
Connect Odoo with whats app
whats app Odoo connection
    """,
    'depends': [
        'base','sale','mail','contacts'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'views/whatsapp_invoice_view.xml',
        'wizard/wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
