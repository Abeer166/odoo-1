16.0.1 ( Date : 8 September 2022 )
-----------------------------------

- Initial Release

16.0.2 ( Date : 7 March 2023 )
-----------------------------------

[Add] Minor Bug Fixed.

16.0.3 ( Date : 13 March 2023 )
-----------------------------------

[Add] Display Sale Order History on already created Sale Orders also.

16.0.4 ( Date : 18 May 2023 )
-------------------------------

- [fix] Small bug fixed.

sh_sale_order_history/models/sale_order_history.py", line 94, in _compute_new_unit_price
    [(record.product_id, record.product_uom_qty, record.order_id.partner_id,)], uom_id=record.product_uom.id)
odoo/odoo/addons/product/models/product_pricelist.py", line 166, in _compute_price_rule
    items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)                                                     ^
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts.



