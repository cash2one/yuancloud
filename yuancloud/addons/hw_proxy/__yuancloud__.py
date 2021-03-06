# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'Hardware Proxy',
    'version': '1.0',
    'category' : 'Offline 2 Online', #原分类 'Point Of Sale',
    'sequence': 6,
    'summary': 'Connect the Web Client to Hardware Peripherals',
    'website': 'http://www.yuancloud.cn/page/point-of-sale',
    'description': """
Hardware Poxy
=============

This module allows you to remotely use peripherals connected to this server.

This modules only contains the enabling framework. The actual devices drivers
are found in other modules that must be installed separately. 

""",
    'depends': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
