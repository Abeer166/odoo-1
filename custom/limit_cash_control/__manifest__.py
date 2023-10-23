# -*- coding: utf-8 -*-
{
    "name": "Limit Cash Control in Odoo Point of Sale",
    "version": "0.0.1",
    "category": "Sales/Point of Sale",
    'summary': "Customize Cash Control Mechanism in Point of Sales",
    "author": "Ewetoye Ibrahim",
    "auto_install": False,
    "depends": ["point_of_sale"],
    'installable': True,
    'application': False,
    'data': ['pos_config.xml','custom_pos.xml'],
    "price": 150,
    "currency": 'USD',
    'assets': {
        'point_of_sale.assets': [
            'limit_cash_control/static/src/js/CashOpeningPopup.js',
            'limit_cash_control/static/src/js/ClosePosPopup.js',
            'limit_cash_control/static/src/xml/**/*.xml',
        ],
    },
    'images': ['static/description/limit_cash_control.jpg'],
    'license': 'LGPL-3',
}
