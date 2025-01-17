# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Risha C.T(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
{
    'name': 'Customer Route Management',
    'summary': """This module will set routes and generates report based on the routes""",
    'version': '16.0.1.0.0',
    'description': """This module will set routes,
    shows customers in each route and generates report with customer details and due amount.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'live_test_url': 'https://www.youtube.com/watch?v=tdu6iBP2N6Y',
    'category': 'Tools',
    'depends': ['base', 'mail','sale','account'],
    'license': 'OPL-1',
    'price': 19.99,
    'currency': 'EUR',
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_partner.xml',
        'views/delivery_route.xml',
        'security/routaccess.xml',

        'views/report.xml',
        'views/report_template.xml',
        'views/wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'customer_route_management/static/src/js/action_manager.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
