# -*- coding: utf-8 -*-

from yuancloud import models, fields, api

# class wx_qr_pay(models.Model):
#     _name = 'wx_qr_pay.wx_qr_pay'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100