# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2023 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class WizardPartnerRouteMap(models.TransientModel):
    _name = 'wizard.partner.route.map'
    _description = 'Partner Routes Map'

    partner_route_ids = fields.One2many(
        'partner.route.map.lines', 'partner_route_map_id')

    @api.model
    def default_get(self, fields_lst):
        res = super(WizardPartnerRouteMap, self).default_get(fields_lst)
        ctx = dict(self.env.context)
        partner_route_ids = []
        sequence = 1
        for partner in self.env['res.partner'].browse(
                ctx.get('active_ids', [])):
            partner_route_ids.append(
                (0, 0, {'partner_id': partner.id, 'sequence': sequence}))
            sequence += 1
        res.update({'partner_route_ids': partner_route_ids})
        return res

    def action_show_routes_map(self):
        if not self.partner_route_ids:
            return {'type': 'ir.actions.act_window_close'}
        url = 'https://www.google.com/maps/dir/?api=1'
        # Origin
        start_partner = self.env.user.partner_id
        if not start_partner.partner_latitude and start_partner.partner_longitude:
            raise UserError(
                _('Missing %s Geolocation!' % (start_partner.name)))
        origin_coordinates = start_partner.mapped(
            lambda x: (str(x.partner_latitude), str(x.partner_longitude)))
        origin_res = origin_coordinates[0][0] + ',' + origin_coordinates[0][1]
        url += '&origin=%s' % (origin_res)

        # Destination
        last_partner = self.partner_route_ids[-1].partner_id
        if not last_partner.partner_latitude and \
                last_partner.partner_longitude:
            raise UserError(
                _('Missing %s Geolocation!' % (last_partner.name)))
        url += '&destination=%s' % (
            str(last_partner.partner_latitude) + ',' + str(
                last_partner.partner_longitude))

        # WayPoints
        if len(self.partner_route_ids.ids) > 1:
            partner_ids = self.partner_route_ids.mapped(
                'partner_id') - last_partner
            coordinates = partner_ids.filtered(
                lambda res: res.partner_latitude and res.partner_longitude
            ).mapped(lambda x: (str(x.partner_latitude),
                                str(x.partner_longitude)))
            if not coordinates:
                raise UserError(_('Missing Partners Geolocation!'))
            partner_res = []
            partner_res += [i[0] + ',' + i[1] for i in coordinates]
            url += '&waypoints=%s' % ('|'.join(partner_res))

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


class PartnerRouteLines(models.TransientModel):
    _name = 'partner.route.map.lines'
    _description = 'Partner Route Lines'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", index=True, default=1)
    partner_id = fields.Many2one('res.partner', required=True)
    partner_route_map_id = fields.Many2one('wizard.partner.route.map')
