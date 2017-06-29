# -*- encoding: utf-8 -*-
from yuancloud import models, fields, api # , _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    dom = "['|',                                      " \
          "  ('on_contact' ,'!=', is_company        )," \
          "  '|',                                     " \
          "   '&',                                    " \
          "    ('on_company' , '=', is_company      )," \
          "    ('on_company' , '=', state=='perjur' )," \
          "   '&',                                    " \
          "    ('on_merchant', '=', state=='pernat' )," \
          "    ('on_merchant', '=', is_company      )]"

    fiscal_id_type = fields.Many2one(
        'res.partner.idtype',
        string=u'Tipo de documento',
        domain=dom,
    )
    fiscal_id = fields.Char(
        string=u'Nro Documento',
        # compute='validateformatcopy',
    )
    fiscal_id_doc = fields.Binary(
        string=u'Adjunto Escaneado',
        help="Sube tu documento adjunto "
             "Preferiblemente en formato PDF"
             "Esto te permite, ahorrar espacio en disco "
             "y concatenar varios documentos"
    )

    @api.one
    @api.onchange(
        'fiscal_id_type',
        'fiscal_id',
        'is_company',
    )
    def validateformatcopy(self):
        # CASE: Current ID Type is not applicable on Merchant
        if self.is_company and self.state == 'pernat':
            if not self.fiscal_id_type.on_merchant:
                # Get the first valid ID type (remember: ordered by sequence)
                self.fiscal_id_type = self.env['res.partner.idtype'].search(
                    [('on_merchant', '=', True)], limit=1).id
                self.fiscal_id = None  # Reset ID value
        # CASE: Current ID Type is not applicable on Company
        if self.is_company and self.state == 'perjur':
            if not self.fiscal_id_type.on_company:
                # Get the first valid ID type (remember: ordered by sequence)
                self.fiscal_id_type = self.env['res.partner.idtype'].search(
                    [('on_company', '=', True)], limit=1).id
                self.fiscal_id = None  # Reset ID value
        # CASE: Current ID Type is not applicable on contact
        if not self.is_company:
            if not self.fiscal_id_type.on_contact:
                # Get the first valid ID type (remember: ordered by sequence)
                self.fiscal_id_type = self.env['res.partner.idtype'].search(
                    [('on_contact', '=', True)], limit=1).id
                self.fiscal_id = None  # Reset ID value
        # If everything is fine, call subclasses
        if self.fiscal_id_type and self.fiscal_id:
            # Function for String Operations
            res = self._validateandformatid()
            if res['output_type'] and res['output_id']:
                self.fiscal_id_type = res['output_type']
                self.fiscal_id = res['output_id']
            # Procedure for Copying
            self._copyid()

    def _validateandformatid(self):
        """
        Hook method to be inherited for custom validation methods.
        :param input_type: the value of the field fiscal_id_type (id); passed
        on by onchange decorator
        :param input_id: the value of the field fiscal_id (string); passed on
        by onchange decorator
        :return: must return a dict with validated and formatted values

        Hint:
        you might not alter the output_type unless you might want to build
        some kind of fiscal_id_type recognition
        based on the input pattern into your hook method. CO###.###.###-#
        CO-VAT (NIT) for example.

        Find below a suggested basic outline.

        """
        return {'output_type': self.fiscal_id_type, 'output_id': self.fiscal_id}
        """
        f_type     = self.fiscal_id_type
        f_id       = self.fiscal_id
        is_company = self.is_company

        def default():
            return {'output_type': f_type, 'output_id': f_id}

        return {
            # Define your cases
            # The index to match is self.fiscal_id_type.code
            # Note: You can change this index below.
            # Example assignation using two functions
            # {'output_type': func_type1(), 'output_id': funct_id1()}
            'CODE1': { "put your assignation here" },
            'CODE2': { "put your assignation here" },
        }.get(self.fiscal_id_type.code, default())
        """

    def _copyid(self):
        """
        Hook Method to be inherited for custom copy methods based on the
        document type (id)
        Example Use Case: Copy some local VAT number into the VAT-Field in
        it's international format for compatibility.

        :return: It is a Procedure and therefore has no return value.

        Find below a suggested basic outline.

        """
        """
        f_type     = self.fiscal_id_type
        f_id       = self.fiscal_id
        is_company = self.is_company

        def stringop_def(s): return s

        def stringop_1(s): return re.match('\\d|\\w*', s)

        # Define other Docstringoperatios if necessary

        def default():
            self.vat_subjected = True
            # self.vat is a Boolean until base_vat is installed.
            # self.vat = self.country_id.code + sringop_def(f_id)

        {
            # Some examples to consider...
            # seld.vat_subjected: True,
            # self.vat: self.country_id.code + stringop_1(f_id)
            'CODE1': { "put your statments here" },
            'CODE2': { "put your statments here" },
        }.get(self.fiscal_id_type.code, default())
        """
