# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
import this
from typing import Union, Any


from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError ,UserError




class SaleOrderStges(models.Model):
    _name = "sale.order.stages"
    _description = "Sale Order Stages"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string="Name")
    color = fields.Integer(string="Color", default=1)
    stage_key = fields.Char(required=True, translate=True, string="Stage Keys")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Stage name already exists !"),
    ]
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)


class SaleOrderHistory(models.Model):
    _name = "sale.order.history"
    _description = "Sale Order History"
    _order = "date_order desc"

    sale_reorder = fields.Boolean("Reorder")
    name = fields.Many2one("sale.order.line", "Sale Order Line")
    order_id = fields.Many2one(
        "sale.order",
        "Current Sale Order",
        readonly=False
    )


    status = fields.Selection(
        string="Status", related="name.order_id.state", readonly=True)
    date_order = fields.Datetime("Date", store=True)
    so_id = fields.Char("Sale Order", store=True)

     #adding customer
    partner_id = fields.Many2one(
        "res.partner",
        related="name.order_id.partner_id", store=True
    )


    invoice_status = fields.Selection(
        "sale.order",
        string="Invoice Status",
        related="name.order_id.invoice_status",
        store=True)

    product_id = fields.Many2one(
        "product.product",
        related="name.product_id",
        readonly=True,
        store=True
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        related="name.order_id.pricelist_id",
        readonly=True
    )
    price_unit = fields.Float(
        "Price",
        related="name.price_unit",
        readonly=True
    )
    new_price_unit = fields.Float(
        "New Price",
        compute='_compute_new_unit_price',
        readonly=True
    )
    product_uom_qty = fields.Float(
        "Quantity",
        related="name.product_uom_qty",
        readonly=True,
        store=True
    )

    # adding الجرد
    product_uom_qtyy = fields.Float(
        "الجرد",
        related="name.aljard",
        store=True
    )


    discount = fields.Float('Discount',
                            related='name.discount',
                            readonly=False)
    product_uom = fields.Many2one(
        "uom.uom",
        "Unit",
        related="name.product_uom",
        readonly=True,
        store=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency Id",
        related="name.currency_id"
    )
    price_subtotal = fields.Monetary(
        "Subtotal",
        readonly=True,
        related="name.price_subtotal"
    )
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    enable_reorder = fields.Boolean("Enable Reorder Button for Sale Order History", related="company_id.enable_reorder")

    alsarf = fields.Float("الصرف", compute="_compute_alsarf",store=True)
    @api.depends("product_uom_qty", "product_uom_qtyy", "alsarf", "order_id.partner_id")
    def _compute_alsarf(self):
        for record in self:

                   previous_record = self.search([('id', '<', record.id),('partner_id', '=', record.partner_id.id),('product_id', '=', record.product_id.id)],limit=1, order='id desc')
                   if previous_record:
                       record.alsarf = (previous_record.product_uom_qty + previous_record.product_uom_qtyy) - record.product_uom_qtyy
                   else:
                       record.alsarf = 0



    @api.depends('order_id.pricelist_id')
    def _compute_new_unit_price(self):

        for record in self:
            sh_new_price = 0.0
            if record.order_id and record.order_id.pricelist_id and record.product_id and record.order_id.partner_id and record.product_uom:
                price = record.order_id.pricelist_id._compute_price_rule(
                    record.product_id, record.product_uom_qty, uom_id=record.product_uom.id)
                sh_new_price = price.get(record.product_id.id)[0]
            record.new_price_unit = sh_new_price

    # Reorder Button

    def sales_reorder(self):
        vals = {
            "price_unit": self.price_unit,
            "product_uom_qty": self.product_uom_qty,
            "price_subtotal": self.price_subtotal
        }

        if self.product_id:
            vals.update({
                "name": self.product_id.display_name,
                "product_id": self.product_id.id
            })

        if self.product_uom:
            vals.update({"product_uom": self.product_uom.id})

        context = self._context.get('params')
        print("\n\nContext............", context)

        vals.update({"order_id": context.get('id')})

        so = self.env['sale.order'].sudo().browse(context.get('id'))
        so.write({'order_line': [(0, 0, vals)]})
        so._cr.commit()

        return {"type": "ir.actions.client", "tag": "reload"}

    # View Sale Order Button

    def view_sales_reorder(self):

        return{
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.name.order_id.id,
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    aljard = fields.Float('الجرد', store=True)

    #NOW LIN ORDER_ID IN SALE HISTOR "NAME" TO SALE ORDER LINE
    order_history_line = fields.One2many( 'sale.order.history', 'name', string='Order History Lines')
    #----------------------------------------------

    #then link alserf field to alsarf in sale order history by order id "order_history_line"
    alsarf = fields.Float('الصرف', related='order_history_line.alsarf',store=True, readonly=True)
    #---------------------------------------------
    #value from multiplied alsarf .
    multiplied_field = fields.Float('Multiplied Field', compute='_compute_multiplied_field', store=True, readonly=True)

    #-----------------------------------
    #this method to show vlue and updat the record for field alsarf in sales order line whenever user add new vallue in aljard field .
    @api.onchange('aljard')
    def _onchange_aljard(self):
        if self.order_id:
            previous_record = self.env['sale.order.history'].search([
                ('order_id', '=', self.order_id.id),
                ('product_id', '=', self.product_id.id)],
                limit=1, order='id desc')

            if previous_record:
                alsarf_value = (previous_record.product_uom_qty + previous_record.product_uom_qtyy) - self.aljard
                self.alsarf = alsarf_value
            else:
                self.alsarf = 0.0


    #-----------------------------------------------------
    #multiplied alsarf * price
    @api.depends('alsarf', 'order_history_line.price_unit')
    def _compute_multiplied_field(self):
        for record in self:
            record.multiplied_field = record.alsarf * record.order_history_line.price_unit

     #_______________________________________________________________
     #The create and write methods in the SaleOrderLine model are modified to trigger the computation of the total in the sale.order model
     # whenever a new record is created or an existing record is modified.
    @api.model
    def create(self, values):
        # Call the parent create method
        record = super(SaleOrderLine, self).create(values)

        # Call the method to update the total in sale order
        if record.order_id:
            record.order_id._compute_total_multiplied_field()

        return record
    def write(self, values):
        # Call the parent write method
        result = super(SaleOrderLine, self).write(values)

        # Call the method to update the total in sale order
        if self.order_id:
           self.order_id._compute_total_multiplied_field()

        return result


    #_______________________________________________________

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_multiplied_field_sum = fields.Float(
        string='المجموع المستحق للشريك',
        compute='_compute_total_multiplied_field_sum',
        store=True,
        help='Sum of total_multiplied_field_sale_order for all invoices related to the partner.'
    )

    # Define a related field to access the invoices related to the partner
    invoice_ids = fields.One2many(
        'account.move',
        'partner_id',
        string='Invoices',
        help='Invoices related to the partner.'
    )

    @api.depends('invoice_ids.total_multiplied_field_sale_order')
    def _compute_total_multiplied_field_sum(self):
        for partner in self:
            partner.total_multiplied_field_sum = sum(partner.invoice_ids.mapped('total_multiplied_field_sale_order'))

class AccountMove(models.Model):
    _inherit = "account.move"

# this field to link account move with sale order
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        help='Link to the corresponding sale order.',
    )

    # We creat new field name total_multiplied_field_sale_order to add value that in sale order inside it ..

    total_multiplied_field_sale_order = fields.Float(
        string='المجموع المستحق لهذه الفاتوره ',
        store=True,readonly=True  )

    # ovirraide the function that is in account move and add eidt
    # it that make the value in total_multiplied_field in sale order visible in new field in account move total_multiplied_field_sale_order.

    def action_post(self):
        result = super(AccountMove, self).action_post()

        # If sale_order_id is not set, try to find it based on the invoice lines
        if not self.sale_order_id and self.invoice_line_ids:
            sale_order_lines = self.invoice_line_ids.mapped('sale_line_ids')
            sale_orders = sale_order_lines.mapped('order_id')

            # If there is only one sale order linked to the invoice lines, set it as sale_order_id
            if len(sale_orders) == 1:
                self.sale_order_id = sale_orders

        # Retrieve the Sale Order linked to the Account Move
        sale_order = self.sale_order_id

        if sale_order:
            # Assign the value of total_multiplied_field from Sale Order to Account Move
            self.total_multiplied_field_sale_order = sale_order.total_multiplied_field

        return result

        # --------------------------------------------------
        # the way to show to balance of each invoice
        # --------------------------------------------------

    partner_id = fields.Many2one(
            'res.partner',
            string='Partner',
            store=True,
     readonly = True,
    )

        # Add a related field to display total_multiplied_field_sum from res.partner on account.move
    total_multiplied_field_partner = fields.Float(
            string='المجموع المستحق للشريك',
            related='partner_id.total_multiplied_field_sum',
            store=True,readonly = True,
        )

    @api.model
    def create(self, vals):
            move = super(AccountMove, self).create(vals)
            move.partner_id.total_multiplied_field_sum += move.total_multiplied_field_sale_order
            return move

    def write(self, vals):
            res = super(AccountMove, self).write(vals)
            for move in self:
                move.partner_id.total_multiplied_field_sum += move.total_multiplied_field_sale_order
            return res
        # total_balance = fields.Float(
        #    string='Total Balance',
        #   compute='_compute_total_balance',
        #    store=True,
        #        help='Sum of total_multiplied_field_sale_order for all invoices.'
        # )

        # New field to sum total_multiplied_field_sale_order for the same partner

   # total_multiplied_field_partner = fields.Float(
      #      string='المجموع المستحق لهذا الشريك',
      #      compute='_compute_total_multiplied_field_partner',
      #      store=True, readonly=True,
      #      help='Sum of total_multiplied_field_sale_order for the same partner.'
      #  )

        # to find total_multiplied_field_sale_order for each invoice
        #  @api.depends('total_multiplied_field_sale_order')
        #  def _compute_total_balance(self):
        #   for move in self:
        #   total_balance = sum(move.mapped('total_multiplied_field_sale_order'))
        #   move.total_balance = total_balance

        # to find total_balance for all invoice
   # @api.depends('total_multiplied_field_sale_order')
   # def _compute_total_multiplied_field_partner(self):
      #  for move in self:
            # Filter account moves based on the partner_id
         #   moves_with_same_partner = self.env['account.move'].search([
          #      ('partner_id', '=', move.partner_id.id),
          #  ])

            # Calculate the total_multiplied_field_sale_order for the filtered account moves
          #  total_multiplied_field_partner_sum = sum(
           #     moves_with_same_partner.mapped('total_multiplied_field_sale_order'))

            # Update the total_multiplied_field_partner for all moves with the same partner_id
          #  for move_with_same_partner in moves_with_same_partner:
          #      move_with_same_partner.total_multiplied_field_partner = total_multiplied_field_partner_sum

#--------------------------------------------------

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_history_line = fields.One2many(
        "sale.order.history",
        "order_id",
        string="Order History",
        compute="_compute_sale_order_history",
    )
    #----------------------------------------
    # We add total_multiplied_field to sale order which comput sum for total multiple field that is defid already in sales order line

    total_multiplied_field = fields.Float('Total Multiplied Field', compute='_compute_total_multiplied_field',
                                        store=True, readonly=True)

    @api.model
    @api.depends('order_line.multiplied_field')
    def _compute_total_multiplied_field(self):
        for order in self:
            total_before_tax = sum(order.order_line.mapped('multiplied_field'))
            tax_percentage = 0.15  # 15% tax

            # Calculate the total including tax
            order.total_multiplied_field = total_before_tax * (1 + tax_percentage)

    enable_reorder = fields.Boolean(
        "Enable Reorder Button for Sale Order History", related="company_id.enable_reorder")

    # All Lines Reorder Button

    def action_all_sale_reorder(self):
        for rec in self.order_history_line:
            if self.enable_reorder:
                vals = {
                    "price_unit": rec.price_unit,
                    "product_uom_qty": rec.product_uom_qty,
                    "price_subtotal": rec.price_subtotal
                }

                if rec.product_id:
                    vals.update({
                        "name": rec.product_id.display_name,
                        "product_id": rec.product_id.id
                    })

                if rec.product_uom:
                    vals.update({"product_uom": rec.product_uom.id})

                if self.id:
                    vals.update({'order_id': self.id})

                self.write({'order_line': [(0, 0, vals)]})
                self._cr.commit()

        return{"type": "ir.actions.client", "tag": "reload"}

    @api.model
    @api.onchange("partner_id")
    def _onchange_partner(self):
        self.order_history_line = None
        if self.partner_id:
            partners = []
            domain = []

            partners.append(self.partner_id.id)

            if self.env.company.day:
                day = self.env.company.day
                Display_date = datetime.today() - relativedelta(days=day)
                domain.append(("date_order", ">=", Display_date),)

            stages = []

            if self.env.company.stages:
                for stage in self.env.company.stages:
                    if stage.stage_key:
                        stages.append(stage.stage_key)
                domain.append(("state", "in", stages),)

            if self.env.user.company_id.sh_sale_configuration_limit:
                limit = self.env.user.company_id.sh_sale_configuration_limit
            else:
                limit = None

            if self.partner_id.child_ids:
                for child in self.partner_id.child_ids:
                    partners.append(child.id)

            if partners:
                domain.append(("partner_id", "in", partners),)

            if self._origin:
                domain.append(("id", "=", self._origin.id))

            sale_order_search = self.env["sale.order"].search(
                domain,
                limit=limit,
                order="date_order desc",)

            sale_ordr_line = []
            if sale_order_search:
                for record in sale_order_search:

                    if record.order_line:
                        for rec in record.order_line:

                            sale_ordr_line.append((0, 0, {
                                # "order_id":record.id,
                                "so_id": record.name,
                                "name": rec.id,
                                'date_order': record.date_order,
                                'discount': rec.discount,
                                "product_id": rec.product_id.id,
                                "pricelist_id": record.pricelist_id.id,
                                "price_unit": rec.price_unit,
                                "product_uom_qty": rec.product_uom_qty,
                                "product_uom": rec.product_uom.id,
                                "price_subtotal": rec.price_subtotal,
                                "status": rec.state,
                            }))

            self.order_history_line = sale_ordr_line

    def _compute_sale_order_history(self):
        for vals in self:
            vals.order_history_line = None
            if vals.partner_id:
                partners = []
                domain = []

                partners.append(vals.partner_id.id)

                history_domain = []
                if self.env.company.day:
                    day = self.env.company.day
                    Display_date = datetime.today() - relativedelta(days=day)
                    domain.append(("date_order", ">=", Display_date),)
                    history_domain.append(("date_order", ">=", Display_date),)

                stages = []

                if self.env.company.stages:
                    for stage in self.env.company.stages:
                        if stage.stage_key:
                            stages.append(stage.stage_key)
                    domain.append(("state", "in", stages),)
                    history_domain.append(("status", "in", stages),)

                if self.env.user.company_id.sh_sale_configuration_limit:
                    limit = self.env.user.company_id.sh_sale_configuration_limit
                else:
                    limit = None

                if vals.partner_id.child_ids:
                    for child in vals.partner_id.child_ids:
                        partners.append(child.id)

                # if vals.partner_id.parent_id:
                #     partners.append(vals.partner_id.parent_id.id)
                #     for child in vals.partner_id.parent_id.child_ids:
                #         partners.append(child.id)

                if partners:
                    domain.append(("partner_id", "in", partners),)
                    history_domain.append(
                        ('order_id.partner_id', 'in', partners),)
                if vals.id:
                    domain.append(("id", "=", vals.id))

                sale_order_search = self.env["sale.order"].search(
                    domain,
                    limit=limit,
                    order="date_order desc",)

                history_domain.append(
                    ('order_id', 'in', sale_order_search.ids),)

                if sale_order_search:
                    for record in sale_order_search:
                        history_ids = self.env['sale.order.history'].sudo().search(
                            history_domain,
                            limit=limit,
                            order="date_order desc",
                        )
                        if record.order_line:
                            for rec in record.order_line:
                                if rec.id in history_ids.name.ids:
                                    vals.order_history_line = [
                                        (6, 0, history_ids.ids)]
                                else:
                                    history_vals = {
                                        "order_id": record.id,
                                        "so_id": record.name,
                                        "name": rec.id,
                                        'date_order': record.date_order,
                                        'discount': rec.discount,
                                        "product_id": rec.product_id.id,
                                        "pricelist_id": record.pricelist_id.id,
                                        "price_unit": rec.price_unit,
                                        "product_uom_qty": rec.product_uom_qty,
                                        "product_uom": rec.product_uom.id,
                                        "price_subtotal": rec.price_subtotal,
                                        "status": rec.state,
                                    }
                                    res = self.env['sale.order.history'].sudo().create(
                                        history_vals)
