# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Fleet Management',
    'version' : '0.1',
    'author' : 'YuanCloud S.A.',
    'sequence': 165,
    'category' : 'Office Automation',
    'website' : 'http://www.yuancloud.cn/page/fleet',
    'summary' : 'Vehicle, leasing, insurances, costs',
    'description' : """
Vehicle, leasing, insurances, cost
==================================
With this module, YuanCloud helps you managing all your vehicles, the
contracts associated to those vehicle as well as services, fuel log
entries, costs and many other features necessary to the management 
of your fleet of vehicle(s)

Main Features
-------------
* Add vehicles to your fleet
* Manage contracts for vehicles
* Reminder when a contract reach its expiration date
* Add services, fuel log entry, odometer values for all vehicles
* Show all costs associated to a vehicle or to a type of service
* Analysis graph for costs
""",
    'depends' : [
        'base',
        'mail',
    ],
    'data' : [
        'security/fleet_security.xml',
        'security/ir.model.access.csv',
        'fleet_view.xml',
        'fleet_cars.xml',
        'fleet_data.xml',
        'fleet_board_view.xml',
    ],

    'demo': ['fleet_demo.xml'],

    'installable' : True,
    'application' : False,
}
