# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "POS Direct Login Without Odoo Backend",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point of Sale",
    "license": "OPL-1",
    "summary": "Redirect to pos screen quick pos login without backend point of sale login point of sale login POS screen login POS session login point of sales direct pos login pos sign in pos signin direct pos direct sign in pos access Odoo",
    "description": """ POS Direct Login Without Odoo Backend, This module is very useful for pos user. 
    Normally pos user logged its redirect to odoo backend than user need to go point of sale and start/resume session. Our module helps to save this unusual time, It will directly redirect you to pos screen instead of odoo backend.
redirect to pos screen app, quick pos login module, pos login without backend, point of sale login odoo, quick pos login, responsive point of sale login""",
    "version": "16.0.1",
    "depends": ['point_of_sale','web'],
    "application": True,
    "data": [
        'views/res_users.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'sh_pos_direct_login/static/src/js/Popups/close_popup.js'
        ],
    },
    "images": ["static/description/background.jpg", ],
    "live_test_url": "https://youtu.be/_JeBY_tkZf8",
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": "EUR"
}
