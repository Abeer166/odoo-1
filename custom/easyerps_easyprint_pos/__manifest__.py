# -*- coding: utf-8 -*-
{
    'name': "Easy Print",
    'support': "support@easyerps.com",
    'license': "OPL-1",
    'price': 269,
    'currency': "USD",
    'summary': """
        This module Allows you to print POS receipts directly using Bluetooth, Built-in Printer on SUNMI/Android devices
        """,
    'author': "EasyERPS",
    'website': "https://easyerps.com",
    'category': 'Point of Sale',
    'version': '16.1.0',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'easyerps_easyprint_pos/static/src/js/*.js',
             ('after','point_of_sale/static/src/scss/pos.scss' ,'easyerps_easyprint_pos/static/src/css/BluetoothPrinterReceiptScreen.css'),
            'easyerps_easyprint_pos/static/src/xml/*.xml',
        ],

    },
    'images': ['images/main_screenshot.png'],
}
