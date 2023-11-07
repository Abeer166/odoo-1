# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2023 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, api, fields


class WizardPartnerRouteMap(models.TransientModel):
    _inherit = 'wizard.partner.route.map'

    @api.model
    def default_get(self, fields_lst):
        ctx = dict(self.env.context)
        partner_ids = []

        # Sale Orders
        if ctx.get('active_model') and ctx.get('active_model') == 'sale.order':
            order_ids = self.env[ctx['active_model']].browse(
                ctx.get('active_ids', []))
            partner_ids = order_ids.mapped('partner_id').ids

        # Invoices
        if ctx.get('active_model') and ctx.get('active_model') == 'account.move':
            invoice_ids = self.env[ctx['active_model']].browse(
                ctx.get('active_ids', []))
            partner_ids = invoice_ids.mapped('partner_id').ids

        if partner_ids:
            self = self.with_context(active_ids=partner_ids)

        return super(WizardPartnerRouteMap, self).default_get(fields_lst)
