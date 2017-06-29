# -*- coding: utf-8 -*-

from yuancloud import models, fields, api

# class wx_qr(models.Model):
#     _name = 'wx_qr.wx_qr'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100