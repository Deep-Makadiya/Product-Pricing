# -*- coding: utf-8 -*-
import datetime

from odoo import fields, models, api


class ProductSalePrice(models.Model):
    _name = 'product.sale_price'
    _description = 'Product Sale Price'
    _rec_name = "name"

    name = fields.Char(string="Name")
    sequence = fields.Integer('Sequence', default=1, help="Assigns the priority to the list of product sale price.")
    product_id = fields.Many2one("product.product")
    currency_id = fields.Many2one("res.currency")
    start_date = fields.Date(string="Start Date", help="Start date of the sale price")
    end_date = fields.Date(string="End Date", help="End date of the sale price, leave blank if there is no end date")
    calculated_cost_price = fields.Monetary(string="Calculated Cost Price",
                                            help="Cost will be calculated based on several elements")
    sale_price_calculation = fields.Selection([('margin', 'Margin'), ('margin_percentage', 'Margin Percentage'), ('sale_price', 'Sale Price')])
    margin = fields.Monetary(string="Margin", help="Margin Amount")
    margin_percentage = fields.Float(string="Margin Percentage", help="Margin %")
    sale_price = fields.Monetary(string="Sale Price", help="Set price or based on margin")
    recommended_sale_price_calculation = fields.Selection([('recommended_sale_price', 'Recommended Sale Price'), (
    'recommended_sale_price_margin_perc', 'Recommended Sale Price Margin Perc')])
    recommended_sale_price_margin_perc = fields.Float(string="Recommended Sale Price Margin Percentage",
                                                      help="Recommended sale price margin %")
    recommended_sale_price = fields.Monetary(string="Recommended Sale Price",
                                             help="Recommended sale price (including VAT)")

    _sql_constraints = [
        ('check_date', 'check (end_date >= start_date)', 'The End Date should not be smaller than Start Date!'),
    ]

    def calculate_cost_price(self):
        self.ensure_one()
        # Calculate Cost Price based on BOM lines and Suppliers
        product_extra_cost_ids = self.get_product_extra_cost_lines()
        total_cost = 0
        for product_extra_cost in product_extra_cost_ids:
            total_cost += product_extra_cost.cost
        if self.product_id.bom_ids:
            self.product_id.button_bom_cost()
            self.calculated_cost_price = self.product_id.standard_price + total_cost
        if not self.product_id.bom_ids:
            supplier_ids = self.get_product_supplier_lines()
            supplier_for_marg_calc = []
            for supplier in supplier_ids:
                if supplier.margin_calc:
                    supplier_for_marg_calc.append(supplier)
            if supplier_for_marg_calc:
                self.calculated_cost_price = supplier_for_marg_calc[0].price + total_cost
            elif supplier_ids:
                self.calculated_cost_price = supplier_ids[0].price + total_cost
            else:
                self.calculated_cost_price = (self.product_id.seller_ids[0].price + total_cost) if self.product_id.seller_ids else 0

        # Calculate Sale Price based on Margin and Margin %
        if self.sale_price_calculation == 'margin':
            self.sale_price = self.calculated_cost_price + self.margin
            self.margin_percentage = (self.margin * 100) / (self.calculated_cost_price or 1)
        elif self.sale_price_calculation == 'margin_percentage':
            self.sale_price = self.calculated_cost_price + (self.calculated_cost_price * (self.margin_percentage / 100))
            self.margin = (self.margin_percentage / 100) * self.calculated_cost_price
        elif self.sale_price_calculation == 'sale_price':
            self.margin = abs(self.sale_price - self.calculated_cost_price)
            self.margin_percentage = (abs(self.sale_price - self.calculated_cost_price) * 100) / (self.calculated_cost_price or 1)

        # Set lst_price, calculated_cost_price and calculated_margin in product -> General Information Tab
        end_date = self.end_date or datetime.date(9999, 12, 31)
        if self.start_date and end_date and (self.start_date <= datetime.date.today() <= end_date):
            self.product_id.lst_price = self.sale_price
            self.product_id.calculated_cost_price = self.calculated_cost_price
            self.product_id.calculated_margin = self.margin_percentage

        # Calculate Recommended Sale Price based on Recommended Sale Price and Recommended Sale Price Margin %
        if self.recommended_sale_price_calculation == 'recommended_sale_price_margin_perc':
            recommended_sale_price = self.calculated_cost_price + (
                    self.calculated_cost_price * (self.recommended_sale_price_margin_perc / 100))
            sale_price_incl_tax = self.product_id.taxes_id.compute_all(recommended_sale_price, product=self.product_id,
                                                                       partner=self.product_id.env['res.partner'])
            self.recommended_sale_price = sale_price_incl_tax.get('total_included')
        elif self.recommended_sale_price_calculation == 'recommended_sale_price':
            self.recommended_sale_price_margin_perc = ((
                                                               self.sale_price - self.calculated_cost_price) / (self.sale_price or 1)) * 100

    def get_product_supplier_lines(self):
        self.ensure_one()
        supplier_ids_final = []
        end_date = self.end_date or datetime.date(9999, 12, 31)
        if self.start_date and end_date:
            supplier_ids = self.product_id.seller_ids.filtered(
                lambda supplier_id: ((supplier_id.date_start <= end_date) if supplier_id.date_start else False))
            for supplier in supplier_ids:
                if supplier.date_end and supplier.date_end < end_date:
                    continue
                else:
                    supplier_ids_final.append(supplier)
        return supplier_ids_final

    def get_product_extra_cost_lines(self):
        self.ensure_one()
        product_extra_cost_ids_final = []
        end_date = self.end_date or datetime.date(9999, 12, 31)
        if self.start_date and end_date:
            product_extra_cost_ids = self.product_id.product_extra_cost_ids.filtered(
                lambda cost: ((cost.start_date <= end_date) if cost.start_date else False))
            for cost in product_extra_cost_ids:
                if cost.end_date and cost.end_date < end_date:
                    continue
                else:
                    product_extra_cost_ids_final.append(cost)
        return product_extra_cost_ids_final

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            sale_price_ids = rec.product_id.product_sale_price_ids.filtered(lambda line: not line.end_date and line.id != rec.id and line.start_date < rec.start_date)
            if sale_price_ids:
                sale_price_ids.write({'end_date': rec.start_date - datetime.timedelta(days=1)})
        return res