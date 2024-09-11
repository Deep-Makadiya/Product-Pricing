# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductExtraCostPrice(models.Model):
    _name = 'product.extra_cost_type'
    _description = 'Product Extra Cost Type'
    _rec_name = "name"

    name = fields.Char(string="Name", help="Cost type used in product extra cost")
    active = fields.Boolean(string="Active", help="If cost type can be selected", default=True)
