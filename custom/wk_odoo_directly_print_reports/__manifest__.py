# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Print Odoo Reports via Zebra Printer",
  "summary"              :  """This module allows the user to directly print the reports via zebra printer instead of downloading as PDF.""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """This module allows the user to directly print the reports via zebra printer instead of downloading as PDF.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/demo_feedback?module=wk_odoo_directly_print_reports",
  "depends"              :  ['base', 'web'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/ir_actions_report_xml_view.xml',
                             'views/report_template_view.xml',
                             'views/printers_view.xml',
                            ],

    "assets"             : {
                            'web.assets_backend': [
                                '/wk_odoo_directly_print_reports/static/src/js/lib/qz-tray.js',
                                '/wk_odoo_directly_print_reports/static/src/js/lib/rsvp-3.1.0.min.js',
                                '/wk_odoo_directly_print_reports/static/src/js/lib/sha-256.min.js',
                                '/wk_odoo_directly_print_reports/static/src/js/inherit_action_menu.js',
                                '/wk_odoo_directly_print_reports/static/src/js/report_action_inherit.js',
                              ]
                           },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  129,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['zplgrf', 'ghostscript']},
}
