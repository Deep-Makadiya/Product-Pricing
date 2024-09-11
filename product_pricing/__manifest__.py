# #############################################################################
#
# 	Author: Cravit.
# 	Copyright 2023 Cravit
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU Affero General Public License as
# 	published by the Free Software Foundation, either version 3 of the
# 	License, or (at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU Affero General Public License for more details.
#
# 	You should have received a copy of the GNU Affero General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

# -*- coding: utf-8 -*-
{
    'name': "Product Pricing",

    'summary': "Product Pricing calculation based on suppliers defined and add extra costs",

    'description': """
    1. Defined Extra Costs for that product
#   2. Sale Price calculations on Recalc button based on BOMs if
#         defined or else from Vendor Pricelists and also add extra cost.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account', 'sale', 'purchase', 'stock', 'product'],

    # always loaded
    'data': [

        "security/ir.model.access.csv",
        "data/cron_data.xml",
        "views/product_supplierinfo_view.xml",
        "views/sale_order_view.xml",
        "views/product_view.xml",
        "views/product_extra_cost_type_view.xml",
        "views/product_extra_cost_view.xml",
        "views/product_sale_price_view.xml",

    ],
    'installable': True,
    'application': True,
}
