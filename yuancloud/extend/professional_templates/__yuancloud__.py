# -*- coding: utf-8 -*-
{
    'name': "Professional PO/RFQ/SO/SQ/D Note/Pickling List",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category' : 'Uncategorized',
    'version': '0.1',
    'price': 99,
    'currency': 'EUR',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/sale_order_reports.xml',
        'reports/purchase_order_reports.xml',
        'reports/rfq_reports.xml',
        'reports/delivery_reports.xml',
        'reports/stock_picking_report.xml',

        'sale_order/all_reports.xml',
        'sale_order/sale_order_view.xml',
        'sale_order/res_company_view.xml',
        'sale_order/yuancloud_template.xml',
        'sale_order/retro_template.xml',
        'sale_order/classic_template.xml',
        'sale_order/tva_template.xml',
        'sale_order/modern_template.xml',

        'purchase_order/all_reports.xml',
        'purchase_order/purchase_order_view.xml',
        'purchase_order/res_company_view.xml',
        'purchase_order/yuancloud_template.xml',
        'purchase_order/retro_template.xml',
        'purchase_order/classic_template.xml',
        'purchase_order/tva_template.xml',
        'purchase_order/modern_template.xml',


        'rfq/all_reports.xml',
        'rfq/rfq_view.xml',
        'rfq/res_company_view.xml',
        'rfq/yuancloud_template.xml',
        'rfq/retro_template.xml',
        'rfq/classic_template.xml',
        'rfq/tva_template.xml',
        'rfq/modern_template.xml',

        'delivery_note/all_reports.xml',
        'delivery_note/delivery_note_view.xml',
        'delivery_note/res_company_view.xml',
        'delivery_note/yuancloud_template.xml',
        'delivery_note/retro_template.xml',
        'delivery_note/classic_template.xml',
        'delivery_note/tva_template.xml',
        'delivery_note/modern_template.xml',

        'picking/all_reports.xml',
        'picking/picking_view.xml',
        'picking/res_company_view.xml',
        'picking/yuancloud_template.xml',
        'picking/retro_template.xml',
        'picking/classic_template.xml',
        'picking/tva_template.xml',
        'picking/modern_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
