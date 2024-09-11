from odoo import models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _compute_base_price(self, product, quantity, uom, date, target_currency):
        price = super()._compute_base_price(
            product, quantity, uom, date, target_currency
        )
        order_date = self._context.get("sale_order_date")
        if product._name == "product.product" and order_date:
            product_sale_price_ids = product.product_sale_price_ids.filtered(
                lambda sp: sp.start_date <= order_date
                and (sp.end_date >= order_date if sp.end_date else True)
            )
            if product_sale_price_ids:
                return product_sale_price_ids[0].sale_price
        return price
