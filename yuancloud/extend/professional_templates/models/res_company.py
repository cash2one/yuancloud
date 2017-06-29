# -*- coding: utf-8 -*-

from yuancloud import models, fields, api

class default_report_sett(models.Model):
	_inherit=["res.company"]

        @api.model
        def _default_so_template(self):
            def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.SO\_%\_document' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('sale.report_saleorder_document')

        @api.model
        def _default_po_template(self):
            def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.PO\_%\_document' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('purchase.report_purchaseorder_document')

        @api.model
        def _default_rfq_template(self):
            def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.RFQ\_%\_document' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('purchase.report_purchasequotation_document')

        @api.model
        def _default_dn_template(self):
            def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.DN\_%\_document' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('stock.report_delivery_document')

        @api.model
        def _default_pk_template(self):
            def_tpl = self.env['ir.ui.view'].search([('key', 'like', 'professional_templates.PICK\_%\_document' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('stock.report_picking')

        odd = fields.Char('Odd parity Color', size=7, required=True, default="#F2F2F2", help="The background color for Odd order lines in the order")  
        even = fields.Char('Even parity Color', size=7, required=True, default="#FFFFFF", help="The background color for Even order lines in the order" )   
        theme_color = fields.Char('Theme Color', size=7, required=True, default="#F07C4D", help="The Main Theme color of the order. Normally this should be one of your official company colors")    
        text_color = fields.Char('Text Color', size=7, required=True, default="#6B6C6C", help="The Text color of the order. Normally this should be one of your official company colors or default HTML text color") 
        name_color = fields.Char('Company Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Company Name. Normally this should be one of your official company colors or default HTML text color") 
        cust_color = fields.Char('Customer Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Customer Name. Normally this should be one of your official company colors or default HTML text color") 
        theme_txt_color = fields.Char('Theme Text Color', size=7, required=True, default="#FFFFFF", help="The Text color of the areas bearing the theme color. Normally this should NOT be the same color as the theme color. Otherwise the text will not be visible")

	invoice_logo = fields.Binary("Logo", attachment=True,
               help="This the image used as logo for any report, if non is uploaded, the company logo will be used by default")	
	template_so = fields.Many2one('ir.ui.view', 'Default Sales Order Template', default=_default_so_template, 
			domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.SO\_%\_document' )]", required=True)

	template_po = fields.Many2one('ir.ui.view', 'Default Purchase Order Template', default=_default_po_template, 
			domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PO\_%\_document' )]", required=True)

	template_rfq = fields.Many2one('ir.ui.view', 'Default RFQ Template', default=_default_rfq_template, 
			domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.RFQ\_%\_document' )]", required=True)

	template_dn = fields.Many2one('ir.ui.view', 'Default Delivery Slip Template', default=_default_dn_template, 
			domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.DN\_%\_document' )]", required=True)

	template_pk = fields.Many2one('ir.ui.view', 'Default Picking Template', default=_default_pk_template, 
			domain="[('type', '=', 'qweb'), ('key', 'like', 'professional_templates.PICK\_%\_document' )]", required=True)


