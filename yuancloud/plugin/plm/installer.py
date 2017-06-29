# -*- coding: utf-8 -*-
##############################################################################
#
#    yuancloud, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from yuancloud import fields, api, _, osv


class plm_installer(osv.osv.osv_memory):
    _name='plm.installer'
    _inherit='res.config.installer'
    __logger = logging.getLogger(_name)

    def default_get(self, cr, uid, fields, context=None):
        data=super(plm_installer, self).default_get(cr, uid, fields, context)
        data['exe_file']='http://sourceforge.net/projects/yuancloudplm/files/Client/yuancloudPlm(x64).exe/download'
        return data

    name        = fields.Char   (_('File name'), size=34)
    exe_name    = fields.Char   (_('File name'), size=128)
    plm         = fields.Boolean(_('yuancloud PLM Plug-in'), help=_("Product Life-Cycle Management Module."))
    exe_file    = fields.Char   (_('yuancloud PLM File download'), size=128, readonly=True, help=_("Product Life-Cycle Management Client file. Save this file and install this application."))
    description = fields.Text   (_('Description'), readonly=True)

    _defaults={
        'plm'           : False,
        'name'          : 'yuancloudPlm.exe',
        'description'   : """
                            To complete your installation follow these notes :
                             
                            * Configure yuancloud access capabilty adding Users to the group 'PLM / Integration' before to use Clients.
                            
                            * Download the yuancloud PLM Client file.
                            * Follow these steps to install Product Life-Cycle Management Client.
                                1. Double click on yuancloud PLM Client file.
                                2. Select language.
                                3. Select the directory where to install integrations.
                                4. Select the editor that has to be connected.
                            
                            * At editor startup yuancloud PLM menu and toolbar will be automatically loaded.
                            * At first time execution :
                                1. Click on Login button.
                                2. Insert data connection.
                            """
    }

plm_installer()