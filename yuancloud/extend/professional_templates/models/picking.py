# -*- coding: utf-8 -*-
from yuancloud import models, fields, api

class customized_picking_slip(models.Model):
	_inherit=["stock.picking"]

	@api.model
	def _default_picking_template(self):
	    company_obj = self.env['res.company']
	    company = self.env['res.users'].browse([self.env.user.id]).company_id
	    if not company.template_pk:
		def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.PICK_%' ), ('type', '=', 'qweb')], order='id asc', limit=1)
                company.write({'template_pk': def_tpl.id})
	    return company.template_pk or self.env.ref('stock.report_picking')
	
 	pk_logo = fields.Binary("Logo", attachment=True,
             help="This field holds the image used as logo for the Picking, if non is uploaded, the default logo set in the company settings will be used")
	templ_pk_id = fields.Many2one('ir.ui.view', 'Picking Slip Template', default=_default_picking_template,required=True, 
		domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PICK\_%\_document' )]")
