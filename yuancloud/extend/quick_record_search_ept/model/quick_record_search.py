from yuancloud import models, fields, api, _

class quick_record_search(models.Model):
    _name="quick.search.record"
    
    name=fields.Char(string="Name")
    default=fields.Boolean(string="Default")
    search_type= fields.Selection([('exact','Exact'), ('matching','Matching')], string='Search Type',default='exact')
    window_type= fields.Selection([('new','New'), ('current','Current')], string='Window Type',default='new')
    model_id=fields.Many2one('ir.model',"Model Name")
    model_model=fields.Char(string="Model",related="model_id.model",readonly=True)
    view_id=fields.Many2one('ir.ui.view',"Form View")
    tree_view_id=fields.Many2one('ir.ui.view',"Tree View")
    field_id=fields.Many2one('ir.model.fields',"Fields")
    
    _sql_constraints = [
        ('default_search_uniq', 'unique(default)', 'Default must be unique for search preference!'),
    ]
    _defaults={'search_type':'exact','window_type':'new'
               }
    @api.multi       
    def _check_default(self):
        default_ids = self.search([('default','=',True)])
        default_ids=[x.id for x in default_ids]
        if len(default_ids) > 1:            
            return False
        return True
    
    def _check_search_type(self,cr,uid,ids,context=None):
        for obj in self.browse(cr,uid,ids,context=context):
            if obj.field_id.ttype == 'integer':
                if obj.search_type == 'matching':
                    return False
                else:
                    return True
            else:
                return True
        
    _constraints = [
        (_check_default, 'You cannot set multiple default search preference.', ['default']),
        (_check_search_type, 'You cannot set matching for integer search field.', ['search_type']),
        ]
        
    """This method checks that whether search preference is set by user ???"""
    @api.model
    def check_search_record_preference(self,uid):
        current_user = self.env['res.users'].browse(uid)
        if current_user.quick_search_record_id: 
            if current_user.quick_search_record_id or current_user.quick_search_record_id.default:
                return 'True'
        else:   
            default_ids = self.search([('default','=',True)])
            if not default_ids :
                return 'False'
            return 'True'            
           
    
    """This method provides quick record search functionality"""
    @api.model
    def quick_record_search_def(self,record_no):
        value={}
        users_obj=self.env['res.users']
        current_user = users_obj.browse(self._uid)       
        
        if current_user :
            if current_user.quick_search_record_id :
                name=current_user.quick_search_record_id.name
                model = current_user.quick_search_record_id.model_id.model
                view_id = current_user.quick_search_record_id.view_id.id
                tree_view_id = current_user.quick_search_record_id.tree_view_id.id or None
                field = current_user.quick_search_record_id.field_id.name
                search_type=current_user.quick_search_record_id.search_type
                window_type=current_user.quick_search_record_id.window_type
                if current_user.quick_search_record_id.field_id.ttype == 'integer':
                    if record_no.isdigit():
                        value=self.get_action(name,record_no, model, view_id,tree_view_id, field,search_type,window_type)
                    else:
                        value.update({'msg_id':'There is no matching record found for %s'%(name)})
                else:
                    value=self.get_action(name,record_no, model, view_id,tree_view_id, field,search_type,window_type)
                print value
                return value
            else:
                default_ids = self.search([('default','=',True)])
                if default_ids :
                    name=default_ids[0].name
                    model = default_ids[0].model_id.model                    
                    view_id = default_ids[0].view_id.id
                    tree_view_id = default_ids[0].tree_view_id.id or None
                    field = default_ids[0].field_id.name
                    search_type=default_ids[0].search_type
                    window_type=default_ids[0].window_type
                    if default_ids[0].field_id.ttype == 'integer':
                        if record_no.isdigit():
                            value=self.get_action(name,record_no, model, view_id,tree_view_id, field,search_type,window_type)
                        else:
                            value.update({'msg_id':'There is no matching record found for %s'%(name)})
                    else:
                        value=self.get_action(name,record_no, model, view_id,tree_view_id, field,search_type,window_type)                        
                    return value
                    
    def get_action(self,name,record_no, model, view_id,tree_view_id, field,search_type,window_type):
        print search_type
        views=[]
        vals={}
        res_id=None
        domain=None
        if search_type == "exact":
            record_ids = self.env[model].search( [( field, '=', record_no )] )
        else:
            record_ids = self.env[model].search( [( field, 'ilike', record_no )] )
        context=dict(self._context or {})        
        if record_ids:
            context.update({'active_id':[x.id for x in record_ids][0],'active_ids' :[x.id for x in record_ids]})
            record_ids_list=[x.id for x in record_ids]
            view_mode = 'form'
            if tree_view_id :
                views=[(tree_view_id, 'list'), (view_id, 'form')] 
                view_mode = 'tree,form'
                domain=[('id', 'in', record_ids_list)]           
            else:
                views=[(view_id, 'form')]                
                res_id=record_ids_list[0]
                
            vals={
                   'type': 'ir.actions.act_window',
                   'name': name,
                   'view_type': 'form',                       
                        'view_mode': view_mode,
                        'res_model': model,                       
                        'target': window_type,                     
                        'views': views,
                        'flags' :{                            
                                  'pager': True,
                                  'action_buttons':True,
                                  'sidebar':True,
                                  }             
                    }
            if domain:
                vals.update({'domain':domain})
            if res_id:
                vals.update({'res_id':res_id})
            return vals
        else:
            vals.update({'msg_id':'There is no matching record found for %s'%(name)})
            return vals     
            
        
