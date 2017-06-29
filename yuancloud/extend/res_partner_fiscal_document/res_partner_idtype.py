# -*- encoding: utf-8 -*-

from yuancloud import models, fields # , api, _


class ResPartnerIDtype(models.Model):
    _name = 'res.partner.idtype'
    _description = 'Identificacion Tipo de Documento'
    _order = 'sequence'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    note = fields.Text()
    on_company = fields.Boolean(
        string=u'On Company?',
        default=True,
        help="Id type for use on Company"
    )
    on_contact = fields.Boolean(
        string=u'On Contact?',
        default=True,
        help="Id type for use on Contacts"
    )
    on_merchant = fields.Boolean(
        string=u'On Merchants?',
        default=True,
        help="Id type for use on Merchants"
    )
