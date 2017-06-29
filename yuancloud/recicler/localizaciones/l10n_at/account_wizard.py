# -*- encoding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

# Copyright (C) conexus.at

from yuancloud import tools
from yuancloud.osv import osv
from yuancloud import addons

class AccountWizard_cd(osv.osv_memory):
	_inherit='wizard.multi.charts.accounts'
	
	_defaults = {
		'code_digits' : 0,
	}
