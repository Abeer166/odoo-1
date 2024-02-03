from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReserveUnreserveWizard(models.TransientModel):
    _name = 'reserve.unreserve.wizard'
    _description = "Reserve Unreserve Wizard"

    picking_ids = fields.Many2many('stock.picking', 'rel_stock_picking_wizard', 'wizard_id', 'picking_id',
                                   string="Stock Picking")

    @api.model
    def default_get(self, default_fields):
        res = super(ReserveUnreserveWizard, self).default_get(default_fields)
        active = self.env.context.get('active_ids')
        picking_ids = self.env['stock.picking'].browse(active)
        res.update({
            'picking_ids': [(6, 0, picking_ids.ids)],

        })

        return res

    def action_reserve_stock(self):
        for rec in self:
            for picking_id in rec.picking_ids:
                if picking_id.state in ['assigned', 'done', 'cancel']:
                    raise ValidationError(_(
                        '%s Stock Picking is all ready Reserve or done,Please select unreserve picking for reserve stock') % (
                                              picking_id.name))
                picking_id.action_assign()

    def action_unreserve_stock(self):
        for rec in self:
            for picking_id in rec.picking_ids:
                if picking_id.state != 'assigned':
                    raise ValidationError(_(
                        '%s Stock Picking not Reserve,Please select reserve picking for unreserve stock') % (
                                              picking_id.name))
                picking_id.do_unreserve()
