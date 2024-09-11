# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    margin_calc = fields.Boolean(string="For Margin Calc")
