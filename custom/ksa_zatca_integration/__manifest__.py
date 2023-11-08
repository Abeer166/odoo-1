# -*- coding: utf-8 -*-
{
    'name': "KSA Zatca Phase-2",
    'summary': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business""",
    'description': """
        Phase-2 of ZATCA e-Invoicing(Fatoorah): Integration Phase, its include solution for KSA business
    """,
    'live_test_url': 'https://youtu.be/cM1n_t_FnKQ',
    "author": "Alhaditech",
    "website": "www.alhaditech.com",
    'license': 'OPL-1',
    'images': ['static/description/cover.png'],
    'category': 'Invoicing',
    'version': '16.2.1',
    'price': 590, 'currency': 'USD',
    'depends': ['account', 'sale', 'l10n_sa', 'purchase', 'account_debit_note'],
    'external_dependencies': {
        'python': ['cryptography', 'lxml', 'qrcode']
    },
    "post_init_hook": "post_init_hook",
    'data': [
        'data/data.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/account_move.xml',
        'views/account_tax.xml',
        'views/product_product.xml',
        'reports/account_move.xml',
        'reports/res_partner.xml',
        'reports/res_company.xml',
        'reports/sale_order_report.xml',
        'reports/e_invoicing_b2c.xml',
        'reports/report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ksa_zatca_integration/static/src/css/style.css',
        ],
    },
}
