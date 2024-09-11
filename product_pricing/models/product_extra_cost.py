# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductExtraCost(models.Model):
    _name = 'product.extra_cost'
    _description = 'Product Extra Cost'
    _rec_name = "extra_cost_type_id"

    sequence = fields.Integer('Sequence', default=1, help="Assigns the priority to the list of product extra cost.")
    extra_cost_type_id = fields.Many2one('product.extra_cost_type', string="Extra Cost Type", help="Select the cost type")
    currency_id = fields.Many2one("res.currency")
    start_date = fields.Date(string="Start Date", help="Start date of the extra cost")
    end_date = fields.Date(string="End Date", help="End date of the cost, leave blank if there is no end date")
    cost = fields.Monetary(string="Cost", help="Extra cost amount for this cost type")
    product_id = fields.Many2one('product.product', string="Product")

    _sql_constraints = [
        ('check_date', 'check (end_date >= start_date)', 'The End Date should not be smaller than Start Date!'),
    ]
