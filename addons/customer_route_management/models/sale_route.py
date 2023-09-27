from odoo import models, fields, api
from datetime import datetime, time, timedelta



class DeliveryRoute(models.Model):
    _name = 'delivery.route'

    name = fields.Char(string='المنطقه')

    route_lines = fields.One2many('route.lines', 'delivery_route_link', string='القائمه')#route line


class RouteLines(models.Model):
    _name = 'route.lines'
    _rec_name = 'route'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    route = fields.Char(string='المسارات')#route
    delivery_route_link = fields.Many2one('delivery.route')
    cust_tree = fields.One2many('res.partner', 'locations', string='Customers')


    #date1 = fields.Date(string='تاريخ التنفيذ', default=datetime.today())


    @api.onchange('statuss_checkbox')
    def move_record_to_last(self):
        for record in self:
                record.write({'sequence': 9999})

class chatter(models.Model):
    _name = 'delivery.route'
    _inherit = ['delivery.route','mail.thread','mail.activity.mixin']

class chatterr(models.Model):
    _name = 'route.lines'
    _inherit = ['route.lines','mail.thread','mail.activity.mixin']













