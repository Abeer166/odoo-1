# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Document Management System for All Users',
    'version' : '16.0.1.0',
    'description': """
            Share and manage your attached Documents
    """,
    'summary': """
        Share and manage your attached Documents,
        Document Management System - Customer Portal,
        Document Management System (DMS) - Customer Portal,
        Customer Portal of Documents and Attachments in Odoo App,
        Partner Portal of Documents and Attachments in Odoo App,
        Vendor / Supplier Portal of Documents and Attachments in Odoo App,
        Share Document on Portal to Your Customers / Vendors / Partners,
        Document,
        Attachment,
        Portal,
        Share Attachment,
        Share Document,
        Own Documents,
        Own Attachments,
        Shared Attachment,
        Shared Document,
        My Attchment,
        My Document,
        Shared with Other,
        Shared with Me,
        Shared by me,
        Download Attachment,
        Download Document,
        Portal Document,
        Portal Attachment,
        Attachment Download,
        Document Downlaod,
        Document Management,
        Portal Attachment,
        Portal Document,
        Document Portal,
        Restrict to share,
        Other user Attachment,
        Other user Document
        
	""",
	'author': 'Omax Informatics',
    'category': 'Document Management',
    'website': 'https://www.omaxinformatics.com',
    'depends' : ['base','website','mail'],
    'data': [
        'views/attachment_templates.xml',
        'views/custom_ir_attachment_views.xml',
        'views/res_company_inherit.xml',
    ],
    'installable': True,
    'application': True,
    "images": ["static/description/banner.png",],
    'assets': {
        'web.assets_backend': [
            'portal_doc_mgmt_omax/static/src/components/*/*.js',
            'portal_doc_mgmt_omax/static/src/components/*/*.xml',
        ],
    },
    'currency':'USD',
    'price': 50.0,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/ShTdo_GaJL0',
    'license': 'LGPL-3',
}

