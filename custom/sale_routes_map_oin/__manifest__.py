# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2023 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Route Map of Sale Orders & Invoices Partners',
    'summary': 'Route Map of multiple selected sale orders aor invoices partners',
    'description': """
This module allows us to open an itinerary map from the start address of the
logged-in user to the addresses of the selected sale orders or invoices
partners from the list.

It will open a pop-up when we select an option from the Action after the
selection of sale orders. We can see all the selected sale orders partners
in that pop-up and can also do arrangement as per our route plan.

Same feature is also available in Invoices too.

It will use the latitude and longitude to localize the partner if this
information is present on the partner.
    """,
    'version': '16.0.1',
    'category': 'Extra Tools/Sales',

    'author': "Odoo IT now",
    'website': "http://www.odooitnow.com/",
    'license': 'Other proprietary',

    'depends': ['sale', 'partner_routes_map_oin'],
    'data': [
        'wizard/wizard_partner_route_map_view.xml',
        ],
    'images': ['images/OdooITnow_screenshot.png'],

    'price': 5.00,
    'currency': 'EUR',

    'installable': True,
    'application': True,
    'auto_install': False
}
