# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'PosBox Homepage',
    'version': '1.0',
    'category' : 'Offline 2 Online', #原分类 'Hardware Drivers',
    'sequence': 6,
    'website': 'http://www.yuancloud.cn/page/point-of-sale',
    'summary': 'A homepage for the PosBox',
    'description': """
PosBox Homepage
===============

This module overrides yuancloud web interface to display a simple
Homepage that explains what's the posbox and show the status,
and where to find documentation.

If you activate this module, you won't be able to access the 
regular yuancloud interface anymore. 

""",
    'depends': ['hw_proxy'],
    'installable': False,
    'auto_install': False,
}
