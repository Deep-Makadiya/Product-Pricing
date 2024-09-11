# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    calculated_cost_price = fields.Monetary(string="Calculated Cost Price",
                                            help="Field is calculated by sale_price model")
    calculated_margin = fields.Float(string="Calculated Margin",
                                     help="Margin % based on sale price and calculated cost price")
    product_extra_cost_ids = fields.One2many("product.extra_cost", "product_id")
    product_sale_price_ids = fields.One2many("product.sale_price", "product_id")

    def update_sale_price_cron(self):
        today_date = datetime.now().date()
        product_ids = self.search([("product_sale_price_ids", "!=", False)])
        for product in product_ids:
            # We are recalculating all sale prices associated with the product.
            # This may affect the server's/cron performance.
            for sale_price_id in product.product_sale_price_ids:
                sale_price_id.calculate_cost_price()

            # Update the Sales Price of the product.
            product_sale_price_ids = product.product_sale_price_ids.filtered(
                lambda sp: sp.start_date <= today_date and (sp.end_date >= today_date if sp.end_date else True))
            if product_sale_price_ids:
                product.lst_price = product_sale_price_ids[0].sale_price
