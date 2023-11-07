# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'POS Customer Order History',
    'version': '16.0.1.0',
    'summary': 'This module allows user to see customer previous order history in POS.| Point Of Sale | POS sale | Customer | Customer Order History | Previous Order | POS Orders | Past Orders | POS Previous Orders | POS Order History | Recent Orders | POS Recent Order| Recent Order History | Customer Recent Orders | ',
    'description': """
POS Customer Order History
    """,
    'category': 'Point of Sale',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'pos_customer_order_history/static/src/css/custom.css',
            'pos_customer_order_history/static/src/xml/pos_history.xml',
            'pos_customer_order_history/static/src/xml/PartnerLine.xml',
            'pos_customer_order_history/static/src/js/PartnerLine.js',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 40,
    'currency': 'EUR',
}
