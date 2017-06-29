# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'Weighting Scale Hardware Driver',
    'version': '1.0',
    'category' : 'Offline 2 Online', #‘≠∑÷¿‡ 'Hardware Drivers',
    'sequence': 6,
    'summary': 'Hardware Driver for Weighting Scales',
    'website': 'http://www.yuancloud.cn/page/point-of-sale',
    'description': """
Weighting Scale Hardware Driver
================================

This module allows the point of sale to connect to a scale using a USB HSM Serial Scale Interface,
such as the Mettler Toledo Ariva.

""",
    'depends': ['hw_proxy'],
    'external_dependencies': {'python': ['serial']},
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
