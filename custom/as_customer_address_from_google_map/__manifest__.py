{
    'name': "Fetch Live/Current GPS location address from Google Map in Contacts/Customers/Vendors",
    'summary': """Google Map Integration With Contacts""",
    'description': """
       Select current location of customer from google map and store it in address of customer
    """,
    'author': 'Accudoo Solutions Pvt. Ltd.',
    'website': "https://accudoo.com/",
    'category': 'Contacts',
    'version': '16.0.1.0.1',
    'depends': ['base', 'contacts', 'base_geolocalize'],
    'data': [
        'views/res_config_settings_view.xml',
        'views/contact_view.xml'
    ],
    'assets': {
        'web.assets_backend':  [
            'as_customer_address_from_google_map/static/src/js/google_map_pin_current_loc.js',
            'as_customer_address_from_google_map/static/src/xml/google_map_template_view.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'price': 100.0,
    'currency': 'USD',
}
