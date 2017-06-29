from yuancloud import models, fields, api, _


class res_users(models.Model):
    _inherit="res.users"
    
    quick_search_record_id=fields.Many2one('quick.search.record',"Quick Search Record")
    
    
    