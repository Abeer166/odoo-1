from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    location_name = fields.Char("Location Name")

    def select_destination_loc(self):
        return {
                'type': 'ir.actions.client',
                'tag': 'partner_select_current_point',
                'target': 'new',
            }
