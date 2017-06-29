# -*- coding: utf-8 -*-

from yuancloud import models, fields, api

# class wx_managed_authorization(models.Model):
#     _name = 'wx_managed_authorization.wx_managed_authorization'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100