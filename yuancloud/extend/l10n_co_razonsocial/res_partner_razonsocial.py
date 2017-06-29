# -*- coding: utf-8 -*-

from yuancloud import models, fields, api, _


class ResPartnerRazonsocial(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends(
        'legal_entity_name',
        'firstname',
        'middlename',
        'first_lastname',
        'second_lastname'
    )
    def _copy_values(self):
        title = self.title.shortcut and ' ' + self.title.shortcut or ''
        if self.state == 'perjur':
            name = self.legal_entity_name and self.legal_entity_name or ''
            self.legal_denomination = name + title
        elif self.state == 'pernat':
            s1 = self.firstname and self.firstname + ' ' or ''
            s2 = self.middlename and self.middlename + ' ' or ''
            s3 = self.first_lastname and self.first_lastname + ' ' or ''
            s4 = self.second_lastname and self.second_lastname or ''
            self.legal_denomination = s1 + s2 + s3 + s4 + title
        else:
            self.legal_denomination = ''

    state = fields.Selection(
        (
            ('pernat', 'Persona Natural'),
            ('perjur', 'Persona Juridica')
        ),
        copy=False
    )
    legal_denomination = fields.Char(
        string='legal_name',
        readonly=True,
        store=True,
        compute='_copy_values'
    )
    legal_entity_name = fields.Char(
        states={
            'perjur': [('required', True)],
            'pernat': [('invisible', True)],
            False: [('invisible', True)]
        }
    )
    firstname = fields.Char(
        states={
            'pernat': [('required', True)],
            'perjur': [('invisible', True)],
            False: [('invisible', True)]
        }
    )
    middlename = fields.Char(
        states={
            'perjur': [('invisible', True)],
            False: [('invisible', True)]
        }
    )
    first_lastname = fields.Char(
        states={
            'pernat': [('required', True)],
            'perjur': [('invisible', True)],
            False: [('invisible', True)]
        }
    )
    second_lastname = fields.Char(
        states={
            'perjur': [('invisible', True)],
            False: [('invisible', True)]
        }
    )

    # Override from res.partner
    @api.multi
    def onchange_type(self, is_company):
        value = {}
        value['title'] = False
        if is_company:
            value['use_parent_address'] = False
            domain = {'title': [('domain', '=', 'partner')]}
        else:
            domain = {'title': [('domain', '=', 'contact')]}
            value['state'] = False
        return {'value': value, 'domain': domain}
