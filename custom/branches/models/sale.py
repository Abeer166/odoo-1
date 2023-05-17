
from datetime import timedelta
from itertools import groupby
from markupsafe import Markup

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo.tools.sql import create_index

from odoo.addons.payment import utils as payment_utils

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

INVOICE_STATUS = [
    ('upselling', 'Upselling Opportunity'),
    ('invoiced', 'Fully Invoiced'),
    ('to invoice', 'To Invoice'),
    ('no', 'Nothing to Invoice')
]

from odoo.addons.sale.models.sale_order import SaleOrder as sale


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_branch_id(self):
        branch_id = self.branch_id
        if self._context.get('default_branch_id'):
            branch_id = self._context.get('default_branch_id')
        if not self._context.get('default_branch_id'):
            if self.env.user.branch_id:
                branch_id = self.env.user.branch_id.id
            elif self.env.user.branch_ids and not self.env.user.branch_id:
                branches = self.env['res.branch'].search([('user_ids', '=', self.env.user.id),('company_id', '=', self.env.company.id)])
                if branches:
                    branch_id = branches[0].id
        return branch_id

   

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                branch = vals.get("branch_id")
                company = vals.get("company_id")
                if branch:
                    use_custom_sequence = self.env['res.branch'].browse(branch).use_custom_sequence
                    activate_general_sequence = self.env['res.company'].browse(company).activate_general_sequence
                    so_custom_sequence = self.env['res.branch'].browse(branch).so_custom_sequence
                    gen_so_sequence_id = self.env['res.company'].browse(company).gen_so_sequence_id
                    if use_custom_sequence:
                        if so_custom_sequence:
                            sequence_id = self.env['res.branch'].browse(branch).so_sequence_id
                            if sequence_id:
                                vals["name"] = sequence_id._next() or _('New')
                        if not so_custom_sequence:
                            if activate_general_sequence:
                                if gen_so_sequence_id:
                                    sequence_id = self.env['res.company'].browse(company).gen_so_sequence_id
                                    if sequence_id:
                                        vals["name"] = sequence_id._next() or _('New')
                    if not use_custom_sequence:
                        if activate_general_sequence:
                            if gen_so_sequence_id:
                                sequence_id = self.env['res.company'].browse(company).gen_so_sequence_id
                                if sequence_id:
                                    vals["name"] = sequence_id._next() or _('New')
        return super(SaleOrder, self).create(vals_list)


    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        for order in self:
            if order.is_branch and not order.branch_id:
                order.update({
                    'warehouse_id': False,
                    'journal_id': False,
                    # 'partner_id': False,
                })
                return
            if order.branch_id:
                warehouse = self.env['stock.warehouse'].search([('branch_id', '=', order.branch_id.id)])
                journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', order.company_id.id),'|',('branch_ids', '=', order.branch_id.id),('branch_ids', '=', False)])
                # partner = self.env['res.partner'].search([('type', '!=', 'private'), ('company_id', 'in', (False, order.company_id.id)),'|',('branch_ids', '=', order.branch_id.id),('branch_ids', '=', False)])
                order.update({
                    'warehouse_id': False,
                    'journal_id': False,
                    # 'partner_id': False,
                })
                if warehouse:            
                            order.update({
                            'warehouse_id': warehouse[0].id,
                            })
                            self.onchange_warehouse_id()
                if journal:            
                            order.update({
                            'journal_id': journal[0].id,
                            })
                # if partner:            
                #             order.update({
                #             'partner_id': partner[0].id,
                #             })

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.company_id.is_branch and not self._context.get('default_branch_id'):
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            self.warehouse_id = False
            if self.env.user.branch_id:
                self.branch_id = self.env.user.branch_id.id
                self._onchange_branch_id()
            if not self.env.user.branch_id and len(branches) > 0:
                self.branch_id = branches[0]
                self._onchange_branch_id()
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        res = super(SaleOrder, self)._onchange_company_id()
  
    def _get_invoice_grouping_keys(self):
        return ['company_id', 'partner_id', 'currency_id','branch_id']
  
    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            picking = self.env['stock.picking.type'].search([('warehouse_id', '=', self.warehouse_id.id),('code', '=', 'outgoing')])
            self.picking_type_id = False
            if self.warehouse_id and picking:
                self.picking_type_id = picking[0].id
            return {'domain': {'picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            return {'domain': {'picking_type_id': []}}



    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),'|', ('branch_ids', '=', False), ('branch_ids', '=', branch_id)]")

    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),'|', ('branch_ids', '=', False), ('branch_ids', '=', branch_id)]")

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)),'|',('branch_ids', '=', branch_id),('branch_ids', '=', False)]")

    branch_id = fields.Many2one("res.branch", string='Branch', default=_default_branch_id, tracking=True,store=True)
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )

    is_branch = fields.Boolean(related='company_id.is_branch')

    @api.depends('user_id', 'company_id')
    def _compute_warehouse_id(self):
        for order in self:
            if self.company_id.is_branch:
                self._onchange_branch_id()
            else:
                default_warehouse_id = self.env['ir.default'].with_company(
                    order.company_id.id).get_model_defaults('sale.order').get('warehouse_id')
                if order.company_id and order.company_id != order._origin.company_id:
                    warehouse = default_warehouse_id
                else:
                    warehouse = self.env['stock.warehouse']
                if order.state in ['draft', 'sent']:
                    order.warehouse_id = warehouse or order.user_id.with_company(order.company_id.id)._get_default_warehouse_id()
                # In case we create a record in another state (eg: demo data, or business code)
                if not order.warehouse_id:
                    order.warehouse_id = self.env.user._get_default_warehouse_id()

    journal_id = fields.Many2one("account.journal",string="Journal",copy=True, readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    inv_custom_journal = fields.Boolean(related='branch_id.inv_custom_journal')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.journal_id:
            invoice_vals.update({'journal_id': self.journal_id.id,'branch_readonly': True,'branch_id': self.branch_id.id, 'branch_type_id': self.branch_id.type_id.id, 'branch_group_id': self.branch_id.group_id.id, 'branch_state_id': self.branch_id.state_id.id, })
        return invoice_vals

    @api.model
    def _default_picking_type(self):
        if self.warehouse_id:
            picking = self.env['stock.picking.type'].search([('warehouse_id', '=', self.warehouse_id.id),('code', '=', 'outgoing')])
            self.picking_type_id = False
            if self.warehouse_id and picking:
                self.picking_type_id = picking[0].id
            return {'domain': {'picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            self.picking_type_id = False

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver From', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, default=_default_picking_type, domain="[('warehouse_id', '=', warehouse_id),('code', '=', 'outgoing')]",
        help="This will determine operation type of outgoing shipment")


    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.order_id.branch_id:
            res.update({'branch_id': self.order_id.branch_id.id,'branch_group_id': self.order_id.branch_id.group_id.id,'branch_type_id': self.order_id.branch_id.type_id.id,'branch_state_id': self.order_id.branch_id.state_id.id,})
        return res


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'
  
    branch_id = fields.Many2one('res.branch',related='order_id.branch_id', store=True)
    is_branch = fields.Boolean(related='order_id.is_branch')
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type',related='branch_id.type_id',store=True)
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group',related='branch_id.group_id',store=True)
    branch_state_id = fields.Many2one("res.country.state", string='Branch State',related='branch_id.state_id',store=True )



class SaleAdvancePayment(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePayment, self)._create_invoice(order, so_line, amount)
        if res and order:
            res.write({'branch_id': order.branch_id.id,'branch_type_id': order.branch_id.type_id.id,'branch_group_id': order.branch_id.group_id.id,'branch_state_id': order.branch_id.state_id.id,})
        return res



class SaleReport(models.Model):
    _inherit = "sale.report"


    branch_id = fields.Many2one('res.branch',string="Branch" )
    branch_type_id = fields.Many2one('account.branch.type' ,string='Branch Business Type')
    branch_group_id = fields.Many2one('account.branch.group',string='Branch Group')
    branch_state_id = fields.Many2one("res.country.state", string='Branch State')


    def _select_additional_fields(self):
        res = super(SaleReport, self)._select_additional_fields()
        res['branch_id'] = "s.branch_id"
        res['branch_group_id'] = "s.branch_group_id"
        res['branch_type_id'] = "s.branch_type_id"
        res['branch_state_id'] = "s.branch_state_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.branch_type_id, s.branch_group_id, s.branch_id, s.branch_state_id"""
        return res

