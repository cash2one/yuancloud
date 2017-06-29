# -*- encoding: utf-8 -*-

from yuancloud.osv import fields, osv


class res_partner(osv.osv):
    
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'state_id': fields.many2one("res.country.state", 'Ubication', domain="[('country_id','=',country_id),('type','=','normal')]"),
        }
  

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: