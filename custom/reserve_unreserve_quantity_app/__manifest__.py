{
    'name': 'Stock Reserve/Unreserve From Location And Transfer App',
    "author": "Edge Technologies",
    'version': '16.0.1.0',
    'live_test_url': "https://youtu.be/Rxs-5I6H3qQ",
    "images":['static/description/main_screenshot.png'],
    'summary': 'Stock Reserve from location stock Unreserve From Location Inventory Reserve From Location Inventory Unreserve From Location stock reserve from transfer stock reservation from location inventory reservation from location stock reservation from location',
    'description': "We provide reserve or unreserve quantity from stock picking tree view as well as location and create purchase order in sale order when confirm order ",
    "license" : "OPL-1",
    'depends': [
        'stock','sale_management','purchase'
    ],
    'data': [
        'security/security.xml',
           'security/ir.model.access.csv',
           'views/sale_order_inherited_view.xml',
           'views/purchase_order_inherited_view.xml',
           'views/stock_picking_inherited_view.xml',
           'wizard/reserve_unreserve_wizard_view.xml',
           'views/stock_location_inherited_view.xml',

    ],
    'demo': [ ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 15,
    'currency': "EUR",
    'category': 'Warehouse',

}
