from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commercial_margin = fields.Monetary(
        string="Commercial Margin",
        compute="_compute_commercial_margin",
        help="Amount of margin based on calculated cost price of products",
    )
    commercial_margin_percentage = fields.Float(
        string="Commercial Margin Percentage",
        compute="_compute_commercial_margin",
        help="Margin % calculation based on calculated cost price",
    )

    @api.depends("order_line.commercial_margin", "amount_untaxed")
    def _compute_commercial_margin(self):
        if not all(self._ids):
            for order in self:
                order.commercial_margin = sum(
                    order.order_line.mapped("commercial_margin")
                )
                order.commercial_margin_percentage = (
                    order.amount_untaxed
                    and order.commercial_margin / order.amount_untaxed
                )
        else:
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env["sale.order.line"].read_group(
                [
                    ("order_id", "in", self.ids),
                ],
                ["commercial_margin", "order_id"],
                ["order_id"],
            )
            mapped_data = {
                m["order_id"][0]: m["commercial_margin"]
                for m in grouped_order_lines_data
            }
            for order in self:
                order.commercial_margin = mapped_data.get(order.id, 0.0)
                order.commercial_margin_percentage = (
                    order.amount_untaxed
                    and order.commercial_margin / order.amount_untaxed
                )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commercial_margin = fields.Monetary(
        string="Commercial Margin",
        help="Amount of margin based on calculated cost price of products",
    )
    commercial_margin_percentage = fields.Float(
        string="Commercial Margin Percentage",
        help="Margin % calculation based on calculated cost price",
    )

    @api.onchange("product_id", "product_uom_qty")
    def onchange_product_id(self):
        if self.product_id:
            self.commercial_margin_percentage = self.product_id.calculated_margin
            self.commercial_margin = (
                self.product_id.calculated_cost_price
                * (self.commercial_margin_percentage / 100)
                * self.product_uom_qty
            )

    # As we super called these methods, we got an error, so we had to override these compute methods to pass the
    # date_order field of sales order. This field is used to get the sale price from our custom model
    # product.sale_price. This context is used to _compute_base_price of product.pricelist.item model.
    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0 or (
                line.product_id.expense_policy == "cost" and line.is_expense
            ):
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                price = (
                    line.with_company(line.company_id)
                    .with_context(sale_order_date=self.order_id.date_order.date())
                    ._get_display_price()
                )
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    "sale",
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id,
                )

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_pricelist_item_id(self):
        for line in self:
            if (
                not line.product_id
                or line.display_type
                or not line.order_id.pricelist_id
            ):
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id.with_context(
                    sale_order_date=line.order_id.date_order.date()
                )._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )
