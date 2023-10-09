# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http


class ZATCA(http.Controller):

    @http.route('/update/partners/vat', auth='none', methods=['POST', 'GET'], csrf=False, cors='*')
    def index(self, **kw):
        partners = request.env['res.partner'].with_user(request.env.user.browse(2)).search([])
        for partner in partners:
            partner.vat = '300075588700003'
        return "updated " + str(len(partners)) + " records."
