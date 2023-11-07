{
    'name': "Restrict Opening Cash Control and Closing Control | Hide Cash Control | POS Hide Cash Control | Disable POS Close Session by Access Control(Original)",
    "version": "16.3.2.1",
    'summary': """Hide Cash Control - Using this module Enable and Disable Opening Cash Control and Closing Cash Control.""",
    'description': '''Hide Cash Control - Using this module Enable and Disable Opening Cash Control and Closing Cash Control.''',
    'sequence': 1,
    'category': 'Point of Sale',
    "author" : "DOTSPRIME",
    "email": 'dotsprime@gmail.com',
    "license": 'OPL-1',
    "price": 25,
    "currency": "EUR",   
    'depends': ['base','point_of_sale'],
    'data': ['views/pos_config.xml'],
    'assets': {
        'point_of_sale.assets': [
            'dps_pos_hide_cash_control/static/src/js/chrome.js',
            'dps_pos_hide_cash_control/static/src/js/MaiClosePopup.js',
        ]
    }, 
    'images': ['static/description/main_screenshot.jpg'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
