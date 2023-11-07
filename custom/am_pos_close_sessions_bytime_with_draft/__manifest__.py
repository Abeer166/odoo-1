# -*- coding: utf-8 -*-

{
    'name': 'POS Close Sessions By Time with delete draft orders',
    'version': '16.0',
    'category': 'Point of Sale',
    'author': 'Ahmed Elmahdi',
    'license': 'LGPL-3',
    'summary': """
    POS Close Sessions By Time
    Delete Draft Orders to close session
    Set Hour in each session to close automated
    Close Sessions Deppend in time Set
    """,
    'description': 'POS Close All Sessions',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_session_views.xml',
    ],
    'images': [
        'static/description/image.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'price': 28,
    'currency': 'EUR',
}
