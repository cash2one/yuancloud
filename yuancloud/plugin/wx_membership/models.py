# -*- coding: utf-8 -*-

from yuancloud import models, fields, api

# class wx_membership(models.Model):
#     _name = 'wx_membership.wx_membership'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100