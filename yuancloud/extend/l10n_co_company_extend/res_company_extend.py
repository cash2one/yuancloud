from yuancloud import models, fields, api, _

# HERENCIA DE OBEJO

class ResCompanyExtend(models.Model):
		_inherit = 'res.company'
		_columns = {
            'nit': fields.Char('NIT', size=32, help='Numero de identificacion triburaria.', required=True),
        }
()


		


