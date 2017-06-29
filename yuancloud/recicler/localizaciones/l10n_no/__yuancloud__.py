# -*- encoding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    "name" : "Norway - Accounting",
    "version" : "1.1",
    "author" : "Rolv Råen",
    "category" : "Localization/Finance",
    "description": """This is the module to manage the accounting chart for Norway in YuanCloud.

Updated for YuanCloud 9 by Bringsvor Consulting AS <www.bringsvor.com>
""",
    "depends" : ["account", "base_iban", "base_vat"],
    "demo_xml" : [],
    "data" : ["account_chart.xml",
                    'account_tax.xml','account_chart_template.yml'],
    "active": False,
    "installable": True
}
