# -*- coding: utf-8 -*-
{
	"name" : "POS Customer Address with Google Maps in Odoo",
	"author": "Edge Technologies",
	"version" : "16.0.1.2",
	"live_test_url":'https://youtu.be/9qlkHDwaVq0',
	"images":["static/description/main_screenshot.png"],
	'summary': 'POS address google map pos address map for pos customer google map address pos google map pos google address of customer pos customer google address on point of sale google map address pos customer location pos customer google location pos google address.',
	"description": """This app used to change customer location from pos using google maps. you can set the address based on google maps, search location on google maps in pos autocomplete address managed with point of sales. point of sale customer address with google map in odoo. point of sale auto complete address with google map in odoo. pos auto complete address with google map in odoo.
 Allow to search customer address in pos

Allow user to search any location by map in pos. suggestion on user input for searching address on pos using google map. pos google map partner address. pos partner address by map. point of sale google map partner address. pos google map customer address. pos customer address by map. point of sale google map customer address. pos customer location on google map point of sale customer location on google map. edit customer address on pos using google map
Gmaps in pos
Map for pos
Customer google maps address
pos google maps
pos google address of customer 
pos customer google address
google address on pos
point of sale google map address
customer google map address
pos customer location 
pos customer google location 
pos google address
google address pos
google location pos 


 """,
	"license" : "OPL-1",
	"depends" : ['base','point_of_sale'],
	"data": [
		'views/pos_config_view.xml',
	],
	'assets': {
        'point_of_sale.assets': [
            'pos_address_map_app/static/src/css/custom.css',
            'pos_address_map_app/static/src/js/api_key.js',
            'pos_address_map_app/static/src/js/pos_custom.js',
            'pos_address_map_app/static/src/xml/pos_view.xml',
        ],               
    },
	"auto_install": False,
	"installable": True,
	"price": 18,
	"currency": 'EUR',
	"category" : "Point of Sale",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
