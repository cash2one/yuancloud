# -*- coding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 2010 OmniaSolutions (<http://omniasolutions.eu>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import os
import time
import random
import string
import StringIO

from book_collector import BookCollector, packDocuments
from yuancloud.report.interface import report_int
from yuancloud import pooler, _
from yuancloud.exceptions import UserError


class component_custom_report(report_int):
    """
        Return a pdf report of each printable document attached to given Part ( level = 0 one level only, level = 1 all levels)
    """
    def create(self, cr, uid, ids, datas, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        docRepository = self.pool.get('plm.document')._get_filestore(cr)
        componentType = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        msg = "Printed by " + \
            str(user.name) + " : " + str(time.strftime("%d/%m/%Y %H:%M:%S"))
        output = BookCollector(
            jumpFirst=False, customTest=(False, msg), bottomHeight=10)
        documents = []
        components = componentType.browse(cr, uid, ids, context=context)
        for component in components:
            documents.extend(component.linkeddocuments)
        if len(documents):
            return packDocuments(docRepository, documents, output)
        if context.get("raise_report_warning", True):
            raise UserError(_("No Document found"))

component_custom_report('report.product.product.pdf')


class component_one_custom_report(report_int):
    """
        Return a pdf report of each printable document attached to children in a Bom ( level = 0 one level only, level = 1 all levels)
    """

    def create(self, cr, uid, ids, datas, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        docRepository = self.pool.get('plm.document')._get_filestore(cr)
        componentType = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        msg = "Printed by " + \
            str(user.name) + " : " + str(time.strftime("%d/%m/%Y %H:%M:%S"))
        output = BookCollector(
            jumpFirst=False, customTest=(False, msg), bottomHeight=10)
        children = []
        documents = []
        components = componentType.browse(cr, uid, ids, context=context)
        for component in components:
            documents.extend(component.linkeddocuments)
            idcs = componentType._getChildrenBom(
                cr, uid, component, 0, 1, context=context)
            children = componentType.browse(cr, uid, idcs, context=context)
            for child in children:
                documents.extend(child.linkeddocuments)
        if len(documents):
            return packDocuments(docRepository, list(set(documents)), output)
        if context.get("raise_report_warning", True):
            raise UserError(_("No Document found"))

component_one_custom_report('report.one.product.product.pdf')


class component_all_custom_report(report_int):
    """
        Return a pdf report of each printable document attached to children in a Bom ( level = 0 one level only, level = 1 all levels)
    """

    def create(self, cr, uid, ids, datas, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        docRepository = self.pool.get('plm.document')._get_filestore(cr)
        componentType = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        msg = "Printed by " + \
            str(user.name) + " : " + str(time.strftime("%d/%m/%Y %H:%M:%S"))
        output = BookCollector(
            jumpFirst=False, customTest=(False, msg), bottomHeight=10)
        children = []
        documents = []
        components = componentType.browse(cr, uid, ids, context=context)
        for component in components:
            documents.extend(component.linkeddocuments)
            idcs = componentType._getChildrenBom(
                cr, uid, component, 1, context=context)
            children = componentType.browse(cr, uid, idcs, context=context)
            for child in children:
                documents.extend(child.linkeddocuments)
        if len(documents):
            return packDocuments(docRepository,
                                 list(set(documents)),
                                 output)
        if context.get("raise_report_warning", True):
            raise UserError(_("No Document found"))

component_all_custom_report('report.all.product.product.pdf')


class component_custom_report_latest(report_int):
    """
        Return a pdf report of each printable document attached to given Part ( level = 0 one level only, level = 1 all levels)
    """

    def create(self, cr, uid, ids, datas, context={}):
        self.pool = pooler.get_pool(cr.dbname)
        objTemplateDoc = self.pool.get('plm.document')
        docRepository = objTemplateDoc._get_filestore(cr)
        componentType = self.pool.get('product.product')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        msg = "Printed by " + \
            str(user.name) + " : " + str(time.strftime("%d/%m/%Y %H:%M:%S"))
        output = BookCollector(jumpFirst=False,
                               customTest=(False, msg),
                               bottomHeight=10)
        documents = []
        components = componentType.browse(cr, uid, ids, context=context)
        for component in components:
            for idDoc in component.linkeddocuments:
                if idDoc.state in ['released', 'undermodify']:
                    documents.extend(idDoc)
        if len(documents):
            return packDocuments(docRepository, documents, output)
        if context.get("raise_report_warning", True):
            raise UserError(_("No Document found"))
        return False, False

component_custom_report_latest('report.product.product.pdf.latest')
